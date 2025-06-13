#!/usr/bin/env python3
"""
Convenience script to start the Azul backend server
"""
import uvicorn

def main():
    uvicorn.run(
        "src.backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()