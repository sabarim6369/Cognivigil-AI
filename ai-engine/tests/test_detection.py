import pytest
import asyncio
import base64
import numpy as np
from datetime import datetime
from app.models.yolo_detector import YOLODetector
from app.models.face_tracker import FaceTracker
from app.services.detection_service import DetectionService
from app.services.risk_scorer import RiskScorer
from app.schemas.models import DetectionRequest, EventType
from app.utils.image_processor import ImageProcessor


class TestImageProcessor:
    """Test image processing utilities"""
    
    @pytest.mark.asyncio
    async def test_decode_base64_frame(self):
        """Test base64 frame decoding"""
        # Create a simple test image
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Encode to base64
        success, encoded = cv2.imencode('.jpg', test_frame)
        assert success
        
        base64_data = base64.b64encode(encoded).decode('utf-8')
        
        # Test decoding
        decoded_frame = await ImageProcessor.decode_base64_frame(base64_data)
        assert decoded_frame is not None
        assert decoded_frame.shape == (480, 640, 3)
    
    @pytest.mark.asyncio
    async def test_invalid_base64_frame(self):
        """Test handling of invalid base64 data"""
        invalid_data = "invalid_base64_data"
        
        decoded_frame = await ImageProcessor.decode_base64_frame(invalid_data)
        assert decoded_frame is not None
        assert decoded_frame.shape == (480, 640, 3)  # Should return dummy frame
    
    @pytest.mark.asyncio
    async def test_frame_quality_calculation(self):
        """Test frame quality metrics calculation"""
        # Create test frame with some noise
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        quality = await ImageProcessor.calculate_frame_quality(test_frame)
        
        assert "sharpness" in quality
        assert "brightness" in quality
        assert "contrast" in quality
        assert "noise" in quality
        assert "quality_score" in quality
        
        # Check that values are reasonable
        assert quality["sharpness"] >= 0
        assert 0 <= quality["brightness"] <= 255
        assert quality["quality_score"] >= 0


class TestYOLODetector:
    """Test YOLO object detection"""
    
    @pytest.fixture
    async def detector(self):
        """Create YOLO detector for testing"""
        detector = YOLODetector()
        # Don't initialize for unit tests to avoid model loading
        yield detector
        await detector.cleanup()
    
    @pytest.mark.asyncio
    async def test_detector_initialization(self, detector):
        """Test detector initialization"""
        # Test without model loading
        assert not detector.is_loaded()
        
        # Test model info
        info = detector.get_model_info()
        assert info["loaded"] is False
    
    @pytest.mark.asyncio
    async def test_detection_without_model(self, detector):
        """Test detection behavior when model not loaded"""
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        detections = await detector.detect_objects(test_frame)
        assert detections == []  # Should return empty list
    
    @pytest.mark.asyncio
    async def test_specific_detection_methods(self, detector):
        """Test specific detection methods"""
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        persons = await detector.detect_persons(test_frame)
        phones = await detector.detect_phones(test_frame)
        suspicious = await detector.detect_suspicious_objects(test_frame)
        
        assert isinstance(persons, list)
        assert isinstance(phones, list)
        assert isinstance(suspicious, list)


class TestFaceTracker:
    """Test face tracking functionality"""
    
    @pytest.fixture
    async def tracker(self):
        """Create face tracker for testing"""
        tracker = FaceTracker()
        # Don't initialize for unit tests
        yield tracker
        await tracker.cleanup()
    
    @pytest.mark.asyncio
    async def test_tracker_initialization(self, tracker):
        """Test tracker initialization"""
        assert not tracker.is_loaded()
        
        info = tracker.get_tracker_info()
        assert info["loaded"] is False
        assert "max_faces" in info
    
    @pytest.mark.asyncio
    async def test_face_analysis_without_model(self, tracker):
        """Test face analysis when model not loaded"""
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        analysis = await tracker.analyze_face(test_frame)
        assert analysis.face_detected is False
        assert analysis.looking_away is False
        assert analysis.confidence == 0.0
    
    @pytest.mark.asyncio
    async def test_face_count_without_model(self, tracker):
        """Test face counting when model not loaded"""
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        count = await tracker.get_face_count(test_frame)
        assert count == 0


