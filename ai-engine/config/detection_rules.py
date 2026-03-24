"""
Detection Rules Configuration

This file contains all configurable rules for the AI detection system.
Modify these settings to adjust detection sensitivity and behavior.
"""

# Main detection rules configuration
DETECTION_RULES = {
    "phone_detection": {
        "enabled": True,
        "weight": 50,
        "confidence_threshold": 0.7,
        "cooldown_seconds": 5,
        "target_classes": ["cell phone", "phone"],
        "description": "Detect mobile phone usage during exam"
    },
    
    "multiple_persons": {
        "enabled": True,
        "weight": 70,
        "confidence_threshold": 0.8,
        "max_persons": 1,
        "description": "Detect if more than allowed persons are present"
    },
    
    "face_absence": {
        "enabled": True,
        "weight": 30,
        "absence_threshold_seconds": 3,
        "critical_threshold_seconds": 10,
        "description": "Detect when student's face is not visible"
    },
    
    "looking_away": {
        "enabled": True,
        "weight": 10,
        "angle_threshold": 45,
        "duration_threshold": 2,
        "cooldown_seconds": 2,
        "description": "Detect when student looks away from screen"
    },
    
    "suspicious_objects": {
        "enabled": True,
        "weight": 20,
        "target_classes": ["book", "laptop", "tablet", "notebook", "paper"],
        "max_objects": 3,
        "description": "Detect potentially unauthorized objects"
    }
}

# Risk scoring configuration
RISK_SCORING = {
    "thresholds": {
        "low": 25,
        "medium": 50,
        "high": 75,
        "critical": 100
    },
    
    "modifiers": {
        "low_face_confidence": 10,
        "multiple_suspicious_objects": 15,
        "extended_face_absence": 20,
        "high_confidence_detections": 10
    },
    
    "trend_analysis": {
        "history_length": 50,
        "trend_window": 3,
        "significant_change": 15
    }
}

# YOLO detection configuration
YOLO_CONFIG = {
    "model_path": "./models/yolov8n.pt",
    "target_classes": [
        "person", "cell phone", "book", "laptop", "mouse", 
        "phone", "tablet", "notebook", "paper", "monitor"
    ],
    "confidence_threshold": 0.5,
    "nms_threshold": 0.4,
    "input_size": [640, 640],
    "max_detections": 100
}

# Face tracking configuration
FACE_TRACKING_CONFIG = {
    "max_faces": 1,
    "min_detection_confidence": 0.5,
    "min_tracking_confidence": 0.5,
    "refine_landmarks": True,
    
    # Gaze detection
    "looking_away_angle_threshold": 45,
    "gaze_sensitivity": 0.3,
    
    # Face absence
    "face_absence_threshold_seconds": 3,
    "critical_absence_threshold_seconds": 10,
    
    # Head pose
    "head_pose_sensitivity": 0.2,
    "rotation_threshold": 30
}

# Performance optimization settings
PERFORMANCE_CONFIG = {
    "max_batch_size": 10,
    "processing_timeout_seconds": 30,
    "enable_gpu_acceleration": True,
    "frame_skip_threshold": 30,  # Skip processing if FPS > threshold
    "memory_limit_mb": 4096,
    
    # Model optimization
    "model_precision": "fp16",  # fp16, fp32
    "enable_tensorrt": False,  # Requires TensorRT
    "optimize_for_speed": True
}

# Logging and monitoring
LOGGING_CONFIG = {
    "level": "INFO",
    "log_detections": True,
    "log_risk_scores": True,
    "log_performance_metrics": True,
    "save_evidence_frames": False,
    "max_log_size_mb": 100,
    "log_retention_days": 7
}

# Evidence collection
EVIDENCE_CONFIG = {
    "save_suspicious_frames": True,
    "save_high_risk_frames": True,
    "evidence_storage_path": "./evidence",
    "max_evidence_per_session": 50,
    "compression_quality": 85,
    "include_metadata": True
}

# Session management
SESSION_CONFIG = {
    "max_session_duration_hours": 4,
    "session_timeout_minutes": 30,
    "cleanup_interval_minutes": 60,
    "max_concurrent_sessions": 100
}

# API configuration
API_CONFIG = {
    "rate_limit_per_minute": 60,
    "max_request_size_mb": 10,
    "enable_cors": True,
    "allowed_origins": [
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://localhost:8000"
    ],
    "api_key_required": False,
    "enable_metrics": True
}

# Development and testing
DEV_CONFIG = {
    "debug_mode": True,
    "mock_ai_models": False,
    "save_test_frames": False,
    "enable_profiling": False,
    "test_data_path": "./test_data"
}

# Production overrides
PRODUCTION_OVERRIDES = {
    "debug_mode": False,
    "log_level": "WARNING",
    "enable_profiling": False,
    "save_test_frames": False,
    "api_key_required": True,
    "enable_tensorrt": True
}

def get_detection_config(rule_name: str) -> dict:
    """Get specific detection rule configuration"""
    return DETECTION_RULES.get(rule_name, {})

def is_rule_enabled(rule_name: str) -> bool:
    """Check if a detection rule is enabled"""
    return DETECTION_RULES.get(rule_name, {}).get("enabled", False)

def get_risk_threshold(level: str) -> int:
    """Get risk threshold for a given level"""
    return RISK_SCORING["thresholds"].get(level, 50)

def apply_environment_overrides(config: dict, environment: str = "development"):
    """Apply environment-specific configuration overrides"""
    if environment == "production":
        config.update(PRODUCTION_OVERRIDES)
    elif environment == "development":
        config.update(DEV_CONFIG)
    
    return config

# Export main configuration
MAIN_CONFIG = {
    "detection_rules": DETECTION_RULES,
    "risk_scoring": RISK_SCORING,
    "yolo": YOLO_CONFIG,
    "face_tracking": FACE_TRACKING_CONFIG,
    "performance": PERFORMANCE_CONFIG,
    "logging": LOGGING_CONFIG,
    "evidence": EVIDENCE_CONFIG,
    "session": SESSION_CONFIG,
    "api": API_CONFIG,
    "development": DEV_CONFIG
}
