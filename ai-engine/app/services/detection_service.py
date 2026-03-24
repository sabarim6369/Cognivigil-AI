import asyncio
import time
from datetime import datetime
from typing import Dict, Any, List
from app.models.yolo_detector import YOLODetector
from app.models.face_tracker import FaceTracker
from app.services.risk_scorer import RiskScorer
from app.schemas.models import (
    DetectionRequest, DetectionResponse, DetectionResult, 
    FaceAnalysis, BehaviorEvent, EventType, SeverityLevel
)
from app.utils.image_processor import ImageProcessor
from app.utils.config import settings


class DetectionService:
    """Main detection orchestrator service"""
    
    def __init__(self, yolo_detector: YOLODetector, face_tracker: FaceTracker):
        self.yolo_detector = yolo_detector
        self.face_tracker = face_tracker
        self.risk_scorer = RiskScorer()
        self.image_processor = ImageProcessor()
        
        # Session state tracking
        self.session_states = {}
        self.detection_cooldowns = {}
        
    async def process_frame(self, frame_data: str, session_id: str, timestamp: str) -> DetectionResponse:
        """Process a single frame for comprehensive detection"""
        start_time = time.time()
        
        try:
            # Decode frame
            frame = await self.image_processor.decode_base64_frame(frame_data)
            
            # Preprocess frame for optimal detection
            frame = await self.image_processor.preprocess_for_detection(frame)
            
            # Run detections concurrently
            yolo_task = self.yolo_detector.detect_objects(frame)
            face_task = self.face_tracker.analyze_face(frame)
            
            # Wait for both detections
            yolo_results, face_analysis = await asyncio.gather(
                yolo_task, face_task, return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(yolo_results, Exception):
                print(f"❌ YOLO detection error: {yolo_results}")
                yolo_results = []
            
            if isinstance(face_analysis, Exception):
                print(f"❌ Face analysis error: {face_analysis}")
                face_analysis = FaceAnalysis(face_detected=False, looking_away=False, confidence=0.0)
            
            # Generate behavior events
            behavior_events = await self._generate_behavior_events(
                yolo_results, face_analysis, session_id, timestamp
            )
            
            # Calculate risk assessment
            risk_assessment = await self.risk_scorer.calculate_risk(
                yolo_results, face_analysis, behavior_events, session_id
            )
            
            # Update session state
            await self._update_session_state(session_id, yolo_results, face_analysis, timestamp)
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            return DetectionResponse(
                detections=yolo_results,
                face_analysis=face_analysis,
                behavior_events=behavior_events,
                risk_assessment=risk_assessment,
                processing_time_ms=processing_time,
                processed_at=datetime.utcnow().isoformat(),
                session_id=session_id
            )
            
        except Exception as e:
            print(f"❌ Error in frame processing: {e}")
            # Return default response
            return DetectionResponse(
                detections=[],
                face_analysis=FaceAnalysis(face_detected=False, looking_away=False, confidence=0.0),
                behavior_events=[],
                risk_assessment=await self.risk_scorer.get_default_risk_assessment(),
                processing_time_ms=0,
                processed_at=datetime.utcnow().isoformat(),
                session_id=session_id
            )
    
    async def _generate_behavior_events(
        self, 
        detections: List[DetectionResult], 
        face_analysis: FaceAnalysis,
        session_id: str, 
        timestamp: str
    ) -> List[BehaviorEvent]:
        """Generate behavior events based on detections and face analysis"""
        events = []
        
        # Phone detection event
        if settings.phone_detection_enabled:
            phone_detections = [d for d in detections if d.class_name in ['cell phone', 'phone']]
            if phone_detections and await self._check_cooldown(session_id, 'phone_detection'):
                best_phone = max(phone_detections, key=lambda x: x.confidence)
                events.append(BehaviorEvent(
                    event_type=EventType.PHONE_DETECTED,
                    confidence=best_phone.confidence,
                    severity=SeverityLevel.HIGH,
                    message="Phone detected during exam",
                    timestamp=timestamp,
                    risk_score_impact=settings.risk_phone_detection_weight,
                    metadata={
                        "bbox": best_phone.bbox,
                        "center": best_phone.center,
                        "area": best_phone.area
                    }
                ))
                await self._set_cooldown(session_id, 'phone_detection', settings.phone_detection_cooldown_seconds)
        
        # Multiple persons detection
        if settings.multiple_persons_enabled:
            person_detections = [d for d in detections if d.class_name == 'person']
            if len(person_detections) > settings.multiple_persons_max_allowed:
                events.append(BehaviorEvent(
                    event_type=EventType.MULTIPLE_PERSONS,
                    confidence=0.8,
                    severity=SeverityLevel.HIGH,
                    message=f"Multiple persons detected: {len(person_detections)}",
                    timestamp=timestamp,
                    risk_score_impact=settings.risk_multiple_persons_weight,
                    metadata={
                        "person_count": len(person_detections),
                        "detections": [{"bbox": d.bbox, "confidence": d.confidence} for d in person_detections]
                    }
                ))
        
        # Face absence event
        if settings.face_absence_enabled and not face_analysis.face_detected:
            if face_analysis.face_absence_duration > settings.face_absence_threshold_seconds:
                events.append(BehaviorEvent(
                    event_type=EventType.FACE_ABSENCE,
                    confidence=0.9,
                    severity=SeverityLevel.MEDIUM,
                    message=f"Face not detected for {face_analysis.face_absence_duration:.1f} seconds",
                    timestamp=timestamp,
                    risk_score_impact=settings.risk_face_absence_weight,
                    metadata={
                        "absence_duration": face_analysis.face_absence_duration
                    }
                ))
        
        # Looking away event
        if settings.looking_away_enabled and face_analysis.looking_away:
            if await self._check_cooldown(session_id, 'looking_away'):
                events.append(BehaviorEvent(
                    event_type=EventType.LOOKING_AWAY,
                    confidence=0.7,
                    severity=SeverityLevel.LOW,
                    message="Looking away from screen",
                    timestamp=timestamp,
                    risk_score_impact=settings.risk_looking_away_weight,
                    metadata={
                        "gaze_direction": face_analysis.gaze_direction,
                        "head_pose": face_analysis.head_pose
                    }
                ))
                await self._set_cooldown(session_id, 'looking_away', 2)  # 2 second cooldown
        
        # Suspicious objects event
        if settings.suspicious_objects_enabled:
            suspicious_classes = ['book', 'laptop', 'tablet', 'notebook', 'paper']
            suspicious_detections = [d for d in detections if d.class_name in suspicious_classes]
            if suspicious_detections:
                best_suspicious = max(suspicious_detections, key=lambda x: x.confidence)
                events.append(BehaviorEvent(
                    event_type=EventType.SUSPICIOUS_OBJECT,
                    confidence=best_suspicious.confidence,
                    severity=SeverityLevel.MEDIUM,
                    message=f"Suspicious object detected: {best_suspicious.class_name}",
                    timestamp=timestamp,
                    risk_score_impact=settings.risk_suspicious_object_weight,
                    metadata={
                        "object_type": best_suspicious.class_name,
                        "bbox": best_suspicious.bbox,
                        "confidence": best_suspicious.confidence
                    }
                ))
        
        return events
    
    async def _update_session_state(
        self, 
        session_id: str, 
        detections: List[DetectionResult], 
        face_analysis: FaceAnalysis,
        timestamp: str
    ):
        """Update session state for trend analysis"""
        if session_id not in self.session_states:
            self.session_states[session_id] = {
                "detection_history": [],
                "risk_scores": [],
                "event_count": 0,
                "start_time": timestamp
            }
        
        state = self.session_states[session_id]
        
        # Add to history (keep last 100 detections)
        state["detection_history"].append({
            "timestamp": timestamp,
            "detections": len(detections),
            "face_detected": face_analysis.face_detected,
            "looking_away": face_analysis.looking_away
        })
        
        if len(state["detection_history"]) > 100:
            state["detection_history"].pop(0)
    
    async def _check_cooldown(self, session_id: str, event_type: str) -> bool:
        """Check if event is in cooldown period"""
        key = f"{session_id}_{event_type}"
        if key not in self.detection_cooldowns:
            return True
        
        cooldown_end = self.detection_cooldowns[key]
        return time.time() > cooldown_end
    
    async def _set_cooldown(self, session_id: str, event_type: str, seconds: int):
        """Set cooldown for event type"""
        key = f"{session_id}_{event_type}"
        self.detection_cooldowns[key] = time.time() + seconds
    
    async def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get session summary statistics"""
        if session_id not in self.session_states:
            return {"error": "Session not found"}
        
        state = self.session_states[session_id]
        
        return {
            "session_id": session_id,
            "start_time": state["start_time"],
            "total_frames": len(state["detection_history"]),
            "event_count": state["event_count"],
            "average_risk_score": sum(state["risk_scores"]) / len(state["risk_scores"]) if state["risk_scores"] else 0,
            "detection_rate": sum(1 for d in state["detection_history"] if d["detections"] > 0) / len(state["detection_history"]) if state["detection_history"] else 0
        }
    
    async def clear_session_state(self, session_id: str):
        """Clear session state"""
        if session_id in self.session_states:
            del self.session_states[session_id]
        
        # Clear related cooldowns
        keys_to_remove = [key for key in self.detection_cooldowns.keys() if key.startswith(f"{session_id}_")]
        for key in keys_to_remove:
            del self.detection_cooldowns[key]
