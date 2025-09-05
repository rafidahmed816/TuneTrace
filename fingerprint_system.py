import librosa
import sounddevice as sd
import numpy as np
import sqlite3
import os
from typing import List, Tuple, Dict, Optional
from audio_processor import AudioProcessor
from fingerPrintGenerator import FingerprintGenerator
from audioMatcher import AudioMatcher
from audio_database import AudioDatabase


class FingerprintSystem:
    """Main system class that orchestrates all components"""

    def __init__(self, db_name: str = "songs.db"):
        self.audio_processor = AudioProcessor()
        self.fingerprint_generator = FingerprintGenerator()
        self.database = AudioDatabase(db_name)
        self.matcher = AudioMatcher(self.database)

    def add_song_to_database(
        self, file_path: str, title: str, artist: str = None, genre: str = "Unknown"
    ) -> bool:
        """Add a song to the fingerprint database"""
        try:
            print(f"Processing: {title} by {artist or 'Unknown Artist'}")

            # Load and process audio
            audio_data, sample_rate = self.audio_processor.load_audio(file_path)
            audio_data = self.audio_processor.normalize_audio(audio_data)

            # Generate fingerprints
            fingerprints = self.fingerprint_generator.generate_fingerprint(
                audio_data, sample_rate
            )

            if not fingerprints:
                print(f"Warning: No fingerprints generated for {title}")
                return False

            # Add to database
            duration = len(audio_data) / sample_rate
            song_id = self.database.add_song(title, artist, genre, file_path, duration)
            if song_id:
                self.database.add_fingerprints(song_id, fingerprints)
                print(f"Added {len(fingerprints)} fingerprints for '{title}'")
                return True
            else:
                print(f"Failed to add song '{title}' to the database.")
                return False

        except Exception as e:
            print(f"Error processing {title}: {e}")
            return False

    def identify_audio(
        self,
        file_path: str = None,
        audio_data: np.ndarray = None,
        sample_rate: int = None,
    ) -> List[Tuple[Dict, float, int]]:
        """Identify audio from file or audio data"""
        try:
            if file_path:
                audio_data, sample_rate = self.audio_processor.load_audio(file_path)
            elif audio_data is None:
                raise ValueError("Either file_path or audio_data must be provided")

            # Normalize audio
            audio_data = self.audio_processor.normalize_audio(audio_data)

            # Generate fingerprints
            query_fingerprints = self.fingerprint_generator.generate_fingerprint(
                audio_data, sample_rate
            )

            if not query_fingerprints:
                print("No fingerprints could be generated from the query audio")
                return []

            print(f"Generated {len(query_fingerprints)} query fingerprints")

            # Match against database
            matches = self.matcher.match_audio(query_fingerprints)

            return matches

        except Exception as e:
            print(f"Error identifying audio: {e}")
            return []

    def batch_add_songs(self, songs_info: List[Dict]) -> int:
        """Add multiple songs to the database"""
        success_count = 0

        for song_info in songs_info:
            file_path = song_info.get("file_path")
            title = song_info.get("title")
            artist = song_info.get("artist")

            if not file_path or not title:
                print(f"Skipping song: missing file_path or title")
                continue

            if self.add_song_to_database(file_path, title, artist):
                success_count += 1

        return success_count

    def list_database_songs(self) -> List[Dict]:
        """List all songs in the database"""
        return self.database.get_all_songs()

    def search_by_file(self, query_file_path: str, top_n: int = 5) -> None:
        """Search for a song by file and print results"""
        print(f"\nSearching for: {os.path.basename(query_file_path)}")
        print("-" * 50)

        matches = self.identify_audio(query_file_path)

        if not matches:
            print("No matches found!")
            return

        for i, (song_info, confidence, match_count) in enumerate(matches[:top_n]):
            print(f"{i+1}. {song_info['title']} by {song_info['artist'] or 'Unknown'}")
            print(f"   Confidence: {confidence:.2%}")
            print(f"   Matches: {match_count}")
            print()

    def play_song(self, file_path: str):
        """Plays a song given its file path."""
        try:
            audio_data, sample_rate = self.audio_processor.load_audio(file_path)
            sd.play(audio_data, sample_rate)
            sd.wait()
        except Exception as e:
            print(f"Error playing song {file_path}: {e}")
