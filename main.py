import streamlit as st
import os
from audio_database import AudioDatabase
from fingerprint_system import FingerprintSystem
import pandas as pd
from spectrogram_utils import SpectrogramGenerator
import numpy as np

# Initialize DB + Systems
db = AudioDatabase()
fingerprint_system = FingerprintSystem()
spec_gen = SpectrogramGenerator()


SONGS_DIR = "songs"
os.makedirs(SONGS_DIR, exist_ok=True)

st.set_page_config(page_title="TuneTrace", page_icon="🎵", layout="centered")

st.title("🎵 TuneTrace")
st.markdown("### Manage and play your songs")

menu = st.sidebar.radio(
    "Menu", ["Add Song", "Show Songs", "Play Song", "Identify Song"]
)

if menu == "Add Song":
    with st.form("add_song_form"):
        uploaded_file = st.file_uploader("Upload a song", type=["mp3", "wav"])
        title = st.text_input("Song Title")

        artist = st.text_input("Artist Name")

        genre = st.selectbox(
            "Genre", ["Pop", "Rock", "Classical", "Hip-Hop", "Jazz", "Other"]
        )

        submitted = st.form_submit_button("Save Song")

    if submitted and uploaded_file and title and artist:
        file_path = os.path.join(SONGS_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Add song to database and generate fingerprints
        with st.spinner("Adding song and generating fingerprints..."):
            fingerprint_system.add_song_to_database(file_path, title, artist, genre)

        st.success(f"✅ {title} by {artist} added successfully!")
        st.info(
            "🎵 Song has been added to both the main database and fingerprint database for identification."
        )

        # Spectrogram visualization
        st.markdown("### 🎵 Spectrogram Preview with Detected Peaks")
        freqs, times, peaks = spec_gen.process_file(file_path, visualize=True)

        # I added this to visualize the spectrogram in Streamlit
        import matplotlib.pyplot as plt

        # Use the spectrogram values instead of raw STFT for proper dimensions
        y, sr = spec_gen.audio_processor.load_audio(file_path)
        frequencies, times_spect, Sxx_db = spec_gen.generate_spectrogram(y, sr)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.pcolormesh(times_spect, frequencies, Sxx_db, shading="gouraud")

        # Overlay peaks
        if peaks:
            peak_times = [times_spect[p[1]] for p in peaks]
            peak_freqs = [frequencies[p[0]] for p in peaks]
            ax.scatter(peak_times, peak_freqs, c="red", s=2, alpha=0.7)

        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Frequency (Hz)")
        ax.set_title(f"Spectrogram for {title}")
        st.pyplot(fig)
        st.write(f"Detected {len(peaks)} peaks in the spectrogram.")


elif menu == "Show Songs":
    songs = db.get_all_songs()
    if songs:
        st.write("### 🎶 Song List")

        df = pd.DataFrame(
            songs,
            columns=[
                "ID",
                "Title",
                "Artist",
                "Genre",
                "Path",
                "Duration",
                "Date Added",
            ],
        )
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
            fingerprint_system.play_song(selected_path)
            st.success(f"Playing {song_choice} 🎧")
    else:
        st.info("No songs available to play.")

elif menu == "Identify Song":
    st.markdown("### 🎵 Identify Songs from Audio Clips")
    st.info(
        "Upload a short audio clip to identify which song from the database it matches."
    )

    uploaded_audio = st.file_uploader(
        "Upload audio clip for identification", type=["mp3", "wav"]
    )

    if uploaded_audio:
        # Save uploaded audio temporarily
        temp_path = os.path.join(SONGS_DIR, f"temp_query_{uploaded_audio.name}")
        with open(temp_path, "wb") as f:
            f.write(uploaded_audio.getbuffer())

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔍 Identify Song"):
                with st.spinner("Analyzing audio and searching database..."):
                    try:
                        matches = fingerprint_system.identify_audio(temp_path)

                        if matches:
                            st.success("🎉 Top Match Found!")
                            song_info, confidence, match_count = matches[0]

                            with st.expander(
                                f"Match: {song_info['title']} by {song_info['artist'] or 'Unknown'}",
                                expanded=True,
                            ):
                                col_info, col_play = st.columns([2, 1])

                                with col_info:
                                    st.write(f"**Confidence:** {confidence:.2%}")
                                    st.write(
                                        f"**Matches:** {match_count} fingerprint matches"
                                    )
                                    st.write(
                                        f"**Duration:** {song_info['duration']:.1f} seconds"
                                    )

                                    # Show match quality
                                    if confidence > 0.7:
                                        st.success("🎯 Excellent match!")
                                    elif confidence > 0.4:
                                        st.warning("🎵 Good match")
                                    else:
                                        st.info("🤔 Possible match")

                                with col_play:
                                    if st.button("▶️ Play Matched Song"):
                                        if os.path.exists(song_info["file_path"]):
                                            fingerprint_system.play_song(
                                                song_info["file_path"]
                                            )
                                            st.success("Playing song! 🎧")
                                        else:
                                            st.error("Song file not found")
                        else:
                            st.warning("No matches found in the database.")
                            st.info(
                                "Try uploading a different audio clip or add more songs to the database."
                            )

                    except Exception as e:
                        st.error(f"Error during identification: {e}")

                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        with col2:
            if st.button("🎧 Preview Query Audio"):
                fingerprint_system.play_song(temp_path)
                st.info("Playing your query audio...")
