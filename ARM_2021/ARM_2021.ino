// Haven't tested this yet since we don't have the model.h ready
// For now: Need fully dense model with input dimension being a power of two
// Preprocess with FFT (add some avergaing if you want too)

// For reading the audio data
#include <PDM.h>
// For preprocessing
#include <arduinoFFT.h>
// ML related
#include <TensorFlowLite.h>
#include <tensorflow/lite/micro/all_ops_resolver.h>
#include <tensorflow/lite/micro/micro_error_reporter.h>
#include <tensorflow/lite/micro/micro_interpreter.h>
#include <tensorflow/lite/schema/schema_generated.h>
#include <tensorflow/lite/version.h>
#include "model.h"

// Parameters for reading the audio data
const int BUFFER_SIZE = 512;
static const int SAMPLE_RATE = 16000;
static const char CHANNELS = 1;
// buffer to read samples into, each sample is 16-bits
int sampleBuffer [BUFFER_SIZE];
volatile int samplesRead;

// Parameters for DSP
double realPart [BUFFER_SIZE];
double imagPart [BUFFER_SIZE];

// Parameters for ML
// global variables used for TensorFlow Lite (Micro)
tflite::MicroErrorReporter tflErrorReporter;

// pull in all the TFLM ops, you can remove this line and
// only pull in the TFLM ops you need, if would like to reduce
// the compiled size of the sketch.
tflite::ops::micro::AllOpsResolver tflOpsResolver;

const tflite::Model* tflModel = nullptr;
tflite::MicroInterpreter* tflInterpreter = nullptr;
TfLiteTensor* tflInputTensor = nullptr;
TfLiteTensor* tflOutputTensor = nullptr;

// Create a static memory buffer for TFLM, the size may need to
// be adjusted based on the model you are using
constexpr int tensorArenaSize = 8 * 1024; // Not sure what this should be changed to
byte tensorArena[tensorArenaSize];

// array to map response index to a name
const char* RESPONSES[] = {
  "yes",
  "no"
};

#define NUM_RESPONSES (sizeof(RESPONSES) / sizeof(RESPONSES[0]))


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
  delay(1000);
}

void loop() {
  // Wait for new samples
  if (samplesRead) {
    preprocessSampleBuffer(); // features (magnitude of FFT) is in realPart
    featuresToInput(); // Store features to input tensor
    runInference(); // Run inference
    samplesRead = 0; // no new samples left
  }
  delay(1000)
}

void updateSampleBuffer() {
  // Query the number of available bytes
  int bytesAvailable = PDM.available();

  // 16-bit, 2 bytes per sample
  samplesRead = bytesAvailable / 2;
  for (int i = 0; i < BUFFER_SIZE - samplesRead; i++){
    sampleBuffer[i] = sampleBuffer[i + samplesRead];
  }
  // Read into the sample buffer
  PDM.read(&(sampleBuffer[BUFFER_SIZE - samplesRead]), bytesAvailable);
}

void preprocessSampleBuffer() {
  // Setup answer arrays
  for (int i = 0; i < BUFFER_SIZE; i++){
    realPart[i] = int8_t(sampleBuffer[i]);
    imagPart[i] = 0.0;
  }
  // Compute the FFT
  FFT.Compute(realPart, imagPart, BUFFER_SIZE, FFT_FORWARD);
  // Compute the magnitude (stored in realPart)
  FFT.ComplexToMagnitude(realPart, imagPart, BUFFER_SIZE);
}

void featuresToInput(){
  for (int i = 0; i < BUFFER_SIZE; i++){
    tflInputTensor->data.f[i] = realPart[i];
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
  for (int i = 0; i < NUM_RESPONSES; i++) {
    Serial.print(RESPONSES[i]);
    Serial.print(": ");
    Serial.println(tflOutputTensor->data.f[i]);
  }
  Serial.println();
}
