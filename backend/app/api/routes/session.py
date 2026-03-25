import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import SessionCreate, SessionResponse
from app.models.database import database
from app.services.scoring_service import scoring_service

router = APIRouter()


@router.post("/create", response_model=SessionResponse)
async def create_session(session_data: dict):
    """Create a new exam session (simplified for demo)"""
    try:
        db = await database.get_database()
        
        # For demo purposes, create user and test if they don't exist
        user = await db.users.find_one({"user_id": session_data.get("user_id", "demo_user")})
        if not user:
            # Create demo user
            user_doc = {
                "user_id": session_data.get("user_id", "demo_user"),
                "email": "demo@example.com",
                "name": "Demo User",
                "created_at": datetime.utcnow(),
                "total_tests_taken": 0,
                "average_score": 0.0,
                "average_risk_score": 0.0
            }
            await db.users.insert_one(user_doc)
        
        test = await db.tests.find_one({"test_id": session_data.get("test_id", "1")})
        if not test:
            # Create demo test
            test_doc = {
                "test_id": session_data.get("test_id", "1"),
                "title": "Demo Test",
                "duration_minutes": 60,
                "total_questions": 3,
                "created_at": datetime.utcnow(),
                "total_attempts": 0,
                "average_score": 0.0,
                "average_risk_score": 0.0
            }
            await db.tests.insert_one(test_doc)
        
        # Use provided session_id or generate one
        session_id = session_data.get("session_id")
        if not session_id:
            session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        # Create session document
        session_doc = {
            "session_id": session_id,
            "user_id": session_data.get("user_id", "demo_user"),
            "test_id": session_data.get("test_id", "1"),
            "start_time": session_data.get("start_time", datetime.utcnow()),
            "end_time": None,
            "final_score": None,
            "final_risk_score": None,
            "current_risk_score": 0,
            "status": session_data.get("status", "active"),
            "created_at": datetime.utcnow(),
            "last_frame_processed": None
        }
        
        await db.sessions.insert_one(session_doc)
        
        # Create test started event
        event_doc = {
            "event_id": f"event_{datetime.utcnow().timestamp()}",
            "session_id": session_id,
            "event_type": "test_started",
            "timestamp": session_data.get("start_time", datetime.utcnow()),
            "confidence": 1.0,
            "risk_score_impact": 0,
            "description": "Test session started",
            "metadata": {
                "user_id": session_data.get("user_id", "demo_user"),
                "test_id": session_data.get("test_id", "1")
            }
        }
        
        await db.events.insert_one(event_doc)
        
        return SessionResponse(
            session_id=session_id,
            user_id=session_data.get("user_id", "demo_user"),
            test_id=session_data.get("test_id", "1"),
            start_time=session_data.get("start_time", datetime.utcnow()),
            end_time=None,
            final_score=None,
            final_risk_score=None,
            status=session_data.get("status", "active"),
            created_at=datetime.utcnow()
        )
        
    except Exception as e:
        print(f"❌ Error creating session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session"
        )


@router.post("/start", response_model=SessionResponse)
async def start_session(session_data: SessionCreate):
    """Start a new exam session"""
    try:
        db = await database.get_database()
        
        # Validate user exists
        user = await db.users.find_one({"user_id": session_data.user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Validate test exists
        test = await db.tests.find_one({"test_id": session_data.test_id})
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test not found"
            )
        
        # Generate unique session ID
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        # Create session document
        session_doc = {
            "session_id": session_id,
            "user_id": session_data.user_id,
            "test_id": session_data.test_id,
            "start_time": session_data.start_time,
            "end_time": None,
            "final_score": None,
            "final_risk_score": None,
            "current_risk_score": 0,
            "status": "active",
            "created_at": datetime.utcnow(),
            "last_frame_processed": None
        }
        
        await db.sessions.insert_one(session_doc)
        
        # Create test started event
        event_doc = {
            "event_id": f"event_{datetime.utcnow().timestamp()}",
            "session_id": session_id,
            "event_type": "test_started",
            "timestamp": session_data.start_time,
            "confidence": 1.0,
            "risk_score_impact": 0,
            "description": "Test session started",
            "metadata": {
                "user_id": session_data.user_id,
                "test_id": session_data.test_id
            }
        }
        
        await db.events.insert_one(event_doc)
        
        return SessionResponse(
            session_id=session_id,
            user_id=session_data.user_id,
            test_id=session_data.test_id,
            start_time=session_data.start_time,
            end_time=None,
            final_score=None,
            final_risk_score=None,
            status="active",
            created_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error starting session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start session"
        )


@router.post("/{session_id}/end")
async def end_session(session_id: str, final_score: float, final_risk_score: float):
    """End an exam session with final scores"""
    try:
        db = await database.get_database()
        
        # Find and update session
        session = await db.sessions.find_one({"session_id": session_id})
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Update session with final data
        await db.sessions.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "end_time": datetime.utcnow(),
                    "final_score": final_score,
                    "final_risk_score": final_risk_score,
                    "status": "completed"
                }
            }
        )
        
        # Create test completed event
        event_doc = {
            "event_id": f"event_{datetime.utcnow().timestamp()}",
            "session_id": session_id,
            "event_type": "test_completed",
            "timestamp": datetime.utcnow(),
            "confidence": 1.0,
            "risk_score_impact": 0,
            "description": f"Test completed with score: {final_score}%, risk: {final_risk_score}%",
            "metadata": {
                "final_score": final_score,
                "final_risk_score": final_risk_score
            }
        }
        
        await db.events.insert_one(event_doc)
        
        # Update user statistics
        await scoring_service.update_user_statistics(session["user_id"])
        
        # Update test attempt count
        await scoring_service.update_test_attempt_count(session["test_id"])
        
        return {"message": "Session ended successfully", "session_id": session_id}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error ending session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to end session"
        )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get session details"""
    try:
        db = await database.get_database()
        
        session = await db.sessions.find_one({"session_id": session_id})
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        return SessionResponse(
            session_id=session["session_id"],
            user_id=session["user_id"],
            test_id=session["test_id"],
            start_time=session["start_time"],
            end_time=session.get("end_time"),
            final_score=session.get("final_score"),
            final_risk_score=session.get("final_risk_score"),
            status=session.get("status", "active"),
            created_at=session["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get session"
        )


@router.get("/user/{user_id}")
async def get_user_sessions(user_id: str, limit: int = 10):
    """Get all sessions for a user"""
    try:
        db = await database.get_database()
        
        # Validate user exists
        user = await db.users.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get user sessions
        sessions = await db.sessions.find(
            {"user_id": user_id}
        ).sort("start_time", -1).limit(limit).to_list(length=None)
        
        return {"sessions": sessions, "total_count": len(sessions)}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting user sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user sessions"
        )


@router.get("/test/{test_id}")
async def get_test_sessions(test_id: str, limit: int = 50):
    """Get all sessions for a test"""
    try:
        db = await database.get_database()
        
        # Validate test exists
        test = await db.tests.find_one({"test_id": test_id})
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test not found"
            )
        
        # Get test sessions
        sessions = await db.sessions.find(
            {"test_id": test_id}
        ).sort("start_time", -1).limit(limit).to_list(length=None)
        
        return {"sessions": sessions, "total_count": len(sessions)}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting test sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get test sessions"
        )