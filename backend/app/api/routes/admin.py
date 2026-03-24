import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.core.security import authenticate_admin, create_access_token, get_password_hash
from app.core.config import settings
from app.models.schemas import AdminLogin, Token, TestCreate, TestResponse, TestUpdate, UserResponse
from app.models.database import database
from app.api.deps import get_admin_user
from app.services.scoring_service import scoring_service

router = APIRouter()
security = HTTPBasic()


@router.post("/login", response_model=Token)
async def admin_login(credentials: AdminLogin):
    """Admin login endpoint"""
    try:
        if authenticate_admin(credentials.username, credentials.password):
            # Create access token
            access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
            access_token = create_access_token(
                data={"sub": credentials.username, "role": "admin"},
                expires_delta=access_token_expires
            )
            
            return Token(access_token=access_token, token_type="bearer")
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Basic"},
            )
    except Exception as e:
        print(f"❌ Admin login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/tests", response_model=TestResponse)
async def create_test(test_data: TestCreate, current_user = Depends(get_admin_user)):
    """Create a new test"""
    try:
        db = await database.get_database()
        
        # Generate unique test ID
        test_id = f"test_{uuid.uuid4().hex[:8]}"
        
        # Create test document
        test_doc = {
            "test_id": test_id,
            "title": test_data.title,
            "description": test_data.description,
            "duration": test_data.duration,
            "difficulty": test_data.difficulty.value,
            "questions": [
                {
                    "question": q.question,
                    "options": q.options,
                    "correct_answer": q.correct_answer
                } for q in test_data.questions
            ],
            "status": "active",
            "attempts": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.tests.insert_one(test_doc)
        
        return TestResponse(
            test_id=test_id,
            title=test_data.title,
            description=test_data.description,
            duration=test_data.duration,
            difficulty=test_data.difficulty,
            questions=test_data.questions,
            status="active",
            attempts=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
    except Exception as e:
        print(f"❌ Error creating test: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create test"
        )


@router.get("/tests")
async def get_all_tests(current_user = Depends(get_admin_user)):
    """Get all tests"""
    try:
        db = await database.get_database()
        
        tests = await db.tests.find().sort("created_at", -1).to_list(length=None)
        
        return {"tests": tests, "total_count": len(tests)}
        
    except Exception as e:
        print(f"❌ Error getting tests: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get tests"
        )


@router.get("/tests/{test_id}")
async def get_test(test_id: str, current_user = Depends(get_admin_user)):
    """Get specific test details"""
    try:
        db = await database.get_database()
        
        test = await db.tests.find_one({"test_id": test_id})
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test not found"
            )
        
        return test
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting test: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get test"
        )


@router.put("/tests/{test_id}")
async def update_test(test_id: str, test_data: TestUpdate, current_user = Depends(get_admin_user)):
    """Update a test"""
    try:
        db = await database.get_database()
        
        # Check if test exists
        test = await db.tests.find_one({"test_id": test_id})
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test not found"
            )
        
        # Prepare update data
        update_data = {"updated_at": datetime.utcnow()}
        
        if test_data.title:
            update_data["title"] = test_data.title
        if test_data.description:
            update_data["description"] = test_data.description
        if test_data.duration:
            update_data["duration"] = test_data.duration
        if test_data.difficulty:
            update_data["difficulty"] = test_data.difficulty.value
        if test_data.questions:
            update_data["questions"] = [
                {
                    "question": q.question,
                    "options": q.options,
                    "correct_answer": q.correct_answer
                } for q in test_data.questions
            ]
        if test_data.status:
            update_data["status"] = test_data.status.value
        
        # Update test
        await db.tests.update_one(
            {"test_id": test_id},
            {"$set": update_data}
        )
        
        return {"message": "Test updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error updating test: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update test"
        )


@router.delete("/tests/{test_id}")
async def delete_test(test_id: str, current_user = Depends(get_admin_user)):
    """Delete a test"""
    try:
        db = await database.get_database()
        
        # Check if test exists
        test = await db.tests.find_one({"test_id": test_id})
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test not found"
            )
        
        # Delete test
        await db.tests.delete_one({"test_id": test_id})
        
        return {"message": "Test deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting test: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete test"
        )


@router.get("/tests/{test_id}/details")
async def get_test_details(test_id: str, current_user = Depends(get_admin_user)):
    """Get comprehensive test details with statistics and attendees"""
    try:
        db = await database.get_database()
        
        # Get test
        test = await db.tests.find_one({"test_id": test_id})
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test not found"
            )
        
        # Get statistics
        stats = await scoring_service.calculate_test_statistics(test_id)
        
        # Get attendees
        attendees = await scoring_service.get_test_attendees(test_id)
        
        return {
            "test": test,
            "stats": stats,
            "attendees": attendees
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting test details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get test details"
        )


@router.get("/users")
async def get_all_users(current_user = Depends(get_admin_user)):
    """Get all users"""
    try:
        db = await database.get_database()
        
        users = await db.users.find().sort("created_at", -1).to_list(length=None)
        
        return {"users": users, "total_count": len(users)}
        
    except Exception as e:
        print(f"❌ Error getting users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get users"
        )


@router.get("/users/{user_id}")
async def get_user_details(user_id: str, current_user = Depends(get_admin_user)):
    """Get detailed user information"""
    try:
        db = await database.get_database()
        
        # Get user
        user = await db.users.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get user sessions
        sessions = await db.sessions.find(
            {"user_id": user_id, "final_score": {"$exists": True}}
        ).sort("start_time", -1).to_list(length=None)
        
        # Prepare test history
        test_history = []
        for session in sessions:
            # Get test details
            test = await db.tests.find_one({"test_id": session["test_id"]})
            if test:
                test_history.append({
                    "test_id": session["test_id"],
                    "test_name": test["title"],
                    "score": session["final_score"],
                    "risk_score": session["final_risk_score"],
                    "date": session["start_time"]
                })
        
        return {
            "user": user,
            "test_history": test_history,
            "total_sessions": len(sessions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting user details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user details"
        )


@router.get("/dashboard/overview")
async def get_dashboard_overview(current_user = Depends(get_admin_user)):
    """Get dashboard overview statistics"""
    try:
        stats = await scoring_service.get_overall_statistics()
        
        # Get recent activity
        db = await database.get_database()
        
        recent_sessions = await db.sessions.find(
            {"final_score": {"$exists": True}}
        ).sort("start_time", -1).limit(10).to_list(length=None)
        
        # Prepare recent activity with user info
        recent_activity = []
        for session in recent_sessions:
            user = await db.users.find_one({"user_id": session["user_id"]})
            test = await db.tests.find_one({"test_id": session["test_id"]})
            
            if user and test:
                recent_activity.append({
                    "user_name": user["name"],
                    "test_name": test["title"],
                    "score": session["final_score"],
                    "risk_score": session["final_risk_score"],
                    "date": session["start_time"]
                })
        
        return {
            "stats": stats,
            "recent_activity": recent_activity
        }
        
    except Exception as e:
        print(f"❌ Error getting dashboard overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dashboard overview"
        )
