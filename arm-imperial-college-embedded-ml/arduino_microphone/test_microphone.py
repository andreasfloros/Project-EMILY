# # Upload the arduino_microphone.ino file to the Arduino and then run this script to record an audio track
# and subsequently save to a .wav file.
#
# The code below achieves the following:
#   1. Creates a bytearray from the data in the serial buffer (as much of that data as we specify)
#   2. Multiplies everything in the bytearray by an amplification factor since original audio is too quiet
#   3. Writes to a .wav file

# Imports: (install using pip3 if not already present)
import serial
import wave
import audioop

# Specify parameters used
SAMPLE_RATE = 16000
SAMPLE_WIDTH = 2
NUM_CHANNELS = 1
AMPLIFICATION_FACTOR = 10
SECONDS_OF_AUDIO = 1
TOTAL_SAMPLES = SAMPLE_RATE * SECONDS_OF_AUDIO


# Serial Port, check which port your Arduino is in (perhaps not COM5 for you)
ser = serial.Serial('COM4', 9600, timeout=None)

# print("before flushing: ", ser.inWaiting())
# ser.reset_input_buffer()
# ser.reset_output_buffer()
# print("after flushing: ", ser.inWaiting())

# Using a bytearray since other methods proved to be too slow (i.e caused too many missing
# values thus giving a compression effect on the sound)
data = bytearray()
bytes_read = 0

# Reading TOTAL_SAMPLES * 2 worth of bytes from the serial and writing them to our bytearray
# factor of 2 comes from the fact that each sample is 16-bits (2 bytes) and not 8-bits
while bytes_read < TOTAL_SAMPLES * 2:
    availableBytes = ser.inWaiting()
    for _ in range(availableBytes):
        data += ser.read()
    bytes_read += availableBytes


# Sanity check: Ensure we captured the correct number of samples might not be
# exactly the same due to the Arduino sending samples in batchesand thus last
# batch of samples might exceed the total numebr of samples specified here
print(len(data),SAMPLE_RATE*SECONDS_OF_AUDIO)


# amplify the data bby multiplying every value in the bytearray
multiplied_data = audioop.mul(data, SAMPLE_WIDTH, AMPLIFICATION_FACTOR)


# make .wav file
with wave.open("new_audio_file.wav", "wb") as out_f:
    out_f.setnchannels(NUM_CHANNELS)
    out_f.setsampwidth(SAMPLE_WIDTH)
    out_f.setframerate(SAMPLE_RATE)
    out_f.writeframesraw(multiplied_data)