# audio_processor.py
import numpy as np
import librosa
from typing import Tuple, List  # Ensure List is imported from typing

class AudioProcessor:
    """Handles audio file loading and preprocessing"""

    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate

    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        try:
            # Use librosa with audioread/ffmpeg support
            audio_data, sr = librosa.load(file_path, sr=self.sample_rate, mono=True)
            return audio_data, sr
        except Exception as e_librosa:
            print(f"librosa failed: {e_librosa}")
            raise ValueError(f"Could not load audio file {file_path}: {e_librosa}")

    def normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Normalize audio data to [-1, 1] range"""
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            return audio_data / max_val
        return audio_data

    def apply_window(
        self, audio_data: np.ndarray, window_size: int = 4096, hop_size: int = 1024
    ) -> List[np.ndarray]:  # List should now be properly recognized
        """Apply windowing to audio data"""
        windows = []
        for i in range(0, len(audio_data) - window_size, hop_size):
            window = audio_data[i : i + window_size]
            windows.append(window * np.hanning(window_size))
        return windows
