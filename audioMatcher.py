from typing import List, Tuple, Dict
import sqlite3
from collections import defaultdict, Counter
from audio_database import AudioDatabase


class AudioMatcher:
    """Matches audio fingerprints and identifies songs"""

    def __init__(self, database: AudioDatabase):
        self.database = database

    def match_audio(
        self, query_fingerprints: List[Tuple[str, int]], min_matches: int = 5
    ) -> List[Tuple[Dict, float, int]]:
        """Match query fingerprints against database"""
        query_hashes = [fp[0] for fp in query_fingerprints]
        query_times = {fp[0]: fp[1] for fp in query_fingerprints}

        # Query database
        db_matches = self.database.query_fingerprints(query_hashes)

        if not db_matches:
            return []

        # Calculate time alignment for each song
        song_scores = defaultdict(list)
        for song_id, db_fingerprints in db_matches.items():
            for db_hash, db_time in db_fingerprints:
                if db_hash in query_times:
                    query_time = query_times[db_hash]
                    time_delta = db_time - query_time
                    song_scores[song_id].append(time_delta)

        # Find the best match for each song
        final_matches = {}
        for song_id, time_deltas in song_scores.items():
            if len(time_deltas) >= min_matches:
                time_delta_counts = Counter(time_deltas)
                best_alignment, alignment_count = time_delta_counts.most_common(1)[0]

                # Calculate confidence score
                confidence = alignment_count / len(query_fingerprints)
                final_matches[song_id] = (confidence, alignment_count)

        # Sort by confidence and return results
        results = []
        for song_id, (confidence, match_count) in sorted(
            final_matches.items(), key=lambda x: x[1][0], reverse=True
        ):
            song_info = self.database.get_song_by_id(song_id)
            if song_info:
                results.append((song_info, confidence, match_count))

        return results
