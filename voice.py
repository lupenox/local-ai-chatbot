import speech_recognition as sr
import pyttsx3
import requests

# Initialize speech recognition and text-to-speech
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Function to capture voice input
def get_voice_input():
    with sr.Microphone() as source:
        print("Listening... 🎤")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio)
            print(f"Recognized: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that.")
            return None
        except sr.RequestError:
            print("Error with the speech recognition service.")
            return None

# Function to send text to chatbot and get a response
def chat_with_ai(user_input):
    url = "http://localhost:5000/chat"  # Adjust this if needed
    payload = {"message": user_input}
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        return response.json().get("response", "Sorry, I couldn't get a response.")
    else:
        return "Error connecting to chatbot."

# Function to convert text to speech
def speak_response(response_text):
    print(f"Speaking: {response_text}")
    engine.say(response_text)
    engine.runAndWait()

# Main Loop: Listen → Process → Respond
while True:
    print("\nSay something:")
    user_input = get_voice_input()

    if user_input:
        ai_response = chat_with_ai(user_input)
        speak_response(ai_response)
