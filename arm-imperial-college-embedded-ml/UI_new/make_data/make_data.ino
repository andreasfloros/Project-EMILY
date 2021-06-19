// import the PDM (microphone)
#include <PDM.h>

constexpr float expected_duration = 1.0;
constexpr int sample_rate = 16000;

static constexpr unsigned int NUM_OF_SAMPLES_PER_TRACK = expected_duration * sample_rate;


// define the required buffers
// storageBuffer: this is where we store the raw microphone data, this is where we read into from the internal PDM buffer, which is of equal size
// sampleBuffer: we keep an entire audio_track worth of data in this buffer, so the length is NUM_OF_SAMPLES_PER_TRACK, as defined above
static const unsigned int SAMPLE_BUFFER_SIZE = NUM_OF_SAMPLES_PER_TRACK;
static const int PDM_BUFFER_SIZE = 512;
static const int PDM_BUFFER_SIZE_BYTES = PDM_BUFFER_SIZE * sizeof(short); // each sample is 2 bytes
static const int STORAGE_BUFFER_SIZE = PDM_BUFFER_SIZE; // equal to PDM buffer size
short sampleBuffer [SAMPLE_BUFFER_SIZE] = {0};
short storageBuffer [STORAGE_BUFFER_SIZE] = {0};

// determined by comparing the mean square value of part of the
// sampleBuffer to a predefined, experimentally-found threshold 
volatile float meanSquare = 0.0;
volatile bool audioIsLoud = false;
static const float THRESHOLD = 40.0;
bool corruptedBuffer = false;
int corruptionCounter = 0;
volatile int samplesRead;

// Callback function to process the data from the PDM microphone.
// Part of an Interrupt Service Routine (ISR)
void microphone_callback() {
  // Query the number of available bytes
  int bytesAvailable = PDM.available();
  
  // 16-bit, 2 bytes per sample
  samplesRead = bytesAvailable / sizeof(sampleBuffer[0]);

  // Read into the storage buffer  
  PDM.read(storageBuffer, samplesRead * sizeof(sampleBuffer[0]));
}

// setup
void setup() {
  Serial.begin(9600);
  while (!Serial);

  PDM.setBufferSize(PDM_BUFFER_SIZE_BYTES);
  
  // Configure the data receive callback
  PDM.onReceive(microphone_callback);

  // 0 gain works best for audio quality
  PDM.setGain(10);

  // Initialize PDM with:
  // - one channel (mono mode)
  // - a 16 kHz sample rate for the Arduino Nano 33 BLE Sense
  if (!PDM.begin(1, sample_rate)) {
    Serial.println("Failed to start PDM!");
    while (1);
  }
  
  delay(2000);
}



// loop
void loop() {
  // Wait for samples to be read
  if (samplesRead) {

    // Serial.println(samplesRead);
    // shift values from samplesRead to SAMPLE_BUFFER_SIZE to the range 0 to SAMPLE_BUFFER_SIZE - samplesRead
    memmove(&sampleBuffer[0], &sampleBuffer[samplesRead], (SAMPLE_BUFFER_SIZE - samplesRead) * sizeof(sampleBuffer[0]));
    // write the samplesRead from the storageBuffer to the end of the sampleBuffer
    memmove(&sampleBuffer[SAMPLE_BUFFER_SIZE - samplesRead], &storageBuffer[0], samplesRead * sizeof(sampleBuffer[0]));

    if (corruptedBuffer) {
      corruptionCounter -= samplesRead;
      if (corruptionCounter <= 0) {
        corruptedBuffer = false;
      }
    }


    if (!corruptedBuffer) {
      meanSquare = 0.0;
      for (unsigned short i = 0; i < SAMPLE_BUFFER_SIZE /4; i++) {
        meanSquare += (sampleBuffer[i] * sampleBuffer[i]) / ((float) SAMPLE_BUFFER_SIZE);
      }
      audioIsLoud = (meanSquare > THRESHOLD);  
    }


    if (audioIsLoud && !corruptedBuffer) {
      Serial.write((uint8_t*) sampleBuffer, SAMPLE_BUFFER_SIZE * sizeof(sampleBuffer[0]));
      corruptedBuffer = true;
      corruptionCounter = SAMPLE_BUFFER_SIZE;
    }
    
    // Clear the read count
    samplesRead = 0;
  }
  
}
