import pvporcupine
import pyaudio
import struct

# Initialize Porcupine with a built-in wake word (e.g., "Alexa", "Hey Google") or create your own
porcupine = pvporcupine.create(access_key="nybfq6Ktat6lgQ66zdK3GTXglNmnsS5zMmjgj/Cf7NB62eEWLJZUuA==", keywords=["computer"])  # Or "Lupenox"

# Audio setup
pa = pyaudio.PyAudio()
audio_stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)

print("🎤 Listening for the wake word...")

while True:
    pcm = audio_stream.read(porcupine.frame_length)
    pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

    keyword_index = porcupine.process(pcm)
    if keyword_index >= 0:
        print("🔥 Wake word detected!")
        break  # Replace this with triggering your AI chat function

# Cleanup
audio_stream.close()
pa.terminate()
porcupine.delete()
