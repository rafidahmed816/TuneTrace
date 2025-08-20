import streamlit as st
import os
from audio_database import AudioDatabase
from fingerprint_system import FingerprintSystem
import pandas as pd
# Initialize DB + System
db = AudioDatabase()
fp_system = FingerprintSystem()


SONGS_DIR = "songs"
os.makedirs(SONGS_DIR, exist_ok=True)

st.set_page_config(page_title="TuneTrace", page_icon="🎵", layout="centered")

st.title("🎵 TuneTrace")
st.markdown("### Manage and play your songs")

menu = st.sidebar.radio("Menu", ["Add Song", "Show Songs", "Play Song"])

if menu == "Add Song":
    with st.form("add_song_form"):
        uploaded_file = st.file_uploader("Upload a song", type=["mp3", "wav"])
        title = st.text_input("Song Title")

        # Suggest existing artists dynamically
        existing_artists = [row[0] for row in db.conn.execute(
            "SELECT DISTINCT artist FROM songs WHERE artist IS NOT NULL").fetchall()]
        artist = st.selectbox("Artist", options=existing_artists + ["<New Artist>"])
        if artist == "<New Artist>":
            artist = st.text_input("Enter new artist name")

        # Genre selection
        genre = st.selectbox("Genre", ["Pop", "Rock", "Classical", "Hip-Hop", "Jazz", "Other"])

        submitted = st.form_submit_button("Save Song")

        if submitted and uploaded_file and title and artist:
            file_path = os.path.join(SONGS_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # calculate duration
            import librosa
            y, sr = librosa.load(file_path, sr=None, mono=True)
            duration = librosa.get_duration(y=y, sr=sr)

            db.add_song(title, artist, genre, file_path, duration)
            st.success(f"✅ {title} by {artist} added successfully!")


elif menu == "Show Songs":
    songs = db.get_all_songs()
    if songs:
        st.write("### 🎶 Song List")
        
        df = pd.DataFrame(songs, columns=["ID", "Title", "Artist", "Genre", "Path", "Duration", "Date Added"])
        st.dataframe(df)

    else:
        st.info("No songs added yet.")

elif menu == "Play Song":
    songs = db.get_all_songs()
    if songs:
        song_choice = st.selectbox("Select a song to play", [s[1] for s in songs])
        if st.button("▶️ Play"):
            # get file_path where title matches song_choice
            selected_path = [s[4] for s in songs if s[1] == song_choice][0]
            fp_system.play_song(selected_path)
            st.success(f"Playing {song_choice} 🎧")

