#!/usr/bin/env python3
"""
Startup script for Cognivigil AI Backend
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.init_db import init_sample_data
from app.main import app
import uvicorn


async def initialize_and_start():
    """Initialize database and start server"""
    
    print("🚀 Cognivigil AI Backend Startup")
    print("=" * 50)
    
    # Check if MongoDB is running (optional for demo)
    mongodb_available = False
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        from app.core.config import settings
        
        client = AsyncIOMotorClient(settings.mongodb_url, serverSelectionTimeoutMS=3000)
        await client.admin.command('ping')
        await client.close()
        print("✅ MongoDB connection verified")
        mongodb_available = True
    except Exception as e:
        print("⚠️  MongoDB not available - running in demo mode")
        print(f"   Error: {e}")
        print("   Backend will work with demo data")
    
    # Initialize sample data only if MongoDB is available
    if mongodb_available:
        print("\n🌱 Initializing sample data...")
        try:
            await init_sample_data()
            print("✅ Sample data initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize sample data: {e}")
            print("   Continuing with server startup...")
    else:
        print("\n🌱 Skipping sample data (MongoDB not available)")
    
    print("\n🌐 Starting FastAPI server...")
    print("   Server will be available at: http://localhost:8000")
    print("   API Documentation: http://localhost:8000/docs")
    print("   Health Check: http://localhost:8000/health")
    print("\n   Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the server
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
    
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(initialize_and_start())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server failed to start: {e}")
        sys.exit(1)
