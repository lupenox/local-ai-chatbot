import { useState } from "react";
import axios from "axios";

function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);

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

  return (
    <div className="chat-container">
      <h1>Local AI Chatbot</h1>
      <div className="chat-box">
        {messages.map((msg, index) => (
          <p key={index} className={msg.sender}>{msg.text}</p>
        ))}
      </div>
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        placeholder="Type your message..."
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}

export default App;
