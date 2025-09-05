import sqlite3
import os
from typing import List, Tuple, Dict
from collections import defaultdict, Counter


class AudioDatabase:
    def __init__(self, db_name="songs.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        # For normal app use:
        query = """
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist TEXT,
            genre TEXT,
            file_path TEXT NOT NULL,
            duration REAL,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        self.conn.execute(query)
        self.conn.commit()

        # Create fingerprints table
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS fingerprints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                song_id INTEGER,
                hash TEXT,
                time_offset INTEGER,
                FOREIGN KEY (song_id) REFERENCES songs (id)
            )
        """
        )
        self.conn.commit()

        # ----- Optional one-time drop during dev -----
        # Uncomment only once if you want a fresh table:
        # self.conn.execute("DROP TABLE IF EXISTS songs;")
        # self.conn.execute(query)
        # self.conn.commit()

    def add_song(
        self, title: str, artist: str, genre: str, path: str, duration: float
    ) -> int:
        query = "INSERT INTO songs (title, artist, genre, file_path, duration) VALUES (?, ?, ?, ?, ?);"
        cursor = self.conn.cursor()
        cursor.execute(query, (title, artist, genre, path, duration))
        self.conn.commit()
        return cursor.lastrowid

    def get_all_songs(self):
        query = "SELECT id, title, artist, genre, file_path, duration, date_added FROM songs;"
        return self.conn.execute(query).fetchall()

    def add_fingerprints(self, song_id: int, fingerprints: List[Tuple[str, int]]):
        """Add fingerprints for a song"""
        # Create fingerprints table if it doesn't exist
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS fingerprints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                song_id INTEGER,
                hash TEXT,
                time_offset INTEGER,
                FOREIGN KEY (song_id) REFERENCES songs (id)
            )
        """
        )

        fingerprint_data = [
            (song_id, str(hash_val), int(time_offset))
            for hash_val, time_offset in fingerprints
        ]

        cursor.executemany(
            """
            INSERT INTO fingerprints (song_id, hash, time_offset)
            VALUES (?, ?, ?)
        """,
            fingerprint_data,
        )

        self.conn.commit()

    def query_fingerprints(
        self, query_hashes: List[str]
    ) -> Dict[int, List[Tuple[str, int]]]:
        """Query database for matching fingerprints"""
        if not query_hashes:
            return {}

        cursor = self.conn.cursor()

        # Create placeholders for the IN clause
        placeholders = ",".join(["?"] * len(query_hashes))
        query = f"""
            SELECT song_id, hash, time_offset
            FROM fingerprints
            WHERE hash IN ({placeholders})
        """

        cursor.execute(query, query_hashes)
        results = cursor.fetchall()

        # Group results by song_id
        matches = defaultdict(list)
        for song_id, hash_val, time_offset in results:
            matches[song_id].append((hash_val, time_offset))

        return dict(matches)

    def get_song_by_id(self, song_id: int) -> Dict:
        """Get song information by song ID"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, title, artist, file_path, duration FROM songs WHERE id = ?",
            (song_id,),
        )
        result = cursor.fetchone()
        if result:
            return {
                "id": result[0],
                "title": result[1],
                "artist": result[2],
                "file_path": result[3],
                "duration": result[4],
            }
        return None

    def close(self):
        self.conn.close()
