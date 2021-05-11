import subprocess

#The following line of code runs the batch file to download required arduino libraries
subprocess.call([r'C:/Bharat/Imperial College London/Year 3/GP/Python/Blink/Dependencies.bat'])

#The following line of code runs the batch file to compile and upload codee to the arduino board
subprocess.call([r'C:/Bharat/Imperial College London/Year 3/GP/Python/Blink/Compile&Upload.bat'])
