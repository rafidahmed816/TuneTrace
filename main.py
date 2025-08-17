import streamlit as st
import os
from audio_database import AudioDatabase
from fingerprint_system import FingerprintSystem

# Initialize DB + System
db = AudioDatabase()
fp_system = FingerprintSystem()

# Ensure songs folder exists
SONGS_DIR = "songs"
os.makedirs(SONGS_DIR, exist_ok=True)

st.set_page_config(page_title="TuneTrace", page_icon="🎵", layout="centered")

st.title("🎵 TuneTrace")
st.markdown("### Manage and play your songs")

menu = st.sidebar.radio("Menu", ["Add Song", "Show Songs", "Play Song"])

if menu == "Add Song":
    uploaded_file = st.file_uploader("Upload a song", type=["mp3", "wav"])
    if uploaded_file:
        file_path = os.path.join(SONGS_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        db.add_song(uploaded_file.name, file_path)
        st.success(f"✅ {uploaded_file.name} added successfully!")

elif menu == "Show Songs":
    songs = db.get_all_songs()
    if songs:
        st.write("### 🎶 Song List")
        for sid, name, path in songs:
            st.write(f"{sid}. {name}")
    else:
        st.info("No songs added yet.")

elif menu == "Play Song":
    songs = db.get_all_songs()
    if songs:
        song_choice = st.selectbox("Select a song to play", [s[1] for s in songs])
        if st.button("▶️ Play"):
            selected_path = [s[2] for s in songs if s[1] == song_choice][0]
            fp_system.play_song(selected_path)
            st.success(f"Playing {song_choice} 🎧")
    else:
        st.warning("No songs available to play.")
