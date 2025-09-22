#!/usr/bin/env python3
"""
Script to run the FastAPI server on port 2004
"""
import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=2004,
        reload=True
    )
