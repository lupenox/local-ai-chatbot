const express = require("express");
const cors = require("cors");
const axios = require("axios");

const app = express();
app.use(express.json());
app.use(cors());

// AI Personality & Memory
const SYSTEM_MESSAGE = `You are Lupenox, a friendly, witty AI assistant. You love Linux, cybersecurity, and hacking tools. 
You remember important details from the conversation, like the user's name, and try to keep things fun and engaging.`;

let chatHistory = [];

app.post("/chat", async (req, res) => {
    const userMessage = req.body.message;

    // Add user input to chat history
    chatHistory.push(`User: ${userMessage}`);

    try {
        const response = await axios.post("http://127.0.0.1:11434/api/generate", {
            model: "mistral",
            prompt: `${SYSTEM_MESSAGE}\n${chatHistory.join("\n")}\nAssistant:`,
            stream: false,
        });

        const botReply = response.data.response;

        // Add AI response to chat history
        chatHistory.push(`Assistant: ${botReply}`);

        res.json({ response: botReply });
    } catch (error) {
        console.error("Error fetching AI response:", error);
        res.status(500).json({ response: "Oops! Something went wrong." });
    }
});

// Clear chat history after some time
setInterval(() => {
    chatHistory = [];
}, 30 * 60 * 1000); // Clears every 30 minutes

const PORT = 5000;
app.listen(PORT, () => {
    console.log(`🔥 AI Backend running on http://localhost:${PORT}`);
});
