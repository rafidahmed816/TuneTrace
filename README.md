# TuneTrace 🎶

TuneTrace is a music-related project aimed at providing advanced audio analysis, including music fingerprinting, song identification, and other audio processing features. The repository includes various components for audio analysis, including spectrogram generation, fingerprint extraction, and database management.

## Features ✨

- **Audio Fingerprinting**: Generate unique fingerprints for audio files. 📝
- **Spectrogram Generation**: Create spectrograms for audio analysis. 📊
- **Song Identification**: Identify songs based on generated fingerprints. 🎧
- **Database Integration**: Store and query fingerprints in an SQLite database. 🗄️

## Installation 🔧

### Prerequisites ⚙️

- Python 3.x
- Git

### Clone the Repository 🛠️

Clone this repository to your local machine using:

```bash
git clone https://github.com/rafidahmed816/TuneTrace.git


🚀 Setup Virtual Environment

📂 Navigate to the project directory:

cd TuneTrace

🐍 Create and activate a virtual environment:

On Windows:


.\venv\Scripts\activate

On macOS/Linux:

python3 -m venv venv
source venv/bin/activate

📦 Install the required dependencies:

pip install -r requirements.txt

▶️ Usage

To run the project, activate the virtual environment and run the main script:

python -u #path/to/audioFingerprinting.py#
EXAMPLE: python -u "h:\audio-fingerprint\audioFingerprinting.py"

## Notes 🗒️

- For best results, use audio files in **WAV or MP3 format** with a consistent sample rate.  
- The SQLite database (`fingerprints.db`) will be generated automatically when running the script.  
- Activate the virtual environment before running any scripts:  
  ```bash
  source venv/bin/activate  # macOS/Linux
  .\venv\Scripts\activate   # Windows
Large audio files may take longer to process — please be patient.

Currently, only single-channel audio is fully supported.

File paths with spaces may require quotes, e.g., "C:/path to/audiofile.mp3".

Logs and outputs are printed to the console by default; you can redirect them to a file if needed.

The project is designed to be modular, so additional audio analysis or database features can be added without changing the main workflow.

Keep Python dependencies up to date with:

```bash
   pip install --upgrade -r requirements.txt


It’s recommended to run the project on Python 3.8+, as older versions may have compatibility issues.


sudo apt-get install libportaudio2
sudo apt-get install portaudio19-dev