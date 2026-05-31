import os
import struct

import pvporcupine
import pyaudio
import pyttsx3
import requests
import speech_recognition as sr
from dotenv import load_dotenv

load_dotenv()

PICOVOICE_ACCESS_KEY = os.getenv("PICOVOICE_ACCESS_KEY")
CHATBOT_API_URL = os.getenv("CHATBOT_API_URL", "http://127.0.0.1:5001/generate")
WAKE_WORD = os.getenv("WAKE_WORD", "computer")

if not PICOVOICE_ACCESS_KEY:
    raise RuntimeError(
        "Missing PICOVOICE_ACCESS_KEY. Add it to a .env file or export it as an environment variable."
    )

porcupine = None
pa = None
stream = None

try:
    porcupine = pvporcupine.create(
        access_key=PICOVOICE_ACCESS_KEY,
        keywords=[WAKE_WORD],
    )
    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=porcupine.sample_rate,
        input=True,
        frames_per_buffer=porcupine.frame_length,
    )

    recognizer = sr.Recognizer()
    engine = pyttsx3.init()

    print(f"Listening for the wake word: {WAKE_WORD}")

    while True:
        pcm = struct.unpack_from(
            "h" * porcupine.frame_length,
            stream.read(porcupine.frame_length, exception_on_overflow=False),
        )
        keyword_index = porcupine.process(pcm)

        if keyword_index >= 0:
            print("Wake word detected.")

            with sr.Microphone() as source:
                print("Say your command...")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)

            try:
                command = recognizer.recognize_google(audio)
                print(f"You said: {command}")

                response = requests.post(
                    CHATBOT_API_URL,
                    json={"message": command, "model": "flan-t5"},
                    timeout=60,
                )
                response.raise_for_status()
                bot_reply = response.json().get("response", "Sorry, I didn't get that.")

                print(f"AI Response: {bot_reply}")
                engine.say(bot_reply)
                engine.runAndWait()

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
    if pa is not None:
        pa.terminate()
    if porcupine is not None:
        porcupine.delete()
