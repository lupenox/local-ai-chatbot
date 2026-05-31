import os

import numpy as np
import pyaudio
import pyttsx3
import requests
import speech_recognition as sr
from dotenv import load_dotenv
from openwakeword.model import Model

load_dotenv()

CHATBOT_API_URL = os.getenv("CHATBOT_API_URL", "http://127.0.0.1:5001/generate")
WAKEWORD_MODEL_PATH = os.getenv("WAKEWORD_MODEL_PATH")
WAKEWORD_THRESHOLD = float(os.getenv("WAKEWORD_THRESHOLD", "0.5"))
SELECTED_MODEL = os.getenv("SELECTED_MODEL", "flan-t5")

if not WAKEWORD_MODEL_PATH:
    raise RuntimeError(
        "Missing WAKEWORD_MODEL_PATH. Add a local openWakeWord .tflite/.onnx model path to your .env file."
    )

wake_model = Model(wakeword_models=[WAKEWORD_MODEL_PATH])
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()
pa = pyaudio.PyAudio()
stream = None

try:
    stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=1280,
    )

    print("Listening for wake word with openWakeWord...")

    while True:
        audio_bytes = stream.read(1280, exception_on_overflow=False)
        audio_frame = np.frombuffer(audio_bytes, dtype=np.int16)
        prediction = wake_model.predict(audio_frame)

        top_score = max(prediction.values()) if prediction else 0

        if top_score >= WAKEWORD_THRESHOLD:
            print(f"Wake word detected with confidence {top_score:.2f}.")

            with sr.Microphone(sample_rate=16000) as source:
                print("Say your command...")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)

            try:
                command = recognizer.recognize_google(audio)
                print(f"You said: {command}")

                response = requests.post(
                    CHATBOT_API_URL,
                    json={"message": command, "model": SELECTED_MODEL},
                    timeout=60,
                )
                response.raise_for_status()
                bot_reply = response.json().get("response", "Sorry, I didn't get that.")

                print(f"AI Response: {bot_reply}")
                tts_engine.say(bot_reply)
                tts_engine.runAndWait()

            except sr.UnknownValueError:
                print("Could not understand audio.")
            except sr.RequestError as error:
                print(f"Speech recognition request failed: {error}")
            except requests.RequestException as error:
                print(f"Chatbot API request failed: {error}")

except KeyboardInterrupt:
    print("\nExiting...")
finally:
    if stream is not None:
        stream.stop_stream()
        stream.close()
    pa.terminate()
