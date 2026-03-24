import asyncio
from app.models.database import database
from datetime import datetime

async def add_default_test():
    """Add a default test to the database"""
    try:
        # First connect to database
        await database.connect_to_mongo()
        db = await database.get_database()
        
        if db is None:
            print("❌ Database connection failed")
            return
        
        # Check if test already exists
        existing_test = await db.tests.find_one({"test_id": "test_math_001"})
        if existing_test:
            print("✅ Default test already exists")
            return
        
        # Create default test
        test_data = {
            "test_id": "test_math_001",
            "title": "Mathematics Final Exam",
            "description": "Comprehensive math exam covering algebra, calculus, and statistics",
            "duration": 120,  # 2 hours
            "difficulty": "medium",
            "status": "active",
            "questions_count": 50,
            "created_at": datetime.utcnow(),
            "instructions": "Read each question carefully and select the best answer.",
            "ai_proctoring": {
                "enabled": True,
                "webcam_required": True,
                "risk_threshold": 75
            }
        }
        
        result = await db.tests.insert_one(test_data)
        print(f"✅ Default test added: {test_data['title']}")
        print(f"   Test ID: {test_data['test_id']}")
        print(f"   Duration: {test_data['duration']} minutes")
        
    except Exception as e:
        print(f"❌ Error adding test: {e}")

async def add_default_user():
    """Add a default user for testing"""
    try:
        # Database should already be connected from add_default_test
        db = await database.get_database()
        
        if db is None:
            print("❌ Database connection failed")
            return
        
        # Check if user already exists
        existing_user = await db.users.find_one({"user_id": "student_001"})
        if existing_user:
            print("✅ Default user already exists")
            return
        
        # Create default user
        user_data = {
            "user_id": "student_001",
            "name": "Test Student",
            "email": "student@test.com",
            "role": "student",
            "created_at": datetime.utcnow(),
            "tests_taken": 0,
            "average_score": 0.0,
            "high_risk_count": 0
        }
        
        result = await db.users.insert_one(user_data)
        print(f"✅ Default user added: {user_data['name']}")
        print(f"   User ID: {user_data['user_id']}")
        print(f"   Email: {user_data['email']}")
        
    except Exception as e:
        print(f"❌ Error adding user: {e}")

async def main():
    print("🔧 Adding Default Test Data")
    print("=" * 40)
    
    await add_default_test()
    await add_default_user()
    
    print("\n✅ Database setup complete!")
    print("   Test ID: test_math_001")
    print("   User ID: student_001")
    print("   You can now start a session and test AI monitoring")

if __name__ == "__main__":
    asyncio.run(main())
