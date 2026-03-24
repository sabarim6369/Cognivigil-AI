#!/usr/bin/env python3
"""
Simple server startup for Cognivigil AI Backend
"""

import sys
import os
import uvicorn

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import app

def main():
    print("🚀 Cognivigil AI Backend - Simple Startup")
    print("=" * 50)
    print("   Server: http://localhost:8000")
    print("   AI Engine Integration: Enabled")
    print("   MongoDB: Auto-connect through app")
    print("   API Docs: http://localhost:8000/docs")
    print("=" * 50)
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
