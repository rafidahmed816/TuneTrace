import sqlite3
import os


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

        # ----- Optional one-time drop during dev -----
        # Uncomment only once if you want a fresh table:
        # self.conn.execute("DROP TABLE IF EXISTS songs;")
        # self.conn.execute(query)
        # self.conn.commit()

    def add_song(self, title: str, artist: str, genre: str, path: str, duration: float):
        query = "INSERT INTO songs (title, artist, genre, file_path, duration) VALUES (?, ?, ?, ?, ?);"
        self.conn.execute(query, (title, artist, genre, path, duration))
        self.conn.commit()

    def get_all_songs(self):
        query = "SELECT id, title, artist, genre, file_path, duration, date_added FROM songs;"
        return self.conn.execute(query).fetchall()

    def close(self):
        self.conn.close()
