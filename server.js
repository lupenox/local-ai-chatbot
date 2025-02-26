const express = require("express");
const cors = require("cors");
const axios = require("axios");

const app = express();
app.use(express.json());
app.use(cors());

app.post("/chat", async (req, res) => {
    const userMessage = req.body.message;

    try {
        // 🧠 Send the message to Ollama
        const ollamaResponse = await axios.post("http://localhost:11434/api/generate", {
            model: "mistral",  // Change to "gemma" or another model if needed
            prompt: userMessage,
            stream: false
        });

        // 📝 Extract the AI response
        const botResponse = ollamaResponse.data.response || "I didn't get that.";

        console.log(`🤖 AI Response: ${botResponse}`);
        res.json({ response: botResponse });

    } catch (error) {
        console.error("⚠️ Error communicating with Ollama:", error);
        res.status(500).json({ response: "Sorry, something went wrong." });
    }
});

const PORT = 5000;
app.listen(PORT, () => {
    console.log(`🚀 Backend running on http://localhost:${PORT}`);
});