class TestRiskScorer:
    """Test risk scoring functionality"""
    
    @pytest.fixture
    def scorer(self):
        """Create risk scorer for testing"""
        return RiskScorer()
    
    @pytest.mark.asyncio
    async def test_default_risk_assessment(self, scorer):
        """Test default risk assessment"""
        assessment = await scorer.get_default_risk_assessment()
        
        assert assessment.total_score == 0
        assert assessment.risk_level.value == "low"
        assert "phone_detection" in assessment.breakdown
        assert assessment.trend == "stable"
        assert len(assessment.recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_risk_level_determination(self, scorer):
        """Test risk level determination"""
        assert scorer._determine_risk_level(10).value == "low"
        assert scorer._determine_risk_level(35).value == "medium"
        assert scorer._determine_risk_level(65).value == "high"
        assert scorer._determine_risk_level(85).value == "critical"
    
    @pytest.mark.asyncio
    async def test_risk_breakdown(self, scorer):
        """Test risk breakdown calculation"""
        from app.schemas.models import BehaviorEvent, SeverityLevel
        
        events = [
            BehaviorEvent(
                event_type=EventType.PHONE_DETECTED,
                confidence=0.8,
                severity=SeverityLevel.HIGH,
                message="Phone detected",
                timestamp=datetime.utcnow().isoformat(),
                risk_score_impact=50
            ),
            BehaviorEvent(
                event_type=EventType.LOOKING_AWAY,
                confidence=0.7,
                severity=SeverityLevel.LOW,
                message="Looking away",
                timestamp=datetime.utcnow().isoformat(),
                risk_score_impact=10
            )
        ]
        
        breakdown = scorer._calculate_risk_breakdown(events)
        
        assert breakdown["phone_detection"] == 50
        assert breakdown["looking_away"] == 10
        assert breakdown["multiple_persons"] == 0
    
    @pytest.mark.asyncio
    async def test_risk_trend_analysis(self, scorer):
        """Test risk trend analysis"""
        session_id = "test_session"
        
        # No history
        trend = await scorer._analyze_risk_trend(session_id, 50)
        assert trend == "stable"
        
        # Add some history
        scorer.session_risk_history[session_id] = [30, 40, 50]
        trend = await scorer._analyze_risk_trend(session_id, 60)
        assert trend == "increasing"
        
        scorer.session_risk_history[session_id] = [60, 50, 40]
        trend = await scorer._analyze_risk_trend(session_id, 30)
        assert trend == "decreasing"


class TestDetectionService:
    """Test main detection service"""
    
    @pytest.fixture
    async def service(self):
        """Create detection service for testing"""
        yolo_detector = YOLODetector()
        face_tracker = FaceTracker()
        service = DetectionService(yolo_detector, face_tracker)
        yield service
        # Cleanup handled by detector and tracker fixtures
    
    @pytest.mark.asyncio
    async def test_frame_processing_error_handling(self, service):
        """Test error handling in frame processing"""
        invalid_frame_data = "invalid_base64"
        session_id = "test_session"
        timestamp = datetime.utcnow().isoformat()
        
        response = await service.process_frame(invalid_frame_data, session_id, timestamp)
        
        # Should return valid response with default values
        assert response.session_id == session_id
        assert response.detections == []
        assert response.face_analysis.face_detected is False
        assert response.processing_time_ms >= 0
    
    @pytest.mark.asyncio
    async def test_cooldown_management(self, service):
        """Test event cooldown management"""
        session_id = "test_session"
        event_type = "phone_detection"
        
        # Initially no cooldown
        assert await service._check_cooldown(session_id, event_type) is True
        
        # Set cooldown
        await service._set_cooldown(session_id, event_type, 5)
        
        # Should be in cooldown
        assert await service._check_cooldown(session_id, event_type) is False
    
    @pytest.mark.asyncio
    async def test_session_state_management(self, service):
        """Test session state tracking"""
        session_id = "test_session"
        
        # Initially no state
        summary = await service.get_session_summary(session_id)
        assert "error" in summary
        
        # Update state
        await service._update_session_state(
            session_id, 
            [],  # No detections
            service.face_tracker.__class__(),  # Dummy face analysis
            datetime.utcnow().isoformat()
        )
        
        # Should have state now
        summary = await service.get_session_summary(session_id)
        assert "session_id" in summary
        assert summary["session_id"] == session_id


class TestIntegration:
    """Integration tests"""
    
    @pytest.mark.asyncio
    async def test_full_detection_pipeline(self):
        """Test complete detection pipeline with dummy data"""
        # Create test frame
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Encode to base64
        success, encoded = cv2.imencode('.jpg', test_frame)
        assert success
        base64_data = base64.b64encode(encoded).decode('utf-8')
        
        # Create service components (without loading models)
        yolo_detector = YOLODetector()
        face_tracker = FaceTracker()
        service = DetectionService(yolo_detector, face_tracker)
        
        try:
            # Process frame
            response = await service.process_frame(
                base64_data, 
                "test_session", 
                datetime.utcnow().isoformat()
            )
            
            # Verify response structure
            assert response.session_id == "test_session"
            assert isinstance(response.detections, list)
            assert isinstance(response.behavior_events, list)
            assert response.risk_assessment.total_score >= 0
            assert response.processing_time_ms >= 0
            
        finally:
            await service.clear_session_state("test_session")
            await yolo_detector.cleanup()
            await face_tracker.cleanup()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
