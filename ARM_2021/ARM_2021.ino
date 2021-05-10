// For reading the audio data
#include <PDM.h>
// For preprocessing
#include <fix_fft.h>

// ML related
#include <TensorFlowLite.h>
#include <tensorflow/lite/micro/all_ops_resolver.h>
#include <tensorflow/lite/micro/micro_error_reporter.h>
#include <tensorflow/lite/micro/micro_interpreter.h>
#include <tensorflow/lite/schema/schema_generated.h>
#include <tensorflow/lite/version.h>
#include <model.cc>

// Parameters for reading the audio data
static const unsigned short BUFFER_SIZE = 32768;
static const unsigned short SAMPLE_BUFFER_SIZE = BUFFER_SIZE / 2;
static const unsigned short SAMPLE_RATE = 16000;
static const char CHANNELS = 1;
// buffer to read samples into, each sample is 16-bits
static short sampleBuffer [SAMPLE_BUFFER_SIZE];
volatile unsigned short samplesRead;

// Parameters for DSP
static char fft [SAMPLE_BUFFER_SIZE];

// Parameters for ML
// global variables used for TensorFlow Lite (Micro)
tflite::MicroErrorReporter tflErrorReporter;

// pull in all the TFLM ops, you can remove this line and
// only pull in the TFLM ops you need, if would like to reduce
// the compiled size of the sketch.
tflite::AllOpsResolver tflOpsResolver;

const tflite::Model* tflModel = nullptr;
tflite::MicroInterpreter* tflInterpreter = nullptr;
TfLiteTensor* tflInputTensor = nullptr;
TfLiteTensor* tflOutputTensor = nullptr;

// Create a static memory buffer for TFLM, the size may need to
// be adjusted based on the model you are using
constexpr unsigned short tensorArenaSize = 8 * 1024;
byte tensorArena[tensorArenaSize];

// array to map response index to a name
const char* RESPONSES[] = {
  "yes",
  "no"
};

unsigned short NUM_RESPONSES = (sizeof(RESPONSES) / sizeof(RESPONSES[0]));


void setup() {
  Serial.begin(9600);
  while (!Serial);
  PDM.onReceive(updateSampleBuffer);
  PDM.setBufferSize(BUFFER_SIZE);
  // initialize PDM with:
  // - one channel (mono mode)
  // - a 16 kHz sample rate
  if (!PDM.begin(CHANNELS, SAMPLE_RATE)) {
    Serial.println("Failed to start PDM!");
    while (1);
  }
  // get the TFL representation of the model byte array
  tflModel = tflite::GetModel(model);
  if (tflModel->version() != TFLITE_SCHEMA_VERSION) {
    Serial.println("Model schema mismatch!");
    while (1);
  }

  // Create an interpreter to run the model
  tflInterpreter = new tflite::MicroInterpreter(tflModel, tflOpsResolver, tensorArena, tensorArenaSize, &tflErrorReporter);

  // Allocate memory for the model's input and output tensors
  tflInterpreter->AllocateTensors();

  // Get pointers for the model's input and output tensors
  tflInputTensor = tflInterpreter->input(0);
  tflOutputTensor = tflInterpreter->output(0);
  delay(1024);
}

void loop() {
  // Wait for new samples
  if (samplesRead) {
    preprocessSampleBuffer(); // features (magnitude of FFT) is in realPart
    Serial.println("PREPROCESS DONE");
    featuresToInput(); // Store features to input tensor
    Serial.println("F TO I DONE");
    runInference(); // Run inference
    Serial.println("INFERENCE DONE");
    samplesRead = 0; // no new samples left
  }
}

void updateSampleBuffer() {
  // Query the number of available bytes
  unsigned short bytesAvailable = PDM.available();

  // 16-bit, 2 bytes per sample
  samplesRead = bytesAvailable / 2;
  for (unsigned short i = 0; i < SAMPLE_BUFFER_SIZE - samplesRead; i++){
    sampleBuffer[i] = sampleBuffer[i + samplesRead];
  }
  // Read into the sample buffer
  PDM.read(&(sampleBuffer[SAMPLE_BUFFER_SIZE - samplesRead]), bytesAvailable);
}

void preprocessSampleBuffer() {
 // Setup answer arrays
  for (unsigned short i = 0; i < SAMPLE_BUFFER_SIZE; i++){
    fft[i] = char(sampleBuffer[i]);
  }
  // Compute the FFT
  Serial.println("ENTERING FFT COMPUTE");
  int scale = fix_fftr(fft, 14, 0);
}

void featuresToInput(){
  for (unsigned short i = 0; i < SAMPLE_BUFFER_SIZE / 2; i+= 16){
    float avg = 0;
    for (unsigned short j = 0; j < 16; j++){
      avg += fft[i+j];
    }
    avg = avg / 16;
    tflInputTensor->data.f[i / 16] = avg;
  }
}

void runInference(){
  // Run inferencing
  TfLiteStatus invokeStatus = tflInterpreter->Invoke();
  if (invokeStatus != kTfLiteOk) {
    Serial.println("Invoke failed!");
    while (1);
    return;
  }
  // Loop through the output tensor values from the model
  unsigned short argmax = 0;
  float mx = 0;
  for (unsigned short i = 0; i < 36; i++) {
    Serial.print(i);
    Serial.print(": ");
    Serial.println(tflOutputTensor->data.f[i]);
    if (tflOutputTensor->data.f[i] > mx){
      mx = tflOutputTensor->data.f[i];
      argmax = i;
    }
  }
//  Serial.print("yes");
//  Serial.print(": ");
//  Serial.println(tflOutputTensor->data.f[18]);
//  Serial.print("no");
//  Serial.print(": ");
//  Serial.println(tflOutputTensor->data.f[31]);
}
