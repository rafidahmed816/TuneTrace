# spectrogram_utils.py
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.ndimage import maximum_filter
from typing import List, Tuple, Optional
from audio_processor import AudioProcessor  # Importing the existing AudioProcessor class 


class SpectrogramGenerator:
    """Generates spectrograms and detects peaks, ready for fingerprinting."""

    def __init__(self, window_size: int = 4096, hop_size: int = 1024):
        self.window_size = window_size
        self.hop_size = hop_size
        self.audio_processor = AudioProcessor()  # Uses existing AudioProcessor

    def generate_spectrogram(
        self, audio_data: np.ndarray, sample_rate: int
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Compute spectrogram in dB scale"""
        frequencies, times, Sxx = signal.spectrogram(
            audio_data,
            fs=sample_rate,
            window="hann",
            nperseg=self.window_size,
            noverlap=self.window_size - self.hop_size,
            scaling="spectrum",
        )
        Sxx_db = 10 * np.log10(Sxx + 1e-12)
        return frequencies, times, Sxx_db

    def find_peaks(
        self, spectrogram: np.ndarray, neighborhood_size: int = 20, min_amplitude: float = -40
    ) -> List[Tuple[int, int]]:
        """Detect local maxima in spectrogram"""
        local_max = maximum_filter(spectrogram, size=neighborhood_size) == spectrogram
        amplitude_thresh = spectrogram > min_amplitude
        peaks = np.where(local_max & amplitude_thresh)
        return list(zip(peaks[0], peaks[1]))  # (freq_bin, time_bin)

    def visualize_spectrogram(
        self,
        frequencies: np.ndarray,
        times: np.ndarray,
        spectrogram: np.ndarray,
        peaks: Optional[List[Tuple[int, int]]] = None,
        title: str = "Spectrogram",
    ):
        """Optional visualization for debugging"""
        plt.figure(figsize=(12, 6))
        plt.pcolormesh(times, frequencies, spectrogram, shading="gouraud")
        plt.colorbar(label="Magnitude (dB)")

        if peaks:
            peak_times = [times[p[1]] for p in peaks]
            peak_freqs = [frequencies[p[0]] for p in peaks]
            plt.scatter(peak_times, peak_freqs, c="red", s=2, alpha=0.7)

        plt.xlabel("Time (s)")
        plt.ylabel("Frequency (Hz)")
        plt.title(title)
        plt.tight_layout()
        plt.show()

    def process_file(
        self, file_path: str, visualize: bool = False
    ) -> Tuple[np.ndarray, np.ndarray, List[Tuple[int, int]]]:
        """
        Complete pipeline for a single audio file:
        1. Load and normalize audio
        2. Generate spectrogram
        3. Detect peaks
        4. visualization
        """
        audio_data, sr = self.audio_processor.load_audio(file_path)
        audio_data = self.audio_processor.normalize_audio(audio_data)

        frequencies, times, spectrogram = self.generate_spectrogram(audio_data, sr)
        peaks = self.find_peaks(spectrogram)

        if visualize:
            self.visualize_spectrogram(frequencies, times, spectrogram, peaks, title=file_path)
        
        print(f"Detected {len(peaks)} peaks\n")
        print("First 10 peaks (Frequency Hz, Time s):")
        for i, (f_idx, t_idx) in enumerate(peaks[:10]):
            freq_hz = frequencies[f_idx]
            time_s = times[t_idx]
            print(f"{i+1}: Frequency = {freq_hz:.1f} Hz, Time = {time_s:.3f} s")
        return frequencies, times, peaks



# if __name__ == "__main__":
#     generator = SpectrogramGenerator()
#     freqs, times, peaks = generator.process_file("songs/song_1.mp3", visualize=True)
#     print(f"Detected {len(peaks)} peaks")
