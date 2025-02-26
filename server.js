const express = require("express");
const cors = require("cors");

const app = express();
app.use(express.json());
app.use(cors());

app.post("/chat", (req, res) => {
    const userMessage = req.body.message;

    // TODO: Replace with real AI processing (right now it echoes back)
    const botResponse = `You said: "${userMessage}"`;

    res.json({ response: botResponse });
});

const PORT = 5000;
app.listen(PORT, () => {
    console.log(`🚀 Backend running on http://localhost:${PORT}`);
});
