# Running the code on the micro-controller

## **Step 1**

Run the "Download.py" Python Script. This script downloads a zip file containing the Arduino CLI which will be used to compile and upload the code to the microcontroller.

## **Step 2**

Go to your main directory("C:\" for example) and create a new folder called "arduino-cli". Move the "Arduino-cli.exe" executable file that has now appeared in the folder next to your sketch to the "arduino-cli" folder.

## Step 3

Type "Edit the system environment variables" in your search bar and open it. Click on Environment Varirables, and double-click "path" under "User Variables for  ..." (the top box). Then click on "New" and type the following "C:\arduino-cli". Then click "OK" everywhere and exit.

## Step 4

Check if everything is working correctly by opening a new CMD instance (make sure to close the old ones if you had opened them previously) and type "arduino-cli -h". This should list a list of different commands available. If you face an error like "command not recognized", then make sure you have followed previous steps correctly.

## Step 5

Place the .ino extension script that you want to upload in the same folder as the other python files. Finally, run the "RunBatchFiles.py" Python script and follow the instructions in CMD. This script will then compile and upload the .ino file to your Arduino microcontroller.
