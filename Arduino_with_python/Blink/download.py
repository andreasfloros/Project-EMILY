from urllib.request import urlretrieve
import zipfile
import requests

download_64bit_windows = "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Windows_64bit.zip"


#Download the appropriate file from the URL
r = requests.get(download_64bit_windows)
urlretrieve(download_64bit_windows, "ArduinoCLI.zip")

#Extract contents of the zip file
with zipfile.ZipFile("ArduinoCLI.zip","r") as zip_ref:
    zip_ref.extractall()