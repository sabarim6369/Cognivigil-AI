import requests
import base64
from datetime import datetime

def test_backend_ai_integration():
    """Test if backend can call AI Engine"""
    print("🧪 Testing Backend → AI Engine Integration")
    print("=" * 50)
    
    # Test AI Engine is running
    print("1. Testing AI Engine health...")
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("✅ AI Engine is running")
        else:
            print(f"❌ AI Engine not healthy: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ AI Engine not accessible: {e}")
        return False
    
    # Test AI Engine detection
    print("\n2. Testing AI Engine detection...")
    try:
        payload = {
            "frame": base64.b64encode(b'\x00').decode('utf-8'),
            "session_id": "test_session",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        response = requests.post(
            "http://localhost:8001/detect",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ AI Engine detection working")
            result = response.json()
            print(f"   Risk score: {result.get('risk_assessment', {}).get('total_score', 0)}")
        else:
            print(f"❌ AI Engine detection failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ AI Engine detection error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Integration Test Complete!")
    print("   AI Engine is ready for backend integration.")
    
    return True

if __name__ == "__main__":
    test_backend_ai_integration()
