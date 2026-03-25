from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import FrameProcessRequest, FrameProcessResponse
from app.models.database import database
from app.services.detection_service import detection_service
from app.services.scoring_service import scoring_service

router = APIRouter()


@router.post("/process-frame", response_model=FrameProcessResponse)
async def process_frame(request: dict):
    """Process a frame for AI detection and risk assessment"""
    try:
        # Extract data from request
        frame_data = request.get("frame")
        session_id = request.get("session_id")
        timestamp_str = request.get("timestamp")
        
        # Convert timestamp string to datetime if needed
        if isinstance(timestamp_str, str):
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        else:
            timestamp = datetime.utcnow()
        
        # Validate session exists
        db = await database.get_database()
        session = await db.sessions.find_one({"session_id": session_id})
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Process frame through AI detection
        result = await detection_service.process_frame(
            frame_data, 
            session_id
        )
        
        # Store events if any alerts detected
        if result.alerts:
            for alert in result.alerts:
                event_data = {
                    "event_id": f"event_{datetime.utcnow().timestamp()}",
                    "session_id": session_id,
                    "event_type": alert["type"],
                    "timestamp": timestamp,
                    "confidence": alert.get("confidence"),
                    "risk_score_impact": 0,  # Will be calculated based on alert severity
                    "description": alert["message"],
                    "metadata": {
                        "severity": alert["severity"],
                        "detections": [d.dict() for d in result.detections]
                    }
                }
                await db.events.insert_one(event_data)
        
        # Update session with latest risk score
        await db.sessions.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "current_risk_score": result.risk_score,
                    "last_frame_processed": datetime.utcnow()
                }
            }
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error processing frame: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process frame"
        )


@router.get("/session/{session_id}/events")
async def get_session_events(session_id: str, limit: int = 50):
    """Get events for a specific session"""
    try:
        db = await database.get_database()
        
        # Validate session exists
        session = await db.sessions.find_one({"session_id": session_id})
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Get events for the session
        events = await db.events.find(
            {"session_id": session_id}
        ).sort("timestamp", -1).limit(limit).to_list(length=None)
        
        return {"events": events, "total_count": len(events)}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting session events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get session events"
        )


@router.get("/session/{session_id}/risk-score")
async def get_session_risk_score(session_id: str):
    """Get current risk score for a session"""
    try:
        db = await database.get_database()
        
        session = await db.sessions.find_one({"session_id": session_id})
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        current_risk = session.get("current_risk_score", 0)
        final_risk = session.get("final_risk_score")
        
        risk_level = await scoring_service.calculate_risk_level(current_risk)
        
        return {
            "session_id": session_id,
            "current_risk_score": current_risk,
            "final_risk_score": final_risk,
            "risk_level": risk_level.value,
            "status": session.get("status", "active")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting risk score: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get risk score"
        )