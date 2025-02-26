import { useState, useEffect, useRef } from "react";
import axios from "axios";
import SpeechRecognition, { useSpeechRecognition } from "react-speech-recognition";

function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const chatRef = useRef(null);

  // Speech-to-text for voice input
  const startListening = () => {
    SpeechRecognition.startListening({ continuous: true });
  };
  
  const { transcript, resetTranscript } = useSpeechRecognition();

  // Update input field with spoken text
  useEffect(() => {
    if (transcript) {
      setInput(transcript);
    }
  }, [transcript]);

  // Function to send a message
  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { text: input, sender: "user" }];
    setMessages(newMessages);
    setInput("");
    resetTranscript(); // Clear transcript after sending

    try {
      const response = await axios.post("http://127.0.0.1:11434/api/generate", {
        model: "mistral",
        prompt: input,
        stream: false,
      });

      const aiResponse = response.data.response;
      setMessages([...newMessages, { text: aiResponse, sender: "bot" }]);
      speak(aiResponse); // Make AI speak its response
    } catch (error) {
      setMessages([...newMessages, { text: "Error connecting to AI", sender: "bot" }]);
    }
  };

  // Function to make AI speak its response
  const speak = (text) => {
    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(text);
    synth.speak(utterance);
  };

  // Auto-scroll to latest message
  useEffect(() => {
    chatRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="chat-container">
      <h1>Local AI Chatbot</h1>
      <div className="chat-box">
        {messages.map((msg, index) => (
          <p key={index} className={msg.sender}>{msg.text}</p>
        ))}
        <div ref={chatRef}></div> {/* Invisible div for auto-scroll */}
      </div>

      <div className="input-area">
        <button className="voice-btn" onClick={startListening}>🎤</button>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Type or say your message..."
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}

export default App;
