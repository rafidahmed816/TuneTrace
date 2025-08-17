import librosa
import sounddevice as sd

class FingerprintSystem:
    def __init__(self, sample_rate=22050):
        self.sample_rate = sample_rate

    def play_song(self, file_path: str):
        """Load and play song using librosa + sounddevice"""
        try:
            audio_data, sr = librosa.load(file_path, sr=self.sample_rate, mono=True)
            sd.play(audio_data, sr)
            sd.wait()  # wait until playback is done
        except Exception as e:
            print(f"Error playing {file_path}: {e}")
