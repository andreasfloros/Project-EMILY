#include <PDM.h>

// default number of output channels
static const char channels = 1;

// default PCM output frequency
static const int frequency = 16000;

// Buffer to read samples into, each sample is 16-bits
short sampleBuffer[256];

// Number of audio samples read
volatile int samplesRead;

void setup()
{
	Serial.begin(9600);
	while (!Serial)
		;

	// Configure the data receive callback
	PDM.onReceive(onPDMdata);

	// Optionally set the gain
	// Defaults to 20 on the BLE Sense and -10 on the Portenta Vision Shield
	PDM.setGain(0);

	// Initialize PDM with:
	// - one channel (mono mode)
	// - a 16 kHz sample rate for the Arduino Nano 33 BLE Sense
	// - a 32 kHz or 64 kHz sample rate for the Arduino Portenta Vision Shield
	if (!PDM.begin(channels, frequency))
	{
		Serial.println("Failed to start PDM!");
		while (1);
	}
}

void loop()
{
	// Wait for samples to be read
	if (samplesRead)
	{

		Serial.write((uint8_t *)sampleBuffer, sizeof(sampleBuffer[0]) * samplesRead);

		// Clear the read count
		samplesRead = 0;
	}
}

/**
 * Callback function to process the data from the PDM microphone.
 * NOTE: This callback is executed as part of an ISR.
 * Therefore using `Serial` to print messages inside this function isn't supported.
 * */
void onPDMdata()
{
	// Query the number of available bytes
	int bytesAvailable = PDM.available();

	// Read into the sample buffer
	PDM.read(sampleBuffer, bytesAvailable);

	// 16-bit, 2 bytes per sample
	samplesRead = bytesAvailable / 2;
}