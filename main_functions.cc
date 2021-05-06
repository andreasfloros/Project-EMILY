/* amended to compile */

#include "tensorflow/lite/micro/examples/micro_speech/main_functions.h"


// micro-speech library 
#include "tensorflow/lite/micro/examples/micro_speech/micro_features/model.h"
#include "tensorflow/lite/micro/examples/micro_speech/micro_features/micro_model_settings.h"
#include "data.h"

// system setting
#include "tensorflow/lite/micro/micro_error_reporter.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/schema/schema_generated.h"

// const parameters : to be filled later
// const int NUM_CATEGORIES = 2;

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

// Create an area of memory to use for input, output, and intermediate arrays.
// The size of this will depend on the model you're using, and may need to be
// determined by experimentation.
constexpr int tensorArenaSize = 10 * 1024;
uint8_t tensorArena[tensorArenaSize];

void setup(){
    tflModel = tflite::GetModel(g_model);

    // Create an interpreter to run the model
    static tflite::MicroInterpreter static_interpreter(tflModel, tflOpsResolver, tensorArena, tensorArenaSize, &tflErrorReporter);
    tflInterpreter = &static_interpreter;

    // Allocate memory for the model's input and output tensors
    tflInterpreter->AllocateTensors();

    // Get pointers for the model's input and output tensors
    tflInputTensor = tflInterpreter->input(0);
    tflOutputTensor = tflInterpreter->output(0);
}

void loop(){
    // Collect audio data
    // Sandeep: wait for threshold trigger, but keep N samples before threshold occurs

    // Preprocessing
    for (int i = 0; i < kFeatureElementCount; i++){
        tflInputTensor->data.f[i] = data[i];
    }


    // Run inference 
    TfLiteStatus invokeStatus = tflInterpreter->Invoke();

    if (invokeStatus != kTfLiteOk) {
        TF_LITE_REPORT_ERROR(&tflErrorReporter,"Invoke failed!");
        while (1);
        return;
    }

    for (int i = 0; i < kCategoryCount; i++) {
        TF_LITE_REPORT_ERROR(&tflErrorReporter, "Heard %s: %f", kCategoryLabels[i],
                            tflOutputTensor->data.f64[i]);
    }
}