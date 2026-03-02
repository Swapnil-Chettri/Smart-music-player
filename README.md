# 🎵 Smart Music Player

A modern, AI-powered desktop music player built with Python. Featuring an offline voice assistant, professional 10-band equalizer, and a sleek Spotify-inspired interface.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![UI](https://img.shields.io/badge/UI-CustomTkinter-black)

---

## ✨ Features

- **🎙️ Offline Voice AI:** Control playback, volume, and effects using natural voice commands (Powered by Vosk).
- **🔍 Smart Fuzzy Search:** Finds songs even with typos or partial names using the Levenshtein Distance algorithm.
- **🎚️ 10-Band Graphic EQ:** Professional-grade frequency control with presets like Bass Boost and Lo-Fi.
- **🎧 DSP Audio Effects:** Real-time Reverb, 3D Audio, and Speed/Pitch manipulation.
- **🎨 Modern UX:** High-DPI responsive dark mode interface with "Spotify Green" accents.
- **🔒 Privacy First:** 100% offline. No data leaves your machine.

---

## 🚀 Installation

### 1. Prerequisites

- **Python 3.10 or higher**
- **VLC Media Player** (Required for the audio engine backend)

### 2. Clone the Repository

```bash
git clone [https://github.com/YOUR_USERNAME/Smart-Music-Player.git](https://github.com/YOUR_USERNAME/Smart-Music-Player.git)
cd Smart-Music-Player
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup AI model

- Download a lightweight Vosk model (e.g., vosk-model-small-en-in-0.4) from Vosk Models.

- Extract the folder into your project directory.

- Update the model_path in src/ui/chat_widget.py to point to your extracted folder.

---

## 🛠 Usage

Run the application using:

```bash
python -m src.main
```

### Voice Commands

- "Play [Song Name]"

- "Pause" / "Stop" / "Next" / "Previous"

- "Volume [0-100]"

- "Apply Bass Boost" / "Enable Lo-fi"

- "3D Audio"

---

## 🏗 System Architecture

The project follows the Model-View-Controller (MVC) pattern:

- **Model:** VLC Audio Engine & JSON Database.

- **View:** CustomTkinter GUI components.

- **Controller:** Main logic handling the interface-engine bridge and AI threading.
  
![licensed-image](https://github.com/user-attachments/assets/b095145f-32cf-4c39-a0d9-4b3e7030f6b4)

---

## 📦 Tech Stack

- GUI: CustomTkinter

- **Audio:** <a href="https://pypi.org/project/python-vlc/">python-vlc</a>,<a href="https://github.com/jiaaro/pydub">Pydub</a>

- **AI/STT:** <a href="https://alphacephei.com/vosk/">Vosk</a>

- **TTS:** <a href="https://pyttsx3.readthedocs.io/en/latest/">pyttsx3</a>

- **Search:** <a href="https://github.com/maxbachmann/RapidFuzz">RapidFuzz</a>

---

## 📄 License

This project is licensed under the MIT License - see the <a href="https://www.google.com/search?q=LICENSE">LICENSE</a> file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
