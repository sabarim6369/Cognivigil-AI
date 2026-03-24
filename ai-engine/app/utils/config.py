import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Model paths
    models_path: str = "./models"
    yolo_model_path: str = "./models/yolov8n.pt"
    
    # YOLO Configuration
    yolo_target_classes: List[str] = [
        "person", "cell phone", "book", "laptop", "mouse", 
        "phone", "tablet", "notebook", "paper"
    ]
    yolo_confidence_threshold: float = 0.5
    yolo_nms_threshold: float = 0.4
    
    # Face Tracking Configuration
    face_max_faces: int = 1
    face_min_detection_confidence: float = 0.5
    face_min_tracking_confidence: float = 0.5
    face_looking_away_angle_threshold: float = 45.0
    face_absence_threshold_seconds: float = 3.0
    
    # Risk Scoring Weights
    risk_phone_detection_weight: int = 50
    risk_multiple_persons_weight: int = 70
    risk_face_absence_weight: int = 30
    risk_looking_away_weight: int = 10
    risk_suspicious_object_weight: int = 20
    
    # Risk Thresholds
    risk_threshold_low: int = 25
    risk_threshold_medium: int = 50
    risk_threshold_high: int = 75
    
    # Detection Rules
    phone_detection_enabled: bool = True
    phone_detection_cooldown_seconds: int = 5
    multiple_persons_enabled: bool = True
    multiple_persons_max_allowed: int = 1
    face_absence_enabled: bool = True
    looking_away_enabled: bool = True
    suspicious_objects_enabled: bool = True
    
    # Performance Settings
    max_batch_size: int = 10
    processing_timeout_seconds: int = 30
    enable_gpu_acceleration: bool = True
    
    # Application Settings
    debug: bool = True
    log_level: str = "info"
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }


# Global settings instance
settings = Settings()
