# 🧠 Local AI Chatbot - Multi-Model Support & Electron Desktop App

A **fully offline AI chatbot** with **wake-word detection**, **multi-model support**, and a **cross-platform desktop app** built with **Electron**.  
Now featuring **Ollama & Mistral models**, **voice-to-text**, and a **secure local backend**—**NO internet required**! 🚀  

![Demo Screenshot](docs/demo.png)

---

## 🚀 Features
- ✅ **Multiple AI Models** (Mistral, BlenderBot, Falcon, T5, Flan-T5, Phi-2, Tiny-Llama, Distil-GPT2)
- ✅ **Wake-word activation** ("Computer" by default, customizable)
- ✅ **Voice-to-text** via `speech_recognition`
- ✅ **Local AI chatbot** (Mistral/Ollama backend)
- ✅ **Electron Desktop App** (Runs standalone)
- ✅ **Offline text-to-speech** with `pyttsx3`
- ✅ **No internet required** for core functions

---

## 🛠️ Installation & Setup

### 1️⃣ Install Dependencies
```bash
sudo apt install portaudio19-dev
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2️⃣ Set Up Picovoice (Wake Word)

1. Sign up at [Picovoice Console](https://console.picovoice.ai/)
2. Get your Access Key and replace it in `wake.py`:
   ```python
   ACCESS_KEY = "your-picovoice-access-key"
   ```
3. Optionally, train a custom wake word (e.g., "Lupenox")

### 3️⃣ Run the AI Chatbot

Use the Bash script to start both Flask and Node.js services:
```bash
/home/logan-lapierre/Desktop/personal_projects/local-ai-chatbot/run_chatbot.sh
```

Or start manually:
- Start the backend:
```bash
python ai_service.py
```

- Start the Electron desktop app:
```bash
npx electron .
```

Or run the standalone app (Local AI Chatbot in Applications).

---

## 🎛️ Multi-Model Support

You can now switch AI models dynamically!

### 🧠 Available Models:

| Model Name     | Hugging Face ID |
|----------------|-----------------|
| Chemistry-T5  | GT4SD/multitask-text-and-chemistry-t5-base-augm |
| Mistral Instruct | mistralai/Mistral-7B-Instruct |
| BlenderBot (Chatbot) | facebook/blenderbot-400M-distill |
| Falcon-7B     | tiiuae/falcon-7b-instruct |
| Flan-T5       | google/flan-t5-small |
| Tiny Llama    | TinyLlama/TinyLlama-1.1B-Chat-v0.3 |
| Distil-GPT2   | distilgpt2 |
| Phi-2         | microsoft/phi-2 |

### 🔹 To select a model, send a request:
```bash
curl -X POST "http://127.0.0.1:5001/generate" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello AI!", "model": "mistral"}'
```

---

## 🖥️ Electron Standalone App

- The chatbot can now run as a desktop app!
- Installed in `~/Applications/LocalAIChatbot-linux-x64/`
- To launch manually:

```bash
~/Applications/LocalAIChatbot-linux-x64/Local\ AI\ Chatbot --no-sandbox
```

- If the desktop shortcut doesn’t work, check `local-ai-chatbot.desktop`.

---

## 📌 To-Do / Future Features

- Custom wake-word support (e.g., "Lupenox")
- Integration with Whisper AI for better speech recognition
- Smart home control (MQTT/Home Assistant)
- Advanced AI personality responses
- Local fine-tuning of AI models
- Convert `.webp` icons to `.ico` for better desktop integration

---

## 💙 Contributions & Support

Want to improve the chatbot? Fork, star, and contribute! 🚀
Feel free to open an issue if you have feature ideas!

---
