import asyncio
import cv2
import numpy as np
from typing import List, Dict, Any, Optional
from ultralytics import YOLO
from app.schemas.models import DetectionResult
from app.utils.config import settings


class YOLODetector:
    def __init__(self):
        self.model = None
        self.model_path = settings.yolo_model_path
        self.target_classes = settings.yolo_target_classes
        self.confidence_threshold = settings.yolo_confidence_threshold
        self.loaded = False
        self.model_lock = asyncio.Lock()
        
    async def initialize(self):
        """Initialize YOLO model"""
        async with self.model_lock:
            if self.loaded:
                return True
                
            try:
                print(f"🤖 Loading YOLO model from {self.model_path}")
                
                # Load model in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                self.model = await loop.run_in_executor(
                    None, 
                    lambda: YOLO(self.model_path)
                )
                
                self.loaded = True
                print(f"✅ YOLO model loaded successfully")
                print(f"   Target classes: {self.target_classes}")
                print(f"   Confidence threshold: {self.confidence_threshold}")
                
                return True
                
            except Exception as e:
                print(f"❌ Error loading YOLO model: {e}")
                self.loaded = False
                return False
    
    async def detect_objects(self, frame: np.ndarray) -> List[DetectionResult]:
        """Detect objects in frame using YOLO"""
        if not self.loaded or self.model is None:
            print("⚠️ YOLO model not loaded, returning empty detections")
            return []
        
        try:
            # Run inference in thread pool
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                lambda: self.model(frame, conf=self.confidence_threshold)
            )
            
            detections = []
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        cls_id = int(box.cls[0])
                        class_name = self.model.names[cls_id]
                        confidence = float(box.conf[0])
                        bbox = box.xyxy[0].cpu().numpy().tolist()
                        
                        # Filter for target classes
                        if class_name in self.target_classes:
                            # Calculate area and center
                            x1, y1, x2, y2 = bbox
                            area = (x2 - x1) * (y2 - y1)
                            center = [(x1 + x2) / 2, (y1 + y2) / 2]
                            
                            detection = DetectionResult(
                                class_name=class_name,
                                confidence=confidence,
                                bbox=bbox,
                                center=center,
                                area=area,
                                timestamp=None
                            )
                            detections.append(detection)
            
            return detections
            
        except Exception as e:
            print(f"❌ Error in YOLO detection: {e}")
            return []
    
    async def detect_persons(self, frame: np.ndarray) -> List[DetectionResult]:
        """Specifically detect persons"""
        person_detections = []
        all_detections = await self.detect_objects(frame)
        
        for detection in all_detections:
            if detection.class_name == 'person':
                person_detections.append(detection)
        
        return person_detections
    
    async def detect_phones(self, frame: np.ndarray) -> List[DetectionResult]:
        """Specifically detect phones"""
        phone_detections = []
        all_detections = await self.detect_objects(frame)
        
        for detection in all_detections:
            if detection.class_name in ['cell phone', 'phone']:
                phone_detections.append(detection)
        
        return phone_detections
    
    async def detect_suspicious_objects(self, frame: np.ndarray) -> List[DetectionResult]:
        """Detect suspicious objects (books, laptops, etc.)"""
        suspicious_classes = ['book', 'laptop', 'tablet', 'notebook', 'paper']
        suspicious_detections = []
        all_detections = await self.detect_objects(frame)
        
        for detection in all_detections:
            if detection.class_name in suspicious_classes:
                suspicious_detections.append(detection)
        
        return suspicious_detections
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.loaded and self.model is not None
    
    async def cleanup(self):
        """Cleanup resources"""
        async with self.model_lock:
            if self.model is not None:
                del self.model
                self.model = None
            self.loaded = False
            print("🧹 YOLO detector cleaned up")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        if not self.loaded:
            return {"loaded": False}
        
        return {
            "loaded": True,
            "model_path": self.model_path,
            "target_classes": self.target_classes,
            "confidence_threshold": self.confidence_threshold,
            "model_names": list(self.model.names.values()) if self.model else []
        }
