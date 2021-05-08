# ARM-ML-Embedded

### Authors: 
- Andreas Floros
- Bharat Kumar
- Hussain Kurabadwala
- Vasileios Manginas
- Stacey Wu


### main_functions.cc
An implementation of inference for Arduino IDE. 

To run, copy the code in Arduino ide and replace the **data[i]** with preprocessed audio data from input. 

### what the files do
Audio_classifier_pipeline -- the full pipeline with choice of preprocessing. Trash accuracy tho

bharat1 -- the full pipeline with mfcc. good accuracy tho but mfcc is gross.

bharat5 -- not entirely working pipeline because the input_shape is being problematic with only dense layers??. idk whats going on with this 
