from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models.database import database
from app.models.schemas import RiskLevel, TestStats, UserTestAttempt


class ScoringService:
    @staticmethod
    async def calculate_risk_level(risk_score: int) -> RiskLevel:
        """Calculate risk level based on risk score"""
        if risk_score <= 25:
            return RiskLevel.LOW
        elif risk_score <= 50:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.HIGH
    
    @staticmethod
    async def calculate_test_statistics(test_id: str) -> TestStats:
        """Calculate comprehensive test statistics"""
        try:
            db = await database.get_database()
            
            # Get all sessions for this test
            sessions = await db.sessions.find({
                "test_id": test_id,
                "final_score": {"$exists": True}
            }).to_list(length=None)
            
            if not sessions:
                return TestStats(
                    test_id=test_id,
                    total_attendees=0,
                    average_score=0.0,
                    average_risk=0.0,
                    high_risk_count=0,
                    medium_risk_count=0,
                    low_risk_count=0,
                    pass_rate=0.0
                )
            
            # Calculate statistics
            total_attendees = len(sessions)
            scores = [s["final_score"] for s in sessions]
            risk_scores = [s["final_risk_score"] for s in sessions]
            
            average_score = sum(scores) / len(scores) if scores else 0.0
            average_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0.0
            
            # Count risk levels
            high_risk_count = sum(1 for r in risk_scores if r > 50)
            medium_risk_count = sum(1 for r in risk_scores if 25 < r <= 50)
            low_risk_count = sum(1 for r in risk_scores if r <= 25)
            
            # Calculate pass rate (70% and above)
            pass_rate = (sum(1 for s in scores if s >= 70) / len(scores)) * 100 if scores else 0.0
            
            return TestStats(
                test_id=test_id,
                total_attendees=total_attendees,
                average_score=round(average_score, 2),
                average_risk=round(average_risk, 2),
                high_risk_count=high_risk_count,
                medium_risk_count=medium_risk_count,
                low_risk_count=low_risk_count,
                pass_rate=round(pass_rate, 2)
            )
            
        except Exception as e:
            print(f"❌ Error calculating test statistics: {e}")
            # Return empty stats on error
            return TestStats(
                test_id=test_id,
                total_attendees=0,
                average_score=0.0,
                average_risk=0.0,
                high_risk_count=0,
                medium_risk_count=0,
                low_risk_count=0,
                pass_rate=0.0
            )
    
    @staticmethod
    async def get_test_attendees(test_id: str) -> List[UserTestAttempt]:
        """Get all users who attended a specific test with their results"""
        try:
            db = await database.get_database()
            
            # Get all completed sessions for this test
            sessions = await db.sessions.find({
                "test_id": test_id,
                "final_score": {"$exists": True}
            }).to_list(length=None)
            
            attendees = []
            
            for session in sessions:
                # Get user information
                user = await db.users.find_one({"user_id": session["user_id"]})
                
                if user:
                    # Calculate risk level
                    risk_level = await ScoringService.calculate_risk_level(
                        session.get("final_risk_score", 0)
                    )
                    
                    # Determine status
                    score = session["final_score"]
                    if score >= 70:
                        status = "Passed"
                    elif score >= 50:
                        status = "Borderline"
                    else:
                        status = "Failed"
                    
                    attendee = UserTestAttempt(
                        user_id=user["user_id"],
                        name=user["name"],
                        email=user["email"],
                        score=score,
                        risk_score=session.get("final_risk_score", 0),
                        risk_level=risk_level,
                        date=session["start_time"],
                        status=status
                    )
                    
                    attendees.append(attendee)
            
            # Sort by date (most recent first)
            attendees.sort(key=lambda x: x.date, reverse=True)
            
            return attendees
            
        except Exception as e:
            print(f"❌ Error getting test attendees: {e}")
            return []
    
    @staticmethod
    async def update_user_statistics(user_id: str):
        """Update user's overall statistics after completing a test"""
        try:
            db = await database.get_database()
            
            # Get all completed sessions for this user
            sessions = await db.sessions.find({
                "user_id": user_id,
                "final_score": {"$exists": True}
            }).to_list(length=None)
            
            if not sessions:
                return
            
            # Calculate statistics
            total_tests = len(sessions)
            scores = [s["final_score"] for s in sessions]
            risk_scores = [s["final_risk_score"] for s in sessions]
            
            average_score = sum(scores) / len(scores) if scores else 0.0
            average_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0.0
            
            # Calculate overall risk level
            risk_level = await ScoringService.calculate_risk_level(int(average_risk))
            
            # Get last active time
            last_active = max(s["start_time"] for s in sessions)
            
            # Update user document
            await db.users.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "total_tests": total_tests,
                        "average_score": round(average_score, 2),
                        "risk_level": risk_level.value,
                        "last_active": last_active,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
        except Exception as e:
            print(f"❌ Error updating user statistics: {e}")
    
    @staticmethod
    async def update_test_attempt_count(test_id: str):
        """Update the number of attempts for a test"""
        try:
            db = await database.get_database()
            
            # Count all sessions for this test
            attempt_count = await db.sessions.count_documents({"test_id": test_id})
            
            # Update test document
            await db.tests.update_one(
                {"test_id": test_id},
                {
                    "$set": {
                        "attempts": attempt_count,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
        except Exception as e:
            print(f"❌ Error updating test attempt count: {e}")
    
    @staticmethod
    async def get_overall_statistics() -> Dict[str, Any]:
        """Get overall system statistics"""
        try:
            db = await database.get_database()
            
            # Get counts
            total_users = await db.users.count_documents({})
            total_tests = await db.tests.count_documents({})
            total_sessions = await db.sessions.count_documents({})
            
            # Get average scores
            completed_sessions = await db.sessions.find({
                "final_score": {"$exists": True}
            }).to_list(length=None)
            
            if completed_sessions:
                scores = [s["final_score"] for s in completed_sessions]
                risk_scores = [s["final_risk_score"] for s in completed_sessions]
                
                average_score = sum(scores) / len(scores) if scores else 0.0
                average_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0.0
                
                # Count high risk users
                high_risk_count = sum(1 for r in risk_scores if r > 50)
            else:
                average_score = 0.0
                average_risk = 0.0
                high_risk_count = 0
            
            return {
                "total_users": total_users,
                "total_tests": total_tests,
                "total_sessions": total_sessions,
                "average_score": round(average_score, 2),
                "average_risk": round(average_risk, 2),
                "high_risk_users": high_risk_count
            }
            
        except Exception as e:
            print(f"❌ Error getting overall statistics: {e}")
            return {
                "total_users": 0,
                "total_tests": 0,
                "total_sessions": 0,
                "average_score": 0.0,
                "average_risk": 0.0,
                "high_risk_users": 0
            }


# Global scoring service instance
scoring_service = ScoringService()