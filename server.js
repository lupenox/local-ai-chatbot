const express = require("express");
const cors = require("cors");
const axios = require("axios");
const sqlite3 = require("sqlite3").verbose();

const app = express();
app.use(express.json());
app.use(cors());

// AI Personality & System Message
const SYSTEM_MESSAGE = `You are Lupenox, a friendly, witty AI assistant. You love Linux, cybersecurity, and hacking tools.
You remember details from the conversation and try to keep things fun and engaging.`;

// Initialize Database
const db = new sqlite3.Database("./chatbot.db", (err) => {
    if (err) console.error("Database connection error:", err.message);
    else console.log("💾 Connected to SQLite database.");
});

// Create Table for Chat Logs
db.run(`
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        message TEXT,
        response TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
`);

app.post("/chat", async (req, res) => {
    const userMessage = req.body.message;
    const userName = req.body.user || "User";

    try {
        // Retrieve previous conversation history
        db.all("SELECT message, response FROM chat_history ORDER BY timestamp DESC LIMIT 10", async (err, rows) => {
            if (err) {
                console.error("Error retrieving chat history:", err);
                return res.status(500).json({ response: "Error retrieving chat history." });
            }

            // Format chat history for context
            let chatContext = rows.map(row => `User: ${row.message}\nAssistant: ${row.response}`).join("\n");

            // Generate response using AI
            const response = await axios.post("http://127.0.0.1:11434/api/generate", {
                model: "mistral",
                prompt: `${SYSTEM_MESSAGE}\n${chatContext}\nUser: ${userMessage}\nAssistant:`,
                stream: false,
            });

            const botReply = response.data.response;

            // Store conversation in database
            db.run("INSERT INTO chat_history (user, message, response) VALUES (?, ?, ?)", [userName, userMessage, botReply]);

            res.json({ response: botReply });
        });

    } catch (error) {
        console.error("Error fetching AI response:", error);
        res.status(500).json({ response: "Oops! Something went wrong." });
    }
});

// API to Retrieve Past Conversations
app.get("/history", (req, res) => {
    db.all("SELECT * FROM chat_history ORDER BY timestamp DESC", (err, rows) => {
        if (err) {
            console.error("Error retrieving chat logs:", err);
            res.status(500).json({ error: "Failed to retrieve chat logs." });
        } else {
            res.json(rows);
        }
    });
});

const PORT = 5000;
app.listen(PORT, () => {
    console.log(`🔥 AI Backend running on http://localhost:${PORT}`);
});
