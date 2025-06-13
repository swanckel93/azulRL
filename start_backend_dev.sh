#!/bin/bash

# Azul Game - Backend Development Server Starter
# This script starts the FastAPI backend server for development

echo "🎮 Starting Azul Game Backend Server..."
echo "📍 Server will be available at:"
echo "   - Local: http://localhost:8000"
echo "   - Network: http://0.0.0.0:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""

# Navigate to the project root directory (where src/ is located)
cd "$(dirname "$0")"

# Check if virtual environment exists and activate it
if [ -d ".venv" ]; then
    echo "🔧 Activating virtual environment..."
    source .venv/bin/activate
else
    echo "⚠️  Warning: No .venv directory found. Make sure you have the virtual environment set up."
fi

# Check if required packages are installed
if ! python -c "import uvicorn" &> /dev/null; then
    echo "❌ Error: uvicorn not found. Please install dependencies with:"
    echo "   poetry install"
    exit 1
fi

echo "🚀 Starting backend server with auto-reload..."
echo "💡 Press Ctrl+C to stop the server"
echo ""

# Start the backend server
python -m uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000