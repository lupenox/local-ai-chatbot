#!/bin/bash
set -e

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

echo "Starting Local Multi-Model AI Assistant..."

if [ -d "$PROJECT_DIR/.venv" ]; then
    source "$PROJECT_DIR/.venv/bin/activate"
    echo "Activated virtual environment (.venv)."
elif [ -d "$PROJECT_DIR/venv" ]; then
    source "$PROJECT_DIR/venv/bin/activate"
    echo "Activated virtual environment (venv)."
else
    echo "Error: No Python virtual environment found (.venv or venv)."
    exit 1
fi

cleanup() {
    echo ""
    echo "Shutting down services..."
    if [ -n "${AI_PID:-}" ] && kill -0 "$AI_PID" 2>/dev/null; then
        kill "$AI_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

echo "Launching Flask AI Service on http://127.0.0.1:5001..."
python "$PROJECT_DIR/ai_service.py" &
AI_PID=$!
sleep 2

if ! kill -0 "$AI_PID" 2>/dev/null; then
    echo "Error: Failed to start ai_service.py."
    exit 1
fi

echo "Launching Electron + React UI..."
npm start
