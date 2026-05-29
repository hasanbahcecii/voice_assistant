# 🎙️ LLM-Powered Voice Assistant

🌐 **[Live Demo — Hugging Face Spaces](https://hasanbahceci-voice-assistant.hf.space)**

A modular, end-to-end voice assistant integrating real-time speech recognition (STT), dual-backend LLM response generation, and neural text-to-speech (TTS) — built for extensibility and production-ready improvement.

---

## 🏗️ Architecture

```
Microphone Input
      ↓
Speech Recognition (STT)
      ↓
Wake Word Detection
      ↓
AI Processing (OpenAI API / Hugging Face API)
      ↓
Text Response
      ↓
Text-to-Speech (Edge TTS)
      ↓
Audio Output
```

---

## 📂 Project Structure

```
voice_assistant/
│
├── api_keys.json               # API key storage (gitignored)
├── api_management.py           # Centralized key management
│
├── greetings.json              # Greeting templates
├── greetings.py                # Greeting logic
│
├── huggingface_apikey_model.py # Hugging Face LLM integration
├── openai_apikey_model.py      # OpenAI LLM integration
│
├── scan_input_devices.py       # Audio device scanner
├── setup_test.py               # Environment validation
├── structure.py                # Project config
│
├── voice_recognition.py        # STT module
├── text_to_speech.py           # TTS module
├── wake_word.py                # Wake word detection
│
├── voice_assistant_openai.py   # Full pipeline — OpenAI backend
├── voice_assistant_hgface.py   # Full pipeline — Hugging Face backend
│
├── app.py                      # Gradio web interface (Hugging Face Spaces)
├── requirements.txt
└── README.md
```

---

## 🚀 Features

- **Real-time STT** — Microphone input via SpeechRecognition + PyAudio
- **Dual LLM Backend** — Swap between OpenAI and Hugging Face with a single file swap
- **Neural TTS** — Edge TTS (Microsoft Azure neural voices, no API key required)
- **Wake Word Detection** — Assistant stays idle until triggered ("Hey Assistant")
- **Modular Design** — Each component (STT, TTS, LLM, wake word) is independently replaceable
- **Web Interface** — Gradio app deployed on Hugging Face Spaces

---

## 🛠️ Technologies

| Component | Technology |
|---|---|
| Speech-to-Text | SpeechRecognition + PyAudio |
| LLM (Cloud) | OpenAI API / Hugging Face Inference API |
| Text-to-Speech | Edge TTS (edge-tts) |
| Web Interface | Gradio |
| Wake Word | Custom keyword detection |

---

## ⚙️ Installation

```bash
git clone https://github.com/hasanbahcecii/voice_assistant
cd voice_assistant

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### API Key Setup

Create `api_keys.json` in the project root:

```json
{
  "openai_api_key": "your_openai_api_key_here",
  "huggingface_api_key": "your_huggingface_api_key_here"
}
```

---

## ▶️ Usage

**OpenAI backend:**
```bash
python voice_assistant_openai.py
```

**Hugging Face backend:**
```bash
python voice_assistant_hgface.py
```

**Gradio web interface (local):**
```bash
python app.py
```

**Scan audio devices:**
```bash
python scan_input_devices.py
```

---

## ⚡ Performance

| Component | Estimated Latency |
|---|---|
| Speech Recognition (STT) | ~0.5 – 1.0s |
| LLM API Response | ~1.0 – 2.0s |
| TTS Generation | ~0.3 – 0.5s |
| **End-to-End (local)** | **~2 – 4s** |

Measured on local machine with OpenAI API backend.

**Planned optimizations:**
- Async audio pipeline
- Streaming token generation
- Voice Activity Detection (VAD)
- Local LLM support (Ollama / llama.cpp)
- Quantized models for reduced latency

---

## 🔒 Security

- `api_keys.json` is gitignored — never commit API keys
- Use environment variables in production (`os.environ.get(...)`)
- HF Spaces deployment uses Hugging Face Secrets

---

## 📈 Roadmap

- [ ] Streaming LLM responses
- [ ] Local LLM support (offline mode)
- [ ] RAG integration (document Q&A)
- [ ] Conversation memory
- [ ] Multilingual support (Turkish / English)
- [ ] Docker deployment
- [ ] CI/CD pipeline

---

## 📜 License

MIT License — open source, free to use and modify.

---

*Voice AI · LLM Systems · Built with Python*