import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models.yolo_detector import YOLODetector
from app.models.face_tracker import FaceTracker
from app.services.detection_service import DetectionService
from app.schemas.models import DetectionRequest, DetectionResponse
from app.utils.config import settings

# Initialize AI components
yolo_detector = YOLODetector()
face_tracker = FaceTracker()
detection_service = DetectionService(yolo_detector, face_tracker)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🤖 Starting Cognivigil AI Engine...")
    
    # Initialize models
    await yolo_detector.initialize()
    await face_tracker.initialize()
    
    print("✅ AI Engine startup complete!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down AI Engine...")
    await yolo_detector.cleanup()
    await face_tracker.cleanup()
    print("✅ AI Engine shutdown complete!")


# Create FastAPI app
app = FastAPI(
    title="Cognivigil AI Engine",
    description="AI processing service for exam proctoring",
    version="1.0.0",
    lifespan=lifespan
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
        "yolo_loaded": yolo_detector.is_loaded(),
        "face_tracker_loaded": face_tracker.is_loaded(),
        "models_path": settings.models_path,
        "timestamp": asyncio.get_event_loop().time()
    }


@app.get("/models/status")
async def models_status():
    """Get detailed model status"""
    return {
        "yolo": {
            "loaded": yolo_detector.is_loaded(),
            "model_path": yolo_detector.model_path,
            "target_classes": yolo_detector.target_classes
        },
        "face_tracker": {
            "loaded": face_tracker.is_loaded(),
            "max_faces": face_tracker.max_faces,
            "min_detection_confidence": face_tracker.min_detection_confidence
        }
    }


@app.post("/detect", response_model=DetectionResponse)
async def detect_objects(request: DetectionRequest):
    """Process frame for object detection and behavioral analysis"""
    try:
        result = await detection_service.process_frame(
            frame_data=request.frame,
            session_id=request.session_id,
            timestamp=request.timestamp
        )
        return result
        
    except Exception as e:
        print(f"❌ Error in detection: {e}")
        raise HTTPException(status_code=500, detail="Detection failed")


@app.post("/detect/batch")
async def detect_batch(requests: list[DetectionRequest]):
    """Process multiple frames in batch"""
    try:
        results = []
        for req in requests:
            result = await detection_service.process_frame(
                frame_data=req.frame,
                session_id=req.session_id,
                timestamp=req.timestamp
            )
            results.append(result)
        
        return {"results": results, "processed_count": len(results)}
        
    except Exception as e:
        print(f"❌ Error in batch detection: {e}")
        raise HTTPException(status_code=500, detail="Batch detection failed")


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Cognivigil AI Engine")
    print("=" * 50)
    print("   AI Processing Microservice")
    print("   YOLOv8 + MediaPipe + Behavioral Analysis")
    print("=" * 50)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.debug,
        log_level="info"
    )
