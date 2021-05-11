@ECHO OFF
ECHO This script will run and upload the .ino sketch to your microcontroller!

@REM Note the com port and fqbn from the below command
arduino-cli board list

@REM We take a bunch of inputs from the user because these details change based on project and microcontroller used

set /P _fbqn = Enter FBQN from above as "arduino:mbed:nano33ble" for example:
echo.
set /P _com = Enter COM port Number from above as "COM3" for example:
echo.
set /P _core = Enter core from above as "arduino:mbed" for example:
echo.
set /P _inoName = Enter .ino file name without the .ino extension(Case Sensitive):
echo.
@REM download some dependencies
arduino-cli core install %_core%
echo.

arduino-cli compile --fqbn %_fbqn% %_inoName%
echo.

arduino-cli upload -p %_com% --fqbn %_fbqn% %_inoName%

PAUSE