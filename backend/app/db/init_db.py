import uuid
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.core.security import get_password_hash


async def init_sample_data():
    """Initialize database with sample data"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    
    print("🌱 Initializing sample data...")
    
    try:
        # Clear existing data
        await db.users.delete_many({})
        await db.tests.delete_many({})
        await db.sessions.delete_many({})
        await db.events.delete_many({})
        
        print("🗑️ Cleared existing data")
        
        # Create sample users
        sample_users = [
            {
                "user_id": "user_student1",
                "email": "john.doe@example.com",
                "name": "John Doe",
                "role": "student",
                "password": get_password_hash("password123"),
                "total_tests": 8,
                "average_score": 85.0,
                "risk_level": "low",
                "last_active": datetime.utcnow() - timedelta(hours=2),
                "created_at": datetime.utcnow() - timedelta(days=30)
            },
            {
                "user_id": "user_student2", 
                "email": "jane.smith@example.com",
                "name": "Jane Smith",
                "role": "student",
                "password": get_password_hash("password123"),
                "total_tests": 12,
                "average_score": 78.0,
                "risk_level": "medium",
                "last_active": datetime.utcnow() - timedelta(hours=6),
                "created_at": datetime.utcnow() - timedelta(days=25)
            },
            {
                "user_id": "user_student3",
                "email": "mike.johnson@example.com", 
                "name": "Mike Johnson",
                "role": "student",
                "password": get_password_hash("password123"),
                "total_tests": 5,
                "average_score": 65.0,
                "risk_level": "high",
                "last_active": datetime.utcnow() - timedelta(minutes=30),
                "created_at": datetime.utcnow() - timedelta(days=15)
            }
        ]
        
        await db.users.insert_many(sample_users)
        print("👥 Created sample users")
        
        # Create sample tests
        sample_tests = [
            {
                "test_id": "test_math1",
                "title": "Mathematics Assessment",
                "description": "Comprehensive math test covering algebra, geometry, and calculus",
                "duration": 60,
                "difficulty": "medium",
                "questions": [
                    {
                        "question": "What is the derivative of x² + 3x + 2?",
                        "options": ["2x + 3", "x + 3", "2x + 2", "x² + 3"],
                        "correct_answer": 0
                    },
                    {
                        "question": "Solve for x: 2x + 5 = 15",
                        "options": ["x = 5", "x = 10", "x = 7.5", "x = 3"],
                        "correct_answer": 0
                    },
                    {
                        "question": "What is the integral of 2x?",
                        "options": ["x² + C", "2x² + C", "x + C", "2x + C"],
                        "correct_answer": 0
                    }
                ],
                "status": "active",
                "attempts": 45,
                "created_at": datetime.utcnow() - timedelta(days=15),
                "updated_at": datetime.utcnow() - timedelta(days=10)
            },
            {
                "test_id": "test_cs1",
                "title": "Computer Science Fundamentals",
                "description": "Test your knowledge of programming concepts and algorithms",
                "duration": 90,
                "difficulty": "hard",
                "questions": [
                    {
                        "question": "What is the time complexity of binary search?",
                        "options": ["O(n)", "O(log n)", "O(n²)", "O(1)"],
                        "correct_answer": 1
                    },
                    {
                        "question": "Which data structure uses LIFO principle?",
                        "options": ["Queue", "Stack", "Array", "Linked List"],
                        "correct_answer": 1
                    }
                ],
                "status": "active",
                "attempts": 32,
                "created_at": datetime.utcnow() - timedelta(days=10),
                "updated_at": datetime.utcnow() - timedelta(days=5)
            },
            {
                "test_id": "test_eng1",
                "title": "English Proficiency",
                "description": "Evaluate your English language skills and comprehension",
                "duration": 45,
                "difficulty": "easy",
                "questions": [
                    {
                        "question": "Choose the correct form: \"He ___ to school yesterday.\"",
                        "options": ["go", "went", "gone", "going"],
                        "correct_answer": 1
                    }
                ],
                "status": "active",
                "attempts": 28,
                "created_at": datetime.utcnow() - timedelta(days=5),
                "updated_at": datetime.utcnow() - timedelta(days=2)
            }
        ]
        
        await db.tests.insert_many(sample_tests)
        print("📝 Created sample tests")
        
        # Create sample sessions and events
        sample_sessions = [
            {
                "session_id": "session_john_math",
                "user_id": "user_student1",
                "test_id": "test_math1",
                "start_time": datetime.utcnow() - timedelta(hours=2),
                "end_time": datetime.utcnow() - timedelta(hours=1),
                "final_score": 92.0,
                "final_risk_score": 15.0,
                "current_risk_score": 15.0,
                "status": "completed",
                "created_at": datetime.utcnow() - timedelta(hours=2),
                "last_frame_processed": datetime.utcnow() - timedelta(hours=1)
            },
            {
                "session_id": "session_john_cs",
                "user_id": "user_student1", 
                "test_id": "test_cs1",
                "start_time": datetime.utcnow() - timedelta(days=3),
                "end_time": datetime.utcnow() - timedelta(days=3) + timedelta(minutes=85),
                "final_score": 78.0,
                "final_risk_score": 35.0,
                "current_risk_score": 35.0,
                "status": "completed",
                "created_at": datetime.utcnow() - timedelta(days=3),
                "last_frame_processed": datetime.utcnow() - timedelta(days=3) + timedelta(minutes=85)
            },
            {
                "session_id": "session_jane_math",
                "user_id": "user_student2",
                "test_id": "test_math1",
                "start_time": datetime.utcnow() - timedelta(hours=6),
                "end_time": datetime.utcnow() - timedelta(hours=5),
                "final_score": 85.0,
                "final_risk_score": 25.0,
                "current_risk_score": 25.0,
                "status": "completed",
                "created_at": datetime.utcnow() - timedelta(hours=6),
                "last_frame_processed": datetime.utcnow() - timedelta(hours=5)
            },
            {
                "session_id": "session_jane_eng",
                "user_id": "user_student2",
                "test_id": "test_eng1", 
                "start_time": datetime.utcnow() - timedelta(days=2),
                "end_time": datetime.utcnow() - timedelta(days=2) + timedelta(minutes=40),
                "final_score": 71.0,
                "final_risk_score": 45.0,
                "current_risk_score": 45.0,
                "status": "completed",
                "created_at": datetime.utcnow() - timedelta(days=2),
                "last_frame_processed": datetime.utcnow() - timedelta(days=2) + timedelta(minutes=40)
            },
            {
                "session_id": "session_mike_cs",
                "user_id": "user_student3",
                "test_id": "test_cs1",
                "start_time": datetime.utcnow() - timedelta(minutes=30),
                "end_time": datetime.utcnow() - timedelta(minutes=30) + timedelta(minutes=88),
                "final_score": 58.0,
                "final_risk_score": 78.0,
                "current_risk_score": 78.0,
                "status": "completed",
                "created_at": datetime.utcnow() - timedelta(minutes=30),
                "last_frame_processed": datetime.utcnow() - timedelta(minutes=30) + timedelta(minutes=88)
            },
            {
                "session_id": "session_mike_math",
                "user_id": "user_student3",
                "test_id": "test_math1",
                "start_time": datetime.utcnow() - timedelta(days=1),
                "end_time": datetime.utcnow() - timedelta(days=1) + timedelta(minutes=62),
                "final_score": 72.0,
                "final_risk_score": 62.0,
                "current_risk_score": 62.0,
                "status": "completed",
                "created_at": datetime.utcnow() - timedelta(days=1),
                "last_frame_processed": datetime.utcnow() - timedelta(days=1) + timedelta(minutes=62)
            }
        ]
        
        await db.sessions.insert_many(sample_sessions)
        print("📊 Created sample sessions")
        
        # Create sample events
        sample_events = [
            {
                "event_id": "event_1",
                "session_id": "session_mike_cs",
                "event_type": "phone_detected",
                "timestamp": datetime.utcnow() - timedelta(minutes=45),
                "confidence": 0.85,
                "risk_score_impact": 50,
                "description": "Phone detected",
                "metadata": {
                    "severity": "high",
                    "detections": [{"class_name": "cell phone", "confidence": 0.85}]
                }
            },
            {
                "event_id": "event_2",
                "session_id": "session_mike_cs",
                "event_type": "looking_away",
                "timestamp": datetime.utcnow() - timedelta(minutes=30),
                "confidence": 0.70,
                "risk_score_impact": 10,
                "description": "Looking away from screen",
                "metadata": {
                    "severity": "low",
                    "detections": []
                }
            },
            {
                "event_id": "event_3",
                "session_id": "session_jane_eng",
                "event_type": "multiple_persons",
                "timestamp": datetime.utcnow() - timedelta(days=2) + timedelta(minutes=20),
                "confidence": 0.80,
                "risk_score_impact": 70,
                "description": "Multiple persons detected: 2",
                "metadata": {
                    "severity": "high",
                    "detections": [{"class_name": "person", "confidence": 0.80}]
                }
            }
        ]
        
        await db.events.insert_many(sample_events)
        print("⚡ Created sample events")
        
        print("✅ Sample data initialization complete!")
        print("\n📊 Summary:")
        print(f"- Users: {len(sample_users)}")
        print(f"- Tests: {len(sample_tests)}")
        print(f"- Sessions: {len(sample_sessions)}")
        print(f"- Events: {len(sample_events)}")
        
        print("\n🔑 Sample User Credentials:")
        print("- Email: john.doe@example.com | Password: password123")
        print("- Email: jane.smith@example.com | Password: password123")
        print("- Email: mike.johnson@example.com | Password: password123")
        
    except Exception as e:
        print(f"❌ Error initializing sample data: {e}")
    
    finally:
        await client.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(init_sample_data())