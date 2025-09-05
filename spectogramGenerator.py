from typing import List, Tuple, Dict, Optional
import numpy as np
import librosa
from scipy.ndimage import maximum_filter
from scipy import signal
class SpectrogramGenerator:
    """Generates spectrograms and extracts constellation points"""

    def __init__(
        self, sample_rate: int = 22050, window_size: int = 4096, hop_size: int = 1024
    ):
        self.sample_rate = sample_rate
        self.window_size = window_size
        self.hop_size = hop_size
        self.freq_bins = window_size // 2 + 1

    def generate_spectrogram(
        self, audio_data: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Generate spectrogram using Short-Time Fourier Transform"""
        frequencies, times, spectrogram = signal.spectrogram(
            audio_data,
            fs=self.sample_rate,
            window="hann",
            nperseg=self.window_size,
            noverlap=self.window_size - self.hop_size,
            scaling="spectrum",
        )

        # Convert to dB scale
        spectrogram_db = 10 * np.log10(spectrogram + 1e-12)
        return frequencies, times, spectrogram_db

    def find_peaks(
        self,
        spectrogram: np.ndarray,
        neighborhood_size: int = 20,
        min_amplitude: float = -40,
    ) -> List[Tuple[int, int]]:
        """Find local maxima (peaks) in the spectrogram"""
        # Apply maximum filter to find local maxima
        local_maxima = (
            maximum_filter(spectrogram, size=neighborhood_size) == spectrogram
        )

        # Apply amplitude threshold
        amplitude_threshold = spectrogram > min_amplitude

        # Combine conditions
        peaks = local_maxima & amplitude_threshold

        # Get peak coordinates
        peak_coords = np.where(peaks)
        return list(zip(peak_coords[0], peak_coords[1]))  # (frequency_bin, time_bin)
