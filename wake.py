import logging
import os
from typing import Any, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

CHATBOT_API_URL = os.getenv("CHATBOT_API_URL", "http://127.0.0.1:5001/generate")
WAKEWORD_MODEL_PATH = os.getenv("WAKEWORD_MODEL_PATH")
WAKEWORD_THRESHOLD = float(os.getenv("WAKEWORD_THRESHOLD", "0.5"))
SELECTED_BACKEND = os.getenv("SELECTED_BACKEND", "huggingface")
SELECTED_MODEL = os.getenv("SELECTED_MODEL", "flan-t5")
SAMPLE_RATE = 16000
FRAME_SIZE = 1280


def send_command_to_ai(
    command: str,
    api_url: str = CHATBOT_API_URL,
    backend: str = SELECTED_BACKEND,
    model: str = SELECTED_MODEL,
) -> str:
    """Send a transcribed voice command to the local Flask `/generate` service."""
    response = requests.post(
        api_url,
        json={"message": command, "backend": backend, "model": model},
        timeout=60,
    )
    response.raise_for_status()
    return response.json().get("response", "Sorry, I didn't get that.")


def listen_for_command(recognizer: Any) -> Optional[str]:
    """Capture a single spoken command after the wake word triggers."""
    import speech_recognition as sr

    with sr.Microphone(sample_rate=SAMPLE_RATE) as source:
        logger.info("Say your command...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio)
        logger.info("You said: %s", command)
        return command
    except sr.UnknownValueError:
        logger.warning("Could not understand audio.")
        return None
    except sr.RequestError as error:
        logger.error("Speech recognition request failed: %s", error)
        return None


def run_wakeword_loop() -> None:
    """
    Continuously monitor 16kHz microphone audio locally with openWakeWord.
    Only captures a full command and queries the AI backend after the wake word exceeds threshold.
    """
    if not WAKEWORD_MODEL_PATH:
        raise RuntimeError(
            "Missing WAKEWORD_MODEL_PATH. Add a local openWakeWord .tflite/.onnx model path to your .env file."
        )

    import numpy as np
    import pyaudio
    import pyttsx3
    import speech_recognition as sr
    from openwakeword.model import Model

    wake_model = Model(wakeword_models=[WAKEWORD_MODEL_PATH])
    recognizer = sr.Recognizer()
    tts_engine = pyttsx3.init()
    pa = pyaudio.PyAudio()
    stream = None

    try:
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=FRAME_SIZE,
        )

        logger.info("Listening for wake word with openWakeWord...")

        while True:
            audio_bytes = stream.read(FRAME_SIZE, exception_on_overflow=False)
            audio_frame = np.frombuffer(audio_bytes, dtype=np.int16)
            prediction = wake_model.predict(audio_frame)

            top_score = max(prediction.values()) if prediction else 0.0
            if top_score < WAKEWORD_THRESHOLD:
                continue

            logger.info("Wake word detected with confidence %.2f.", top_score)
            command = listen_for_command(recognizer)
            if not command:
                continue

            try:
                bot_reply = send_command_to_ai(command)
                logger.info("AI Response: %s", bot_reply)
                tts_engine.say(bot_reply)
                tts_engine.runAndWait()
            except requests.RequestException as error:
                logger.error("Chatbot API request failed: %s", error)

    except KeyboardInterrupt:
        logger.info("Exiting wake-word listener...")
    finally:
        if stream is not None:
            stream.stop_stream()
            stream.close()
        pa.terminate()


if __name__ == "__main__":
    run_wakeword_loop()
