# Project EMILY

An Embedded Machine Learning Ecosystem (EMLE hence EMILY) with the aim of simplifying the deployment of audio classifier to microcontrollers.

Application tested and is working on Windows 10 and on MacOS (with limited support).

Boards tested: Arduino Nano 33 BLE Sense.

We provide the users with an intuive, easy to use User Interface (UI) where they can select their datasets, choose their processing methods and even configure some of the machine learning parameters. We also allow the users to directly upload their models to Arduino, without the use of the Arduino IDE. Our application is an all in one package.

## Authors: 
- Andreas Floros
- Bharat Kumar
- Hussain Kurabadwala
- Vasileios Manginas
- Stacey Wu

## Repository breakdown:

### UI: 
This folder contains what would be considered our "end product". Made up of the following:

1. **main.py:** Main UI frontend file. Everything from the backend is called from here.

3. **imports.py:** Contains all imports currently used.

4. **scripts (folder):** Contains all scripts that form the backend, and is divided further into four folders which represent the four blocks in the pipeline:
      1. **dataset:** Contains everything related to accessing and loading the audio dataset. Achieves the following:
            1. Choose the source of the dataset. Options: load from local directory, download from URL, create from within our UI
            2. Set important dataset parameters, such as the expected track duration and the sampling rate

      3. **processing:** Contains everything related to preprocessing the audio dataset. Achieves the following:
            1. Choose the signal processing method. Options: Averaging, Short Time Fourier Transform, Windowed Root Mean Square
            2. Configure processing by tuning algorithm parameters
            3. Option to streamline the input pipeline
            
      5. **training:** Contains everything related to training, converting, and saving the model. Achieves the following:
            1. Set various ML-related parameters
            2. Choose between Convolutional and Dense models.
            2. Real-time plotting of model performance
            3. Model quantization and quantization-aware
            5. Convert model to form readable by the microcontroller and save it in user-selected destination

      7. **arduino:** Contains everything related to deploying the arduino script as well as the model chosen for inference. Achieves the following:
            1. Compile and upload ready-made Arduino script for preprocessing and inference. 
            2. Pass dataset and processing parameters to Arduino through the model file.
            3. Automated deployment to microcontroller through  Arduino-CLI.
            4. Live feedback from the CLI through a custom CMD.

8. **arduino_files (folder):** Contains the .ino script and the .h model file to be uploaded to the arduino.
9. **Images (folder):** Contains images used as icons within the UI.

#### Requirements:
pip install the following:
1. tensorflow
2. librosa
3. matplotlib
4. tensorflow_model_optimization
5. hexdump

---
