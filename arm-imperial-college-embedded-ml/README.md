# Imperial College Embedded ML

## Repository breakdown:
---
### UI: 
Folder containing what would be considered our "end product". Contains the following files:
1. **main.py:** Main UI file. Everything is called from here.
2. **training_streamlined.py:** Contains the core backend function, preprocess_data_and_train_model, which is called when the user presses "Train". This achieves the following:
      1. Split dataset into training, validation, and testing datasets
      2. Preprocess data: Extract features and labels from the dataset splits
      3. Compile and train a model
     
      Note that points 2 and 3 from the above are streamlined using tf.data.dataset. This means that processing and training does not happen for the entire dataset at once, but only for one batch at time. So each time we fetch one batch (size is user-defined), we process it, obtaining a feature map and label for each of the samples in the batch and then train the network on it. While this makes the process slower, it is much more memory efficient.
3. **dataset_functions.py:** Contains everything related to loading the audio dataset.
4. **processing_functions.py:** Contains everything related to preprocessing the audio dataset.
5. **model_functions.py:** Contains everything related to training, converting, and saving the model.
6. **arduino.py:** Contains everything related to deploying the arduino script as well as the model chosen for inference.
7. **imports.py:** Contains all imports currently used.
8. **arduino_files (folder):** Contains the .ino script and the .h model file to be uploaded to the arduino.
9. **Images & Original Images (folders):** Contain images used as icons within the UI.

#### Requirements:
pip install the following:
1. tensorflow
2. librosa
3. matplotlib
4. tensorflow_model_optimization
5. hexdump
---

### UI_old: 
Practically the same functionality-wise as the UI folder, but doesn't include streamlining, so all the processing happens at once and not in batches during training. Because of this the program may crash from RAM in processing configurations that produce large feature maps, but is much faster otherwise. Note that this has the same installation requirements as the UI folder. Contains the following files:
1. **main.py:** Main UI file. Everything is called from here.
2. **processing.py:** Contains everything related to loading and preprocessing the audio dataset.
3. **training.py:** Contains everything related to training, converting, and saving the model.
4. **arduino.py:** Contains everything related to deploying the arduino script as well as the model chosen for inference.
5. **imports.py:** Contains all imports currently used.
6. **arduino_files (folder):** Contains the .ino script and the .h model file to be uploaded to the arduino.
7. **Images & Original Images (folders):** Contain images used as icons within the UI.

---
### arduino_inference_script: 
Contains the following files
1. **arduino_inference_script.ino:** Early script for simple pipeline for the arduino (currently preprocessing is averaging of the time series). Not tested thoroughly.
2. **model.h:** Contains the model chosen for inference. Should be .h file.

---

### arduino_microphone: 
Contains the following files/folders
1. **arduino_microphone.ino:** Variation of PDMSerialPlotter Arduino example. Used to send serial data to python side to assess microphone audio quality and record audio data.
2. **wav_from_audio.py:** Python script to receive data currently being recorded by Arduino and create a .wav file.
3. **generated wav files (folder):** contains several .wav files generated in the past.

---

### jupyter_notebooks:
Contains the following notebooks
1. **audio_classifier_pipeline.ipynb:** Jupyter notebook containing the entire pipeline for building an audio classifier model. This consists of the following sections:
      1. Download and untar dataset directly to colab
      2. Preprocess dataset
      3. Build, train, and evaluate model
      4. Save model and convert to desired formats
      5. Extra functions (not required for the pipeline)
2. **pipeline_with_interface:** Almost identical to audio_classifier_pipeline, but with the addition of some user interface which prompts the user to enter some essential parameters and simply run all the cells.
3. **autokeras:** Jupyter notebook containing an autokeras model implementation. Preparation and preprocessing of data referenced to audio_classifier_pipeline. Still requires investigation on possible-to-set hyperparameters for refining the model search space.

  Further information on all of the above can be found in the respective sections within the Jupyter notebook files. For some reason, Colab does not recognize this repo, and thus doesn't allow me to save it directly with the convenient "open in colab" button, so please open it by going to [Colab](https://colab.research.google.com/) and copy pasting the Github link of the notebook.

---

## Authors: 
- Andreas Floros
- Bharat Kumar
- Hussain Kurabadwala
- Vasileios Manginas
- Stacey Wu
