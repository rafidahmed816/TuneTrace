import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write

class MicrophoneRecorder:
    def __init__(self, sample_rate=44100, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels

    def record_audio(self, duration: int, output_filename: str):
        """Records audio from the microphone for a given duration and saves it to a file."""
        print(f"Recording for {duration} seconds...")
        recording = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, channels=self.channels, dtype='int16')
        sd.wait()  # Wait until recording is finished
        write(output_filename, self.sample_rate, recording)  # Save as WAV file
        print(f"Recording finished and saved to {output_filename}")