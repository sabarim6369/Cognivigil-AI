from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.models.database import database
from app.services.detection_service import detection_service
from app.api.routes import health, detect, session, admin, tests

# Create evidence directory if it doesn't exist
os.makedirs(settings.evidence_storage_path, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting Cognivigil AI Backend...")
    
    # Connect to database
    await database.connect_to_mongo()
    
    # Create database indexes
    await database.create_indexes()
    
    # Initialize AI models
    await detection_service.initialize_models()
    
    print("✅ Backend startup complete!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Cognivigil AI Backend...")
    await database.close_mongo_connection()
    print("✅ Backend shutdown complete!")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered exam proctoring system backend",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(detect.router, prefix="/api/v1", tags=["Detection"])
app.include_router(session.router, prefix="/api/v1/sessions", tags=["Sessions"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(tests.router, prefix="/api/v1/tests", tags=["Tests"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Cognivigil AI Backend API",
        "version": settings.app_version,
        "status": "running"
    }


# Health check endpoint (without auth)
@app.get("/health")
async def health_check_simple():
    """Simple health check endpoint"""
    try:
        # Check database connection
        db_connected = False
        try:
            await database.get_database()
            db_connected = True
        except Exception:
            pass
        
        # Check AI Engine connection
        ai_engine_available = False
        try:
            import requests
            response = requests.get(f"{settings.ai_engine_url}/health", timeout=2)
            ai_engine_available = response.status_code == 200
        except:
            pass
        
        status = "healthy" if db_connected and ai_engine_available else "unhealthy"
        
        return {
            "status": status,
            "database_connected": db_connected,
            "ai_engine_available": ai_engine_available,
            "version": settings.app_version
        }
    
    except Exception as e:
        return {
            "status": "error",
            "database_connected": False,
            "ai_models_loaded": False,
            "version": settings.app_version,
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )