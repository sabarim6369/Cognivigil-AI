import asyncio
from typing import Dict, Any, List
from app.schemas.models import (
    DetectionResult, FaceAnalysis, BehaviorEvent, 
    RiskAssessment, SeverityLevel
)
from app.utils.config import settings


class RiskScorer:
    """Risk scoring and assessment service"""
    
    def __init__(self):
        # Initialize risk weights from settings
        self.weights = {
            "phone_detection": settings.risk_phone_detection_weight,
            "multiple_persons": settings.risk_multiple_persons_weight,
            "face_absence": settings.risk_face_absence_weight,
            "looking_away": settings.risk_looking_away_weight,
            "suspicious_object": settings.risk_suspicious_object_weight
        }
        
        # Session risk history for trend analysis
        self.session_risk_history = {}
    
    async def calculate_risk(
        self,
        detections: List[DetectionResult],
        face_analysis: FaceAnalysis,
        behavior_events: List[BehaviorEvent],
        session_id: str
    ) -> RiskAssessment:
        """Calculate comprehensive risk assessment"""
        
        # Calculate base risk score from events
        base_score = sum(event.risk_score_impact for event in behavior_events)
        
        # Apply contextual modifiers
        modified_score = await self._apply_contextual_modifiers(
            base_score, detections, face_analysis, session_id
        )
        
        # Calculate risk level
        risk_level = self._determine_risk_level(modified_score)
        
        # Calculate breakdown
        breakdown = self._calculate_risk_breakdown(behavior_events)
        
        # Analyze trend
        trend = await self._analyze_risk_trend(session_id, modified_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risk_level, behavior_events)
        
        # Update session history
        await self._update_risk_history(session_id, modified_score)
        
        return RiskAssessment(
            total_score=min(modified_score, 100),  # Cap at 100
            risk_level=risk_level,
            breakdown=breakdown,
            trend=trend,
            recommendations=recommendations
        )
    
    async def _apply_contextual_modifiers(
        self,
        base_score: int,
        detections: List[DetectionResult],
        face_analysis: FaceAnalysis,
        session_id: str
    ) -> int:
        """Apply contextual modifiers to base risk score"""
        modified_score = base_score
        
        # Modifier 1: Face confidence modifier
        if face_analysis.face_detected and face_analysis.confidence < 0.6:
            # Low confidence face detection might indicate spoofing
            modified_score += 10
        
        # Modifier 2: Multiple suspicious objects
        suspicious_classes = ['book', 'laptop', 'tablet', 'notebook', 'paper']
        suspicious_count = sum(1 for d in detections if d.class_name in suspicious_classes)
        if suspicious_count > 2:
            modified_score += 15
        
        # Modifier 3: Person count modifier
        person_count = sum(1 for d in detections if d.class_name == 'person')
        if person_count > 1:
            extra_persons = person_count - 1
            modified_score += extra_persons * 20
        
        # Modifier 4: Face absence duration modifier
        if not face_analysis.face_detected and face_analysis.face_absence_duration > 10:
            # Extended face absence
            modified_score += 20
        
        # Modifier 5: High confidence detections modifier
        high_conf_detections = [d for d in detections if d.confidence > 0.8]
        if len(high_conf_detections) > 3:
            modified_score += 10
        
        return modified_score
    
    def _determine_risk_level(self, score: int) -> SeverityLevel:
        """Determine risk level based on score"""
        if score <= settings.risk_threshold_low:
            return SeverityLevel.LOW
        elif score <= settings.risk_threshold_medium:
            return SeverityLevel.MEDIUM
        elif score <= settings.risk_threshold_high:
            return SeverityLevel.HIGH
        else:
            return SeverityLevel.CRITICAL
    
    def _calculate_risk_breakdown(self, events: List[BehaviorEvent]) -> Dict[str, int]:
        """Calculate risk score breakdown by event type"""
        breakdown = {
            "phone_detection": 0,
            "multiple_persons": 0,
            "face_absence": 0,
            "looking_away": 0,
            "suspicious_object": 0
        }
        
        for event in events:
            event_type_key = event.event_type.value
            if event_type_key in breakdown:
                breakdown[event_type_key] += event.risk_score_impact
        
        return breakdown
    
    async def _analyze_risk_trend(self, session_id: str, current_score: int) -> str:
        """Analyze risk score trend over time"""
        if session_id not in self.session_risk_history:
            return "stable"
        
        history = self.session_risk_history[session_id]
        
        if len(history) < 3:
            return "stable"
        
        # Get last 3 scores
        recent_scores = history[-3:]
        
        # Calculate trend
        if recent_scores[-1] > recent_scores[-2] > recent_scores[-3]:
            return "increasing"
        elif recent_scores[-1] < recent_scores[-2] < recent_scores[-3]:
            return "decreasing"
        else:
            return "stable"
    
    def _generate_recommendations(
        self, 
        risk_level: SeverityLevel, 
        events: List[BehaviorEvent]
    ) -> List[str]:
        """Generate recommendations based on risk level and events"""
        recommendations = []
        
        if risk_level == SeverityLevel.LOW:
            recommendations.append("Continue monitoring - no immediate concerns")
        
        elif risk_level == SeverityLevel.MEDIUM:
            recommendations.append("Increase monitoring frequency")
            if any(e.event_type.value == "looking_away" for e in events):
                recommendations.append("Check if student needs assistance")
        
        elif risk_level == SeverityLevel.HIGH:
            recommendations.append("Immediate supervisor attention required")
            if any(e.event_type.value == "phone_detection" for e in events):
                recommendations.append("Verify if phone usage is authorized")
            if any(e.event_type.value == "multiple_persons" for e in events):
                recommendations.append("Check for unauthorized assistance")
        
        elif risk_level == SeverityLevel.CRITICAL:
            recommendations.append("URGENT: Consider exam intervention")
            recommendations.append("Document all suspicious activities")
            recommendations.append("Contact exam administrator immediately")
        
        # Event-specific recommendations
        event_types = set(e.event_type.value for e in events)
        
        if "face_absence" in event_types:
            recommendations.append("Ensure webcam is properly positioned")
        
        if "suspicious_object" in event_types:
            recommendations.append("Verify all materials are authorized")
        
        return recommendations
    
    async def _update_risk_history(self, session_id: str, score: int):
        """Update session risk history"""
        if session_id not in self.session_risk_history:
            self.session_risk_history[session_id] = []
        
        history = self.session_risk_history[session_id]
        history.append(score)
        
        # Keep only last 50 scores
        if len(history) > 50:
            history.pop(0)
    
    async def get_default_risk_assessment(self) -> RiskAssessment:
        """Get default risk assessment for error cases"""
        return RiskAssessment(
            total_score=0,
            risk_level=SeverityLevel.LOW,
            breakdown={
                "phone_detection": 0,
                "multiple_persons": 0,
                "face_absence": 0,
                "looking_away": 0,
                "suspicious_object": 0
            },
            trend="stable",
            recommendations=["System error - please check setup"]
        )
    
    async def get_session_risk_statistics(self, session_id: str) -> Dict[str, Any]:
        """Get detailed risk statistics for a session"""
        if session_id not in self.session_risk_history:
            return {"error": "Session not found"}
        
        scores = self.session_risk_history[session_id]
        
        if not scores:
            return {"error": "No risk data available"}
        
        return {
            "session_id": session_id,
            "total_assessments": len(scores),
            "current_score": scores[-1] if scores else 0,
            "average_score": sum(scores) / len(scores),
            "max_score": max(scores),
            "min_score": min(scores),
            "risk_distribution": self._calculate_distribution(scores),
            "trend": await self._analyze_risk_trend(session_id, scores[-1] if scores else 0)
        }
    
    def _calculate_distribution(self, scores: List[int]) -> Dict[str, int]:
        """Calculate risk level distribution"""
        distribution = {
            "low": 0,
            "medium": 0,
            "high": 0,
            "critical": 0
        }
        
        for score in scores:
            level = self._determine_risk_level(score).value
            distribution[level] += 1
        
        return distribution
    
    async def clear_session_history(self, session_id: str):
        """Clear risk history for a session"""
        if session_id in self.session_risk_history:
            del self.session_risk_history[session_id]
