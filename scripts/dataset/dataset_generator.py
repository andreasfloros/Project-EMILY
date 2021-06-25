# # Upload the arduino_microphone.ino file to the Arduino and then run this script to record an audio track
# and subsequently save to a .wav file.
#
# The code below achieves the following:
#   1. Creates a bytearray from the data in the serial buffer (as much of that data as we specify)
#   2. Multiplies everything in the bytearray by an amplification factor since original audio is too quiet
#   3. Writes to a .wav file

# Imports: (install using pip3 if not already present)

from typing import Text
from numpy.lib.npyio import save
from imports import *
from scripts.arduino.arduino import *

# Specify parameters used

SAMPLE_WIDTH = 2
NUM_CHANNELS = 1
AMPLIFICATION_FACTOR = 10

def read_port(app):
    platform_name = check_platform()

    fqbn, COM_PORT, core = Get_Details(platform_name, app)
    print("COM PORT is: ", COM_PORT)
    ser = serial.Serial(COM_PORT, 9600, timeout=None)
    return ser




def record(labels, ser, save_path, app, NUM_RECORDINGS, TOTAL_SAMPLES, SAMPLE_RATE):
    for label in labels:
        for i in range(NUM_RECORDINGS):
            # Using a bytearray since other methods provAed to be too slow (i.e caused too many missing
            # values thus giving a compression effect on the sound)
            data = bytearray()
            bytes_read = 0

            for x in range(1, 5):
                if(x < 4):
                    print("{} recording {} starts in {}".format(label, i+1, 4-x))
                    app.menu_label.config(text = "{} recording {} starts in {}".format(label, i+1, 4-x))
                    sleep(1)
                else:
                    print("Speak Now\n")
                    app.menu_label.config(text = "Speak Now")
                    sleep(0.15)
            # Reading TOTAL_SAMPLES * 2 worth of bytes from the serial and writing them to our bytearray
            # factor of 2 comes from the fact that each sample is 16-bits (2 bytes) and not 8-bits
            while bytes_read < TOTAL_SAMPLES * 2:
                availableBytes = ser.inWaiting()
                for _ in range(availableBytes):
                    data += ser.read()
                bytes_read += availableBytes


            # amplify the data bby multiplying every value in the bytearray
            multiplied_data = audioop.mul(data, SAMPLE_WIDTH, AMPLIFICATION_FACTOR)


            # make .wav file
            folder = os.path.join(save_path, label)
            path, dirs, files = next(os.walk(folder))
            file_count = str(len(files))
            file_path = os.path.join(save_path, label, label+"_audio_file"+file_count+".wav")

            with wave.open(file_path, "wb") as out_f:
                out_f.setnchannels(NUM_CHANNELS)
                out_f.setsampwidth(SAMPLE_WIDTH)
                out_f.setframerate(SAMPLE_RATE)
                out_f.writeframesraw(multiplied_data)

            print("Done recording")
            app.menu_label.config(text = "Done recording")
            sleep(1)




def get_labels(save_path, labels):
    labels_final = []
    #checking if label has occured before
    for x in labels:
        if x not in labels_final:
            labels_final.append(x.strip())

    for label in labels_final:
        folder = os.path.join(save_path, label)
        if(not os.path.exists(folder)):
            os.makedirs(folder)

    return labels_final

def upload_recording_script(app):
    platform_name = check_platform()
    cli_is_installed = check_cli(platform_name, app)
    file_name = os.path.join('"' + wd, 'arduino_record_script"')
    app.menu_label.configure(text = "Uploading the recording script, please wait!")
    Start_Process(cli_is_installed, platform_name, app, file_name)

def run_all(app, save_path, user_labels, NUM_RECORDINGS, SAMPLE_RATE, SECONDS_OF_AUDIO):

    TOTAL_SAMPLES = SAMPLE_RATE * SECONDS_OF_AUDIO

    if(save_path == ""):
        app.menu_label.config(text = "Please select a dataset save location")
        raise Exception("Select dataset location")
    if(len(user_labels) == 1 and "" in user_labels):
        app.menu_label.config(text = "Please enter at least 1 label")
        raise Exception("Please enter at least 1 label")

    if(not NUM_RECORDINGS.isnumeric()):
        app.menu_label.configure(text = "Enter a number for samples!")
        raise Exception("Enter a number for samples!")

    NUM_RECORDINGS = int(NUM_RECORDINGS)

    if(NUM_RECORDINGS <= 0):
        app.menu_label.configure(text = "Enter a number > 0 for samples!")
        raise Exception("Enter a number > 0 for samples!")

    upload_recording_script(app)
    time.sleep(5)
    ser = read_port(app)
    labels = get_labels(save_path, user_labels)
    record(labels, ser, save_path, app, NUM_RECORDINGS, TOTAL_SAMPLES, SAMPLE_RATE)

if __name__ == "__main__":
    pass