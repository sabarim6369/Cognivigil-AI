from datetime import datetime
from fastapi import APIRouter, Depends
from app.models.schemas import HealthResponse
from app.models.database import database
from app.services.detection_service import detection_service

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db_connected = False
        try:
            await database.get_database()
            db_connected = True
        except Exception:
            pass
        
        # Check AI models
        ai_models_loaded = detection_service.yolo_model is not None
        
        status = "healthy" if db_connected and ai_models_loaded else "unhealthy"
        
        return HealthResponse(
            status=status,
            database_connected=db_connected,
            ai_models_loaded=ai_models_loaded,
            timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        return HealthResponse(
            status="error",
            database_connected=False,
            ai_models_loaded=False,
            timestamp=datetime.utcnow()
        )