import pvporcupine
import pyaudio
import struct
import speech_recognition as sr
import requests
import pyttsx3

# 🔑 Replace this with your actual Picovoice access key
ACCESS_KEY = "nybfq6Ktat6lgQ66zdK3GTXglNmnsS5zMmjgj/Cf7NB62eEWLJZUuA=="

# 🎤 Initialize Wake Word Detection
porcupine = pvporcupine.create(access_key=ACCESS_KEY, keywords=["computer"])  # Change "computer" if needed
pa = pyaudio.PyAudio()
stream = pa.open(format=pyaudio.paInt16, channels=1, rate=porcupine.sample_rate, input=True, frames_per_buffer=porcupine.frame_length)

# 🎙️ Speech Recognition & TTS Engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

print("🎤 Listening for the wake word...")

while True:
    try:
        pcm = struct.unpack_from("h" * porcupine.frame_length, stream.read(porcupine.frame_length))
        keyword_index = porcupine.process(pcm)

        if keyword_index >= 0:
            print("🔥 Wake word detected!")

            # 🎤 Capture User Command using SpeechRecognition (no extra PyAudio use)
            with sr.Microphone() as source:
                print("🎙️ Say your command...")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)

            try:
                command = recognizer.recognize_google(audio)
                print(f"🗣️ You said: {command}")

                # 🔗 Send Command to Chatbot API
                response = requests.post("http://localhost:5000/chat", json={"message": command})
                bot_reply = response.json().get("response", "Sorry, I didn't get that.")

                print(f"🤖 AI Response: {bot_reply}")

                # 🔊 Convert AI Response to Speech
                engine.say(bot_reply)
                engine.runAndWait()

            except sr.UnknownValueError:
                print("❌ Could not understand audio.")
            except sr.RequestError:
                print("❌ Speech recognition request failed.")

    except KeyboardInterrupt:
        print("\n👋 Exiting...")
        break
    except Exception as e:
        print(f"⚠️ Error: {e}")

# 🛑 Cleanup Resources
stream.stop_stream()
stream.close()
pa.terminate()
porcupine.delete()
