#!/bin/bash

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd "$PROJECT_DIR" || exit 1

echo "🚀 Starting Local AI Chatbot..."

# Activate virtual environment
source "$PROJECT_DIR/venv/bin/activate"

# Kill any existing processes
sudo fuser -k 5000/tcp 2>/dev/null
sudo fuser -k 5001/tcp 2>/dev/null

echo "🔹 Launching AI Service..."
python "$PROJECT_DIR/ai_service.py" &

echo "🔹 Launching Node.js Server..."
node "$PROJECT_DIR/server.js" &

sleep 2
echo "✅ Chatbot Backend is running!"
wait
