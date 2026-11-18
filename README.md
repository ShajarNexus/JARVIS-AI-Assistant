# JARVIS-AI-Assistant

# J.A.R.V.I.S – Local AI Desktop Assistant

A personal AI-powered desktop assistant built with Python, Ollama, and local AI models. JARVIS combines conversational AI, persistent memory, voice interaction, and Windows PC automation in a modern desktop interface.

The goal is to create a smart desktop companion that understands natural language, remembers previous conversations, responds with a natural female voice, and helps control your computer — while keeping AI processing local.

## ✨ Features Implemented

### 1. AI-Powered Conversations
- Integrated with **Ollama** for local AI inference.
- Uses **Qwen 2.5 3B** as the language model.
- Supports natural-language questions and conversations.
- Runs the AI model locally without requiring a paid AI API.

### 2. Modern Desktop Interface
- Built using **Python and CustomTkinter**.
- Modern dark-themed JARVIS dashboard.
- Animated JARVIS orb with system status.
- Chat interface with separate user and assistant messages.
- Sidebar for managing previous conversations.
- Text input and send functionality.
- Stop Speaking control to stop voice responses.

### 3. Conversation History
- Uses **SQLite** for persistent conversation storage.
- Automatically saves user and assistant messages.
- Restores previous conversations after restarting the application.
- Supports creating new conversations.
- Allows users to delete conversations.

### 4. Personal Memory System
- Detects and stores personal information from conversations.
- Uses SQLite to maintain persistent personal memories.
- Provides a dedicated Memory Manager interface.
- Allows users to view, update, and forget stored memories.
- Makes relevant saved information available to the AI during conversations.

### 5. Female Voice Responses
- Integrated **Kokoro-82M ONNX** for text-to-speech.
- Uses the `af_river` female voice.
- Generates speech locally.
- Uses a background worker and queue for speech generation.
- Plays generated audio through `sounddevice`.
- Supports stopping ongoing speech.

### 6. Voice Recognition and Interaction
- Integrated **Faster-Whisper** for offline English speech recognition.
- Uses the `small.en` speech recognition model.
- Captures microphone input and converts speech into text.
- Supports continuous microphone listening in the main application.
- Detects speech and silence to process voice commands.
- Supports voice-based Yes/No confirmation for PC automation.

### 7. Windows PC Automation
JARVIS understands natural-language requests and generates structured action plans using the local Qwen model.

Currently supported actions include:

- Open Google Chrome.
- Open Notepad.
- Open Calculator.
- Open File Explorer.
- Open Visual Studio Code.
- Open drives and folders.
- Open YouTube.
- Search YouTube for requested content.
- Tell the current time.
- Schedule Windows shutdown.
- Schedule Windows restart.
- Cancel a scheduled shutdown or restart.

**Safety and Confirmation:**
- JARVIS asks for confirmation before executing automation actions.
- Users can confirm or cancel actions using spoken responses such as "Yes" and "No".
- Unclear responses or confirmation timeouts cancel the pending action.
- Shutdown and restart operations are scheduled with a 60-second delay.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.11 | Main programming language |
| CustomTkinter | Desktop user interface |
| Ollama | Local AI model runtime |
| Qwen 2.5 3B | Conversational AI and command understanding |
| SQLite | Conversation history and personal memory |
| Kokoro-82M ONNX | Text-to-speech |
| Faster-Whisper | Speech recognition |
| SoundDevice | Microphone recording and audio playback |
| SoundFile | Audio file handling |
| Requests | Communication with the local Ollama API |
| Windows Subprocess | PC automation |

## 📁 Project Structure

```text
JARVIS/
│
├── app/
│   ├── __init__.py
│   ├── window.py
│   ├── theme.py
│   ├── orb.py
│   ├── ai_engine.py
│   ├── automation.py
│   ├── voice_engine.py
│   ├── speech_engine.py
│   ├── memory.py
│   └── memory_window.py
│
├── models/
│   ├── tts/
│   │   ├── kokoro-v1.0.onnx
│   │   └── voices-v1.0.bin
│   │
│   └── speech/
│       └── (Faster-Whisper model files)
│
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

*Note: AI model files, the virtual environment, generated audio, and personal database files should not be uploaded to GitHub.*

## ⚙️ Installation and Setup

### Prerequisites

- Windows 10 or Windows 11.
- Python 3.11.
- Ollama installed.
- Git installed.
- A microphone and speakers/headphones.

### 1. Clone the repository

```bash
git clone https://github.com/ShajarNexus/JARVIS-AI-Assistant.git
cd JARVIS-AI-Assistant
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it in PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Download the local AI model

Make sure Ollama is installed and running.

```bash
ollama pull qwen2.5:3b
```

### 5. Download required voice models

The Kokoro ONNX model and voice files must be downloaded separately and placed inside:

```text
models/tts/
```

Required files:

- `kokoro-v1.0.onnx`
- `voices-v1.0.bin`

The Faster-Whisper English model is downloaded automatically on its first run when speech recognition is initialized.

### 6. Run JARVIS

```bash
python main.py
```

---

## 🔒 Privacy and Local Processing

JARVIS is designed around local AI processing.

- Qwen runs locally through Ollama.
- Kokoro generates voice responses locally.
- Faster-Whisper performs speech recognition locally after downloading its model.
- Conversation history and personal memories are stored in SQLite on the user's computer.
- No paid AI API subscription is required.

Internet access is required for initial model downloads and online features such as YouTube searches.

## 🚀 Future Development Roadmap

The project is actively being developed. Planned improvements include:

- [ ] Wake-word detection (Hey JARVIS).
- [ ] English and Urdu language support.
- [ ] More Windows application and system controls.
- [ ] Advanced file and folder management.
- [ ] Improved contextual understanding and conversations.
- [ ] Enhanced microphone activation and speech detection.
- [ ] More advanced automation capabilities.
- [ ] Improved user interface and animations.

## 🎯 Project Goal

The long-term goal is to build a personal AI desktop assistant inspired by JARVIS that can communicate naturally, remember useful information, respond through voice, and safely automate everyday computer tasks.

## 👨‍💻 Developer

**Shajar Abbas**

*JARVIS – Your Personal AI Desktop Companion.*
