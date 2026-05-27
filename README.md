# 🎙️ Voice Assistant Project

A modular Python-based Voice Assistant that supports:

- 🎤 Voice recognition
- 🔊 Text-to-speech
- 🧠 OpenAI / Hugging Face integration
- 👋 Wake word detection
- 😊 Greeting system
- 🔑 API key management
- 🧩 Extensible architecture

Designed with clean module separation for experimentation, AI assistant development, and future production-ready improvements.

---

# 📂 Project Structure

```bash
voice_assistant/
│
├── api_keys.json
├── api_management.py
│
├── greetings.json
├── greetings.py
│
├── huggingface_apikey_model.py
├── openai_apikey_model.py
│
├── scan_input_devices.py
├── setup_test.py
│
├── structure.py
│
├── text_to_speech.py
├── voice_recognition.py
├── wake_word.py
│
├── voice_assistant_hgface.py
├── voice_assistant_openai.py
│
├── requirements.txt
└── README.md
```

---

# 🚀 Features

## 🎤 Speech Recognition
- Real-time microphone input
- Speech-to-text conversion
- Input device scanning support

## 🔊 Text-to-Speech (TTS)
- AI-generated voice responses
- Modular TTS pipeline
- Easy provider replacement

## 🧠 AI Model Integration

### OpenAI Backend
Supports OpenAI-powered assistant interaction.

File:
```python
voice_assistant_openai.py
```

### Hugging Face Backend
Supports Hugging Face inference APIs.

File:
```python
voice_assistant_hgface.py
```

---

# 👋 Wake Word Detection

Wake word functionality allows the assistant to stay idle until triggered by a keyword.

Example:
- "Hey Assistant"

File:
```python
wake_word.py
```

---

# 🔑 API Key Management

Centralized API key management system.

Files:
```python
api_management.py
api_keys.json
```

Example `api_keys.json`:

```json
{
  "openai_api_key": "your_openai_api_key_here",
  "huggingface_api_key": "your_huggingface_api_key_here"
}
```

---

# ⚙️ Installation

## 1. Clone Repository

```bash
git clone <https://github.com/hasanbahcecii/voice_assistant>
cd voice_assistant
```

---

## 2. Create Virtual Environment

```bash
python3 -m venv venv
```

Activate environment:

### Linux / macOS
```bash
source venv/bin/activate
```

### Windows
```bash
venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Usage

## Run OpenAI Assistant

```bash
python voice_assistant_openai.py
```

---

## Run Hugging Face Assistant

```bash
python voice_assistant_hgface.py
```

---

# 🎧 Audio Device Setup

Scan available microphone devices:

```bash
python scan_input_devices.py
```

Test setup:

```bash
python setup_test.py
```

---

# 🏗️ Architecture

The project follows a modular architecture:

```text
Microphone Input
        ↓
Voice Recognition
        ↓
Wake Word Detection
        ↓
AI Processing (OpenAI / HF)
        ↓
Text Response
        ↓
Text-to-Speech
        ↓
Audio Output
```

---

# 🛠️ Technologies Used

- Python
- OpenAI API
- Hugging Face API
- SpeechRecognition
- PyAudio
- Text-to-Speech libraries

---

# 📈 Future Improvements

- [ ] Streaming responses
- [ ] Local LLM support
- [ ] RAG integration
- [ ] Memory system
- [ ] GPU acceleration
- [ ] Offline speech recognition
- [ ] Multilingual support
- [ ] Docker deployment
- [ ] Web dashboard
- [ ] Mobile integration

---

# ⚡ Performance Considerations

Current bottlenecks are likely:
- Speech recognition latency
- API response time
- TTS generation latency

Potential optimizations:
- Async audio pipeline
- Streaming token generation
- Quantized local models
- GPU inference
- Voice activity detection (VAD)
- Caching common responses

---

# 🔒 Security Notes

- Never commit `api_keys.json`
- Add secrets to `.gitignore`
- Use environment variables in production

---

# 🧪 Development Notes

Recommended improvements for production-grade systems:

- Structured logging
- Config management
- Async architecture
- Unit/integration testing
- Latency benchmarking
- Containerization
- CI/CD pipelines

---

# 🤝 Contributing

Contributions, improvements, and feature ideas are welcome.

Suggested workflow:

```bash
git checkout -b feature/new-feature
git commit -m "Add new feature"
git push origin feature/new-feature
```

---

# 📜 License

This project is open-source and available under the MIT License.

---

Voice AI • LLM Systems 

---