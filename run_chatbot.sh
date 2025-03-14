#!/bin/bash

# Set the project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd "$PROJECT_DIR" || exit 1

echo "🚀 Starting Local AI Chatbot..."

# Activate virtual environment
if [ -d "$PROJECT_DIR/venv" ]; then
    source "$PROJECT_DIR/venv/bin/activate"
    echo "✅ Virtual environment activated."
else
    echo "❌ Virtual environment not found. Exiting."
    exit 1
fi

# Kill existing processes on ports 5000, 5001, and 3000
for PORT in 5000 5001 3000; do
    if sudo lsof -t -i:$PORT &>/dev/null; then
        sudo fuser -k ${PORT}/tcp 2>/dev/null
        echo "🔄 Killed process running on port $PORT."
    fi
done

# Launch AI Service
echo "🔹 Launching AI Service..."
python "$PROJECT_DIR/ai_service.py" &
AI_PID=$!
sleep 2  # Allow time for Flask to start

# Check if Flask service is running
if ! kill -0 $AI_PID 2>/dev/null; then
    echo "❌ Failed to start AI Service. Exiting."
    exit 1
else
    echo "✅ AI Service is running on port 5001."
fi

# Launch Node.js Server
echo "🔹 Launching Node.js Server..."
node "$PROJECT_DIR/server.js" &
NODE_PID=$!

# Check if Node.js service is running
sleep 2
if ! kill -0 $NODE_PID 2>/dev/null; then
    echo "❌ Failed to start Node.js server. Exiting."
    kill $AI_PID 2>/dev/null
    exit 1
else
    echo "✅ Node.js Server is running on port 3000."
fi

echo "✅ Chatbot Backend is fully operational! (Press Ctrl+C to stop)"

# Wait for processes to end
wait $AI_PID
wait $NODE_PID
