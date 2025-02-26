import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { FaMicrophone, FaSun, FaMoon } from "react-icons/fa";
import "./index.css";

function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [darkMode, setDarkMode] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { text: input, sender: "user" }];
    setMessages(newMessages);
    setInput("");

    try {
      const response = await axios.post("http://127.0.0.1:11434/api/generate", {
        model: "mistral",
        prompt: input,
        stream: false,
      });

      setMessages([...newMessages, { text: response.data.response, sender: "bot" }]);
    } catch (error) {
      setMessages([...newMessages, { text: "Error connecting to AI", sender: "bot" }]);
    }
  };

  const handleSpeechInput = () => {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.onresult = (event) => {
      setInput(event.results[0][0].transcript);
    };
    recognition.start();
  };

  return (
    <div className={`app-container ${darkMode ? "dark-mode" : ""}`}>
      <button className="theme-toggle" onClick={() => setDarkMode(!darkMode)}>
        {darkMode ? <FaSun /> : <FaMoon />}
      </button>

      <div className="chat-box">
        <h1>Local AI Chatbot</h1>
        <div className="chat-history">
          {messages.map((msg, index) => (
            <p key={index} className={`message ${msg.sender}`}>
              {msg.text}
            </p>
          ))}
          <div ref={chatEndRef} />
        </div>

        <div className="input-container">
          <button className="mic-btn" onClick={handleSpeechInput}>
            <FaMicrophone />
          </button>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Type or say your message..."
          />
          <button className="send-btn" onClick={sendMessage}>Send</button>
        </div>
      </div>
    </div>
  );
}

export default App;
