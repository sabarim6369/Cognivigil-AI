import cv2
import numpy as np
import base64
from datetime import datetime
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ultralytics import YOLO
import mediapipe as mp
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


class DetectionResponse(BaseModel):
    detections: List[DetectionResult]
    risk_score: int
    alerts: List[Dict[str, Any]]
    processed_at: str


# Initialize FastAPI app
app = FastAPI(
    title="AI Engine",
    description="AI processing service for Cognivigil",
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


class AIEngineService:
    def __init__(self):
        self.yolo_model = None
        self.face_mesh = None
        self.target_classes = ['person', 'cell phone', 'book', 'laptop', 'mouse']
        self.risk_weights = {
            'cell phone': 50,
            'multiple_persons': 70,
            'face_absence': 30,
            'looking_away': 10,
            'suspicious_object': 20
        }
        self.models_loaded = False
        
    def initialize_models(self):
        """Initialize AI models"""
        try:
            # Initialize YOLO model
            self.yolo_model = YOLO("models/yolov8n.pt")
            
            # Initialize MediaPipe Face Mesh
            self.face_mesh = mp.solutions.face_mesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            
            self.models_loaded = True
            print("✅ AI models initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Error initializing AI models: {e}")
            return False
    
    def decode_frame(self, frame_data: str) -> np.ndarray:
        """Decode base64 frame to numpy array"""
        try:
            # Remove data URL prefix if present
            if ',' in frame_data:
                frame_data = frame_data.split(',')[1]
            
            # Decode base64
            decoded = base64.b64decode(frame_data)
            
            # Convert to numpy array
            nparr = np.frombuffer(decoded, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            return frame
        except Exception as e:
            print(f"❌ Error decoding frame: {e}")
            # Return dummy frame for demo
            return np.zeros((480, 640, 3), dtype=np.uint8)
    
    def detect_objects(self, frame: np.ndarray) -> List[DetectionResult]:
        """Detect objects using YOLO"""
        try:
            if not self.models_loaded or self.yolo_model is None:
                return []
            
            results = self.yolo_model(frame, conf=0.5)
            detections = []
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        cls_id = int(box.cls[0])
                        class_name = self.yolo_model.names[cls_id]
                        confidence = float(box.conf[0])
                        bbox = box.xyxy[0].cpu().numpy().tolist()
                        
                        # Filter for target classes
                        if class_name in self.target_classes:
                            detections.append(DetectionResult(
                                class_name=class_name,
                                confidence=confidence,
                                bbox=bbox,
                                center=self.get_bbox_center(bbox)
                            ))
            
            return detections
            
        except Exception as e:
            print(f"❌ Error in object detection: {e}")
            return []
    
    def analyze_face(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analyze face using MediaPipe"""
        try:
            if not self.models_loaded or self.face_mesh is None:
                return {"face_detected": False, "looking_away": False}
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            
            if results.multi_face_landmarks:
                # Face detected
                landmarks = results.multi_face_landmarks[0]
                looking_away = self.check_looking_away(landmarks)
                
                return {
                    "face_detected": True,
                    "looking_away": looking_away,
                    "landmarks": landmarks
                }
            else:
                return {"face_detected": False, "looking_away": False}
                
        except Exception as e:
            print(f"❌ Error in face analysis: {e}")
            return {"face_detected": False, "looking_away": False}
    
    def get_bbox_center(self, bbox: List[float]) -> List[float]:
        """Calculate center point of bounding box"""
        x1, y1, x2, y2 = bbox
        return [(x1 + x2) / 2, (y1 + y2) / 2]
    
    def check_looking_away(self, landmarks) -> bool:
        """Check if person is looking away from camera"""
        try:
            # Get eye landmarks
            left_eye = landmarks.landmark[33]  # Left eye corner
            right_eye = landmarks.landmark[263]  # Right eye corner
            nose = landmarks.landmark[1]  # Nose tip
            
            # Calculate eye center
            eye_center_x = (left_eye.x + right_eye.x) / 2
            
            # Check if nose is significantly offset from eye center
            nose_offset = abs(nose.x - eye_center_x)
            
            # If nose is offset by more than 0.05, consider as looking away
            return nose_offset > 0.05
            
        except Exception:
            return False
    
    def calculate_risk_score(
        self, 
        detections: List[DetectionResult], 
        face_analysis: Dict[str, Any]
    ) -> tuple[int, List[Dict[str, Any]]]:
        """Calculate risk score and generate alerts"""
        risk_score = 0
        alerts = []
        
        # Check for phone detection
        phones = [d for d in detections if d.class_name == 'cell phone']
        if phones:
            risk_score += self.risk_weights['cell phone']
            alerts.append({
                "type": "phone_detected",
                "message": "Phone detected",
                "confidence": max(p.confidence for p in phones),
                "severity": "high"
            })
        
        # Check for multiple persons
        persons = [d for d in detections if d.class_name == 'person']
        if len(persons) > 1:
            risk_score += self.risk_weights['multiple_persons']
            alerts.append({
                "type": "multiple_persons",
                "message": f"Multiple persons detected: {len(persons)}",
                "confidence": 0.8,
                "severity": "high"
            })
        
        # Check face presence
        if not face_analysis.get("face_detected"):
            risk_score += self.risk_weights['face_absence']
            alerts.append({
                "type": "face_absence",
                "message": "Face not detected",
                "confidence": 0.9,
                "severity": "medium"
            })
        
        # Check if looking away
        if face_analysis.get("looking_away"):
            risk_score += self.risk_weights['looking_away']
            alerts.append({
                "type": "looking_away",
                "message": "Looking away from screen",
                "confidence": 0.7,
                "severity": "low"
            })
        
        # Check for suspicious objects
        suspicious_objects = [d for d in detections if d.class_name in ['book', 'laptop']]
        if suspicious_objects:
            risk_score += self.risk_weights['suspicious_object']
            alerts.append({
                "type": "suspicious_object",
                "message": f"Suspicious object detected: {suspicious_objects[0].class_name}",
                "confidence": suspicious_objects[0].confidence,
                "severity": "medium"
            })
        
        return risk_score, alerts


# Initialize AI service
ai_service = AIEngineService()


@app.on_event("startup")
async def startup_event():
    """Initialize AI models on startup"""
    ai_service.initialize_models()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "models_loaded": ai_service.models_loaded,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/detect", response_model=DetectionResponse)
async def detect_objects(request: DetectionRequest):
    """Process frame for object detection and risk assessment"""
    try:
        # Decode frame
        frame = ai_service.decode_frame(request.frame)
        
        # Run detections
        detections = ai_service.detect_objects(frame)
        face_analysis = ai_service.analyze_face(frame)
        
        # Calculate risk score and alerts
        risk_score, alerts = ai_service.calculate_risk_score(detections, face_analysis)
        
        return DetectionResponse(
            detections=detections,
            risk_score=risk_score,
            alerts=alerts,
            processed_at=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        print(f"❌ Error in detection: {e}")
        raise HTTPException(status_code=500, detail="Detection failed")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
