import sqlite3
import os

class AudioDatabase:
    def __init__(self, db_name="songs.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            path TEXT NOT NULL
        );
        """
        self.conn.execute(query)
        self.conn.commit()

    def add_song(self, name: str, path: str):
        query = "INSERT INTO songs (name, path) VALUES (?, ?);"
        self.conn.execute(query, (name, path))
        self.conn.commit()

    def get_all_songs(self):
        query = "SELECT id, name, path FROM songs;"
        return self.conn.execute(query).fetchall()

    def close(self):
        self.conn.close()
