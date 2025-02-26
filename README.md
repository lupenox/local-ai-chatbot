# Local AI Chatbot with Wake-Word Detection

A local AI chatbot powered by **Ollama & Mistral**, running entirely **offline** for secure, private voice interactions. Now featuring **wake-word detection** using **Picovoice Porcupine**!

![Demo Screenshot](docs/demo.png)

---

## 🚀 Features
- **Wake-word activation** ("Computer" by default, can be customized)
- **Voice-to-text** via `speech_recognition`
- **Local AI chatbot** (Mistral/Ollama backend)
- **Offline text-to-speech** with `pyttsx3`
- **No internet required** for core functions

## 🛠️ Setup & Installation

### 1️⃣ Install Dependencies
```bash
sudo apt install portaudio19-dev
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2️⃣ Set Up Picovoice (Wake Word)
- Sign up at [Picovoice Console](https://console.picovoice.ai/)
- Get your **Access Key** and replace it in `wake.py`:
  ```python
  ACCESS_KEY = "your-picovoice-access-key"
  ```
- Optionally, train a **custom wake word** (e.g., "Lupenox")

### 3️⃣ Run the Chatbot
Start the backend:
```bash
node server.js
```

Start voice detection:
```bash
python wake.py
```
Say "Computer" (or your custom wake word) and start chatting!

## 📌 To-Do / Future Features
- [ ] Custom wake-word support (Lupenox)
- [ ] Integration with **Whisper AI** for better speech recognition
- [ ] Smart home control using MQTT/Home Assistant
- [ ] Advanced AI personality responses

---
**Made with ❤️ by [Lupenox](https://github.com/lupenox)** 🚀

