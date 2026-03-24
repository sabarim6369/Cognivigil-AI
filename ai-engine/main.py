import base64
import random
from datetime import datetime
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


# Pydantic models
class DetectionRequest(BaseModel):
    frame: str
    session_id: str
    timestamp: str


class DetectionResult(BaseModel):
    class_name: str
    confidence: float
    bbox: List[float]
    center: List[float]


class FaceAnalysis(BaseModel):
    face_detected: bool
    looking_away: bool
    confidence: float


class BehaviorEvent(BaseModel):
    event_type: str
    confidence: float
    severity: str
    message: str
    timestamp: str
    risk_score_impact: int


class RiskAssessment(BaseModel):
    total_score: int
    risk_level: str
    breakdown: Dict[str, int]
    trend: str
    recommendations: List[str]


class DetectionResponse(BaseModel):
    detections: List[DetectionResult]
    face_analysis: FaceAnalysis
    behavior_events: List[BehaviorEvent]
    risk_assessment: RiskAssessment
    processing_time_ms: float
    processed_at: str
    session_id: str


# Initialize FastAPI app
app = FastAPI(
    title="Cognivigil AI Engine - Demo",
    description="AI processing service for exam proctoring (Demo Mode)",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "models_loaded": False,
        "mode": "demo",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/models/status")
async def models_status():
    """Get model status"""
    return {
        "yolo": {
            "loaded": False,
            "model_path": "demo_mode",
            "target_classes": ["person", "cell phone", "book", "laptop"]
        },
        "face_tracker": {
            "loaded": False,
            "max_faces": 1,
            "min_detection_confidence": 0.5
        }
    }


@app.post("/detect", response_model=DetectionResponse)
async def detect_objects(request: DetectionRequest):
    """Demo detection with simulated results"""
    try:
        import time
        start_time = time.time()
        
        # Simulate random detections
        detections = []
        behavior_events = []
        
        # Random chance of detecting person
        if random.random() > 0.3:
            detections.append(DetectionResult(
                class_name="person",
                confidence=0.85,
                bbox=[100, 100, 300, 400],
                center=[200, 250]
            ))
        
        # Random chance of detecting phone
        if random.random() > 0.9:
            detections.append(DetectionResult(
                class_name="cell phone",
                confidence=0.75,
                bbox=[50, 50, 150, 200],
                center=[100, 125]
            ))
            behavior_events.append(BehaviorEvent(
                event_type="phone_detected",
                confidence=0.75,
                severity="high",
                message="Phone detected",
                timestamp=datetime.utcnow().isoformat(),
                risk_score_impact=50
            ))
        
        # Random chance of looking away
        if random.random() > 0.8:
            behavior_events.append(BehaviorEvent(
                event_type="looking_away",
                confidence=0.7,
                severity="low",
                message="Looking away from screen",
                timestamp=datetime.utcnow().isoformat(),
                risk_score_impact=10
            ))
        
        # Calculate risk
        risk_score = sum(event.risk_score_impact for event in behavior_events)
        risk_level = "low"
        if risk_score > 75:
            risk_level = "critical"
        elif risk_score > 50:
            risk_level = "high"
        elif risk_score > 25:
            risk_level = "medium"
        
        risk_assessment = RiskAssessment(
            total_score=risk_score,
            risk_level=risk_level,
            breakdown={"phone_detection": 50 if any(e.event_type == "phone_detected" for e in behavior_events) else 0},
            trend="stable",
            recommendations=["Continue monitoring" if risk_level == "low" else "Increase attention"]
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        return DetectionResponse(
            detections=detections,
            face_analysis=FaceAnalysis(
                face_detected=True,
                looking_away=random.random() > 0.8,
                confidence=0.9
            ),
            behavior_events=behavior_events,
            risk_assessment=risk_assessment,
            processing_time_ms=processing_time,
            processed_at=datetime.utcnow().isoformat(),
            session_id=request.session_id
        )
        
    except Exception as e:
        print(f"❌ Error in detection: {e}")
        raise HTTPException(status_code=500, detail="Detection failed")


if __name__ == "__main__":
    import uvicorn
    print("🚀 Cognivigil AI Engine")
    print("   AI Processing Microservice for Exam Proctoring")
    print("   Mode: Demo (simulated detections)")
    print("   Server: http://localhost:8001")
    print("   API Docs: http://localhost:8001/docs")
    print("=" * 50)
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False)
