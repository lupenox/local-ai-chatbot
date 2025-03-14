import express from 'express';
import path from 'path';
import bodyParser from 'body-parser';
import cors from 'cors';
import fetch from 'node-fetch';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const port = 3000;

// Middleware
app.use(express.static(path.join(__dirname, 'ui')));
app.use(bodyParser.json());
app.use(cors());

// Forward the request to the Python AI service
app.post('/generate', async (req, res) => {
    const { message, model } = req.body;
    if (!message || !model) {
        return res.status(400).json({ error: "Missing message or model." });
    }

    try {
        const aiResponse = await fetch('http://127.0.0.1:5001/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message, model })
        });

        const data = await aiResponse.json();
        res.json(data);
    } catch (error) {
        console.error("Error forwarding request to AI service:", error);
        res.status(500).json({ error: "Failed to connect to AI service." });
    }
});

app.listen(port, () => {
    console.log(`Server is running at http://localhost:${port}`);
});
