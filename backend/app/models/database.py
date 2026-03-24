from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from typing import Optional


class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None

    @classmethod
    async def connect_to_mongo(cls):
        """Create database connection"""
        cls.client = AsyncIOMotorClient(settings.mongodb_url)
        cls.database = cls.client[settings.database_name]
        print("✅ Connected to MongoDB")

    @classmethod
    async def close_mongo_connection(cls):
        """Close database connection"""
        if cls.client:
            cls.client.close()
            print("✅ Disconnected from MongoDB")

    @classmethod
    async def get_database(cls):
        """Get database instance"""
        if not cls.database:
            await cls.connect_to_mongo()
        return cls.database

    @classmethod
    async def create_indexes(cls):
        """Create database indexes for better performance"""
        db = await cls.get_database()
        
        # User indexes
        await db.users.create_index("email", unique=True)
        await db.users.create_index("user_id")
        
        # Test indexes
        await db.tests.create_index("test_id", unique=True)
        await db.tests.create_index("created_at")
        
        # Session indexes
        await db.sessions.create_index("session_id", unique=True)
        await db.sessions.create_index("user_id")
        await db.sessions.create_index("created_at")
        
        # Event indexes
        await db.events.create_index("session_id")
        await db.events.create_index("timestamp")
        await db.events.create_index("event_type")
        
        print("✅ Database indexes created")


# Database instance
database = Database()