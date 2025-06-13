#!/usr/bin/env python3
"""
Azul Game Server
Run this script to start the FastAPI backend server
"""

import sys
import os

# Add src to Python path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.backend.main import app
import uvicorn

if __name__ == "__main__":
    print("🎮 Starting Azul Game Server...")
    print("📡 API will be available at: http://localhost:8000")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    print("🔗 WebSocket endpoint: ws://localhost:8000/sessions/{session_id}/ws")
    print()
    
    uvicorn.run(
        "src.backend.main:app",
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )