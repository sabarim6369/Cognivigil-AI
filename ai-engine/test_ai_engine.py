import requests
import base64
import json
from datetime import datetime

def test_ai_engine():
    """Test AI Engine endpoints"""
    base_url = "http://localhost:8001"
    
    print("🧪 Testing Cognivigil AI Engine")
    print("=" * 50)
    
    # Test 1: Health Check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Model Status
    print("\n2. Testing model status...")
    try:
        response = requests.get(f"{base_url}/models/status")
        if response.status_code == 200:
            print("✅ Model status check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Model status check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Model status error: {e}")
    
    # Test 3: Detection API
    print("\n3. Testing detection API...")
    try:
        # Create a simple test frame (1x1 pixel)
        test_frame = base64.b64encode(b'\x00').decode('utf-8')
        
        payload = {
            "frame": test_frame,
            "session_id": "test_session_123",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        response = requests.post(
            f"{base_url}/detect",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Detection API test passed")
            result = response.json()
            print(f"   Session ID: {result.get('session_id')}")
            print(f"   Processing time: {result.get('processing_time_ms')} ms")
            print(f"   Risk score: {result.get('risk_assessment', {}).get('total_score')}")
            print(f"   Detections: {len(result.get('detections', []))}")
        else:
            print(f"❌ Detection API test failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Detection API error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 AI Engine Test Complete!")
    print("   If all tests passed, the AI Engine is ready for integration.")

if __name__ == "__main__":
    test_ai_engine()
