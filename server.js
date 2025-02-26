const express = require("express");
const cors = require("cors");
const axios = require("axios");

const app = express();
const PORT = 5000;

app.use(cors());
app.use(express.json());

app.post("/chat", async (req, res) => {
  try {
    const response = await axios.post("http://127.0.0.1:11434/api/generate", {
      model: "mistral",
      prompt: req.body.prompt,
    });

    res.json({ reply: response.data.response });
  } catch (error) {
    console.error("Error:", error);
    res.status(500).json({ error: "Error communicating with Ollama" });
  }
});

app.listen(PORT, () => {
  console.log(`🚀 Backend running on http://localhost:${PORT}`);
});
