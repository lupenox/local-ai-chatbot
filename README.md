# Local Multi-Model AI Assistant

A desktop AI assistant prototype built with React, Electron, Flask, Hugging Face Transformers, and PyTorch.

The goal of this project is to explore privacy-focused local AI workflows by combining a desktop interface, local model inference, speech interaction, and dynamic model selection into a single application.

## Features

- Desktop application powered by Electron
- React-based chat interface
- Flask API backend for local inference
- Multiple model selection support
- Speech recognition integration
- Wake-word workflow support
- Text-to-speech responses
- Privacy-focused local execution

## Technology Stack

### Frontend
- React
- Electron
- JavaScript
- CSS

### Backend
- Python
- Flask
- Hugging Face Transformers
- PyTorch

### Voice Features
- SpeechRecognition
- PyAudio
- Picovoice Porcupine
- pyttsx3

## Architecture

```text
Electron Desktop App
        |
        v
     React UI
        |
        v
    Flask API
        |
        v
 Hugging Face Models
```

## Project Structure

```text
local-ai-chatbot/
├── ai_service.py          # Flask inference service
├── wake.py                # Wake-word and speech interface
├── main.js                # Electron entry point
├── requirements.txt
├── ui/
│   ├── src/
│   └── package.json
├── .env.example
└── README.md
```

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/lupenox/local-ai-chatbot.git
cd local-ai-chatbot
```

### 2. Create a Python environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Add your Picovoice access key to `.env`.

### 4. Install frontend and Electron dependencies

```bash
npm install
cd ui
npm install
cd ..
```

### 5. Start the backend

```bash
python ai_service.py
```

### 6. Launch the desktop application

```bash
npm start
```

## Example API Request

```bash
curl -X POST http://127.0.0.1:5001/generate \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello AI","model":"flan-t5"}'
```

## Portfolio Highlights

This project demonstrates:

- Desktop application development
- API design and integration
- Local AI model deployment
- Frontend and backend integration
- Speech interaction workflows
- Debugging and system integration

## Future Improvements

- Ollama integration
- Additional local model backends
- Whisper speech recognition
- Conversation persistence
- Smart home integrations
- Fine-tuned custom models

## License

MIT
