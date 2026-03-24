from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    PHONE_DETECTED = "phone_detected"
    MULTIPLE_PERSONS = "multiple_persons"
    FACE_ABSENCE = "face_absence"
    LOOKING_AWAY = "looking_away"
    SUSPICIOUS_OBJECT = "suspicious_object"
    FACE_MOVEMENT = "face_movement"
    EYE_TRACKING = "eye_tracking"


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DetectionResult(BaseModel):
    class_name: str
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]
    center: List[float]  # [x, y]
    area: Optional[float] = None
    timestamp: Optional[str] = None


class FaceLandmark(BaseModel):
    x: float
    y: float
    z: Optional[float] = None


class FaceAnalysis(BaseModel):
    face_detected: bool
    landmarks: Optional[List[FaceLandmark]] = None
    gaze_direction: Optional[Dict[str, float]] = None
    head_pose: Optional[Dict[str, float]] = None
    looking_away: bool = False
    face_absence_duration: float = 0.0
    confidence: float = 0.0


class BehaviorEvent(BaseModel):
    event_type: EventType
    confidence: float
    severity: SeverityLevel
    message: str
    timestamp: str
    risk_score_impact: int
    metadata: Dict[str, Any] = {}


class RiskAssessment(BaseModel):
    total_score: int
    risk_level: SeverityLevel
    breakdown: Dict[str, int]
    trend: str  # "increasing", "decreasing", "stable"
    recommendations: List[str]


class DetectionRequest(BaseModel):
    frame: str  # Base64 encoded image
    session_id: str
    timestamp: str
    frame_number: Optional[int] = None


class DetectionResponse(BaseModel):
    detections: List[DetectionResult]
    face_analysis: FaceAnalysis
    behavior_events: List[BehaviorEvent]
    risk_assessment: RiskAssessment
    processing_time_ms: float
    processed_at: str
    session_id: str


class BatchDetectionRequest(BaseModel):
    requests: List[DetectionRequest]
    batch_id: Optional[str] = None


class BatchDetectionResponse(BaseModel):
    results: List[DetectionResponse]
    batch_id: str
    total_processing_time_ms: float
    processed_at: str


class ModelStatus(BaseModel):
    model_name: str
    loaded: bool
    model_path: str
    version: str
    last_loaded: Optional[str] = None
    performance_stats: Dict[str, Any] = {}


class HealthResponse(BaseModel):
    status: str
    models: Dict[str, ModelStatus]
    system_info: Dict[str, Any]
    uptime_seconds: float
    memory_usage_mb: float
