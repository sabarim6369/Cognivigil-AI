import subprocess
import time
import sys
import os

def check_mongodb_running():
    """Check if MongoDB is running"""
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=3000)
        client.admin.command('ping')
        client.close()
        return True
    except Exception as e:
        print(f"❌ MongoDB not running: {e}")
        return False

def start_mongodb():
    """Start MongoDB service"""
    print("🚀 Starting MongoDB...")
    try:
        # Try to start MongoDB as a service
        subprocess.run(["net", "start", "mongodb"], check=False, capture_output=True)
        time.sleep(3)
        return check_mongodb_running()
    except:
        try:
            # Fallback: Try to start mongod directly
            print("   Trying to start mongod directly...")
            subprocess.run(["mongod", "--dbpath", "C:/data/db"], check=False, capture_output=True)
            time.sleep(5)
            return check_mongodb_running()
        except Exception as e:
            print(f"❌ Failed to start MongoDB: {e}")
            return False

def main():
    print("🔍 MongoDB Setup for Cognivigil AI")
    print("=" * 50)
    
    if check_mongodb_running():
        print("✅ MongoDB is already running")
        return
    
    print("⚠️  MongoDB is not running")
    print("   Trying to start MongoDB...")
    
    if start_mongodb():
        print("✅ MongoDB started successfully!")
        print("   Connection: mongodb://localhost:27017")
        print("   You can now start the backend with real database")
    else:
        print("❌ Failed to start MongoDB automatically")
        print("\n📋 Manual Steps:")
        print("1. Install MongoDB Community Server")
        print("2. Run: 'mongod --dbpath C:/data/db'")
        print("3. Or use MongoDB Compass to start the service")
        print("\n🌐 Download MongoDB: https://www.mongodb.com/try/download/community")

if __name__ == "__main__":
    main()
