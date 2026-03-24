from fastapi import APIRouter, HTTPException, status
from app.models.database import database
from app.models.schemas import TestResponse

router = APIRouter()


@router.get("/", response_model=list[TestResponse])
async def get_available_tests():
    """Get all available tests for students"""
    try:
        db = await database.get_database()
        
        # Get only active tests
        tests = await db.tests.find(
            {"status": "active"}
        ).sort("created_at", -1).to_list(length=None)
        
        return tests
        
    except Exception as e:
        print(f"❌ Error getting available tests: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available tests"
        )


@router.get("/{test_id}", response_model=TestResponse)
async def get_test_by_id(test_id: str):
    """Get specific test by ID"""
    try:
        db = await database.get_database()
        
        test = await db.tests.find_one({"test_id": test_id, "status": "active"})
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
