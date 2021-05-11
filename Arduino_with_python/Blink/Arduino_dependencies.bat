@REM Add dependencies below in the same way as the tensorflowLite example.
@REM Use the exact name mentioned as the in the arduino library manager.
@REM Before adding below, run it as "arduino-cli lib search "Arduino_TensorFlowLite"" in cmd.
@REM This is to check if Arduino CLI is able to find the exact library.

@ECHO OFF
ECHO This script will download the Arduino dependencies!

arduino-cli lib download "Arduino_TensorFlowLite"
