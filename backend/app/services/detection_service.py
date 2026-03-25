import base64
import requests
from datetime import datetime
from typing import List, Dict, Any
from app.core.config import settings
from app.models.schemas import DetectionResult, FrameProcessResponse, EventType


class DetectionService:
    def __init__(self):
        self.ai_engine_url = settings.ai_engine_url
        self.risk_weights = {
            'cell phone': 50,
            'multiple_persons': 70,
            'face_absence': 30,
            'looking_away': 10,
            'suspicious_object': 20
        }
        
    async def initialize_models(self):
        """Check if AI Engine is available"""
        try:
            response = requests.get(f"{self.ai_engine_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ AI Engine service is available")
                return True
            else:
                print("❌ AI Engine service is not healthy")
                return False
        except Exception as e:
            print(f"❌ AI Engine service not available: {e}")
            print("   Please start the AI Engine service on port 8001")
            return False
    
    async def process_frame(self, frame_data: str, session_id: str) -> FrameProcessResponse:
        """Process a single frame and return detection results"""
        try:
            # Send frame to AI Engine service
            payload = {
                "frame": frame_data,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = requests.post(
                f"{self.ai_engine_url}/detect",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Convert AI Engine response to our format
                detections = [
                    DetectionResult(
                        class_name=d["class_name"],
                        confidence=d["confidence"],
                        bbox=d["bbox"],
                        center=d["center"]
                    ) for d in result.get("detections", [])
                ]
                
                # Handle alerts from AI engine (format may vary)
                alerts = []
                ai_alerts = result.get("alerts", [])
                if ai_alerts:
                    for alert in ai_alerts:
                        alerts.append({
                            "type": alert.get("type", "unknown"),
                            "message": alert.get("message", "Suspicious activity detected"),
                            "confidence": alert.get("confidence", 0.5),
                            "severity": alert.get("severity", "medium")
                        })
                
                # Get risk score from AI engine response
                risk_score = result.get("risk_score", 0)
                
                return FrameProcessResponse(
                    detections=detections,
                    risk_score=risk_score,
                    alerts=alerts,
                    processed_at=datetime.utcnow()
                )
            else:
                print(f"❌ AI Engine returned error: {response.status_code}")
                print(f"Response: {response.text}")
                # Return dummy response
                return FrameProcessResponse(
                    detections=[],
                    risk_score=0,
                    alerts=[],
                    processed_at=datetime.utcnow()
                )
            
        except Exception as e:
            print(f"❌ Error processing frame: {e}")
            print("   Falling back to dummy response")
            # Return dummy response for demo
            return FrameProcessResponse(
                detections=[],
                risk_score=0,
                alerts=[],
                processed_at=datetime.utcnow()
            )


# Global detection service instance
detection_service = DetectionService()
