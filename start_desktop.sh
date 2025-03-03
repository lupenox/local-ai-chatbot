#!/bin/bash

# Get the absolute path of the project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "🚀 Starting Chatbot Desktop App..."

# Ensure we're in the right directory
cd "$PROJECT_DIR" || exit 1

# Ensure the virtual environment is activated
if [ -d "$PROJECT_DIR/venv" ]; then
    source "$PROJECT_DIR/venv/bin/activate"
else
    echo "❌ Virtual environment not found!"
    exit 1
fi

# Kill any existing processes on ports 5000 and 5001
echo "🔹 Checking for existing Flask or Node processes..."
sudo fuser -k 5000/tcp 2>/dev/null
sudo fuser -k 5001/tcp 2>/dev/null

# Start the backend services
echo "🔹 Launching AI Service..."
python "$PROJECT_DIR/ai_service.py" &

echo "🔹 Launching Node.js Server..."
node "$PROJECT_DIR/server.js" &

# Wait a moment for servers to start
sleep 2

echo "✅ Chatbot Backend is running!"

# Start the Electron App
if [ -d "$PROJECT_DIR/desktop-ui" ]; then
    cd "$PROJECT_DIR/desktop-ui"
    npx electron .
else
    echo "❌ Error: desktop-ui/ folder not found!"
    exit 1
fi
