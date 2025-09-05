from typing import List, Tuple
import hashlib
import numpy as np
from spectrogram_utils import SpectrogramGenerator


class FingerprintGenerator:
    """Generates audio fingerprints from constellation points"""

    def __init__(self, target_zone_length: int = 5, target_zone_start: int = 1):
        self.target_zone_length = target_zone_length
        self.target_zone_start = target_zone_start

    def generate_hashes(self, peaks: List[Tuple[int, int]]) -> List[Tuple[str, int]]:
        """Generate fingerprint hashes from constellation points"""
        hashes = []

        # Sort peaks by time
        peaks = sorted(peaks, key=lambda x: x[1])

        for i, anchor_peak in enumerate(peaks):
            anchor_freq, anchor_time = anchor_peak

            # Look for target peaks in the target zone
            for j in range(
                i + self.target_zone_start,
                min(i + self.target_zone_start + self.target_zone_length, len(peaks)),
            ):
                target_freq, target_time = peaks[j]

                # Calculate time difference
                time_delta = target_time - anchor_time

                if time_delta <= 0:
                    continue

                # Create hash from frequency pair and time delta
                hash_input = f"{anchor_freq}|{target_freq}|{time_delta}"
                fingerprint_hash = hashlib.sha1(hash_input.encode()).hexdigest()

                # Store hash with anchor time offset
                hashes.append((fingerprint_hash, anchor_time))

        return hashes

    def generate_fingerprint(
        self, audio_data: np.ndarray, sample_rate: int
    ) -> List[Tuple[str, int]]:
        """Complete fingerprint generation pipeline"""
        # Generate spectrogram
        spec_gen = SpectrogramGenerator()
        frequencies, times, spectrogram = spec_gen.generate_spectrogram(
            audio_data, sample_rate
        )

        # Find peaks
        peaks = spec_gen.find_peaks(spectrogram)

        # Generate hashes
        hashes = self.generate_hashes(peaks)

        return hashes
