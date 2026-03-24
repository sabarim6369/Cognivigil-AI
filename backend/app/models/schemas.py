from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    STUDENT = "student"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TestDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class TestStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class EventType(str, Enum):
    PHONE_DETECTED = "phone_detected"
    MULTIPLE_PERSONS = "multiple_persons"
    FACE_ABSENCE = "face_absence"
    LOOKING_AWAY = "looking_away"
    SUSPICIOUS_OBJECT = "suspicious_object"
    TEST_STARTED = "test_started"
    TEST_COMPLETED = "test_completed"


# User Models
class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: UserRole = UserRole.STUDENT


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    user_id: str
    total_tests: int = 0
    average_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW
    last_active: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Test Models
class QuestionBase(BaseModel):
    question: str
    options: List[str]
    correct_answer: int


class TestBase(BaseModel):
    title: str
    description: str
    duration: int  # in minutes
    difficulty: TestDifficulty
    questions: List[QuestionBase]


class TestCreate(TestBase):
    pass


class TestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = None
    difficulty: Optional[TestDifficulty] = None
    questions: Optional[List[QuestionBase]] = None
    status: Optional[TestStatus] = None


class TestResponse(TestBase):
    test_id: str
    status: TestStatus
    attempts: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Session Models
class SessionBase(BaseModel):
    user_id: str
    test_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    final_score: Optional[float] = None
    final_risk_score: Optional[float] = None
    status: str = "active"


class SessionCreate(SessionBase):
    pass


class SessionResponse(SessionBase):
    session_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Event Models
class EventBase(BaseModel):
    session_id: str
    event_type: EventType
    timestamp: datetime
    confidence: Optional[float] = None
    risk_score_impact: int = 0
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class EventCreate(EventBase):
    pass


class EventResponse(EventBase):
    event_id: str
    
    class Config:
        from_attributes = True


# Detection Models
class DetectionResult(BaseModel):
    class_name: str
    confidence: float
    bbox: List[float]
    center: List[float]


class FrameProcessRequest(BaseModel):
    frame: str  # base64 encoded image
    session_id: str
    timestamp: datetime


class FrameProcessResponse(BaseModel):
    detections: List[DetectionResult]
    risk_score: int
    alerts: List[Dict[str, Any]]
    processed_at: datetime


# Authentication Models
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[UserRole] = None


class AdminLogin(BaseModel):
    username: str
    password: str


# Statistics Models
class TestStats(BaseModel):
    test_id: str
    total_attendees: int
    average_score: float
    average_risk: float
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    pass_rate: float


class UserTestAttempt(BaseModel):
    user_id: str
    name: str
    email: str
    score: float
    risk_score: float
    risk_level: RiskLevel
    date: datetime
    status: str


class TestDetailsResponse(BaseModel):
    test: TestResponse
    stats: TestStats
    attendees: List[UserTestAttempt]


# API Response Models
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None


class HealthResponse(BaseModel):
    status: str
    database_connected: bool
    ai_models_loaded: bool
    timestamp: datetime