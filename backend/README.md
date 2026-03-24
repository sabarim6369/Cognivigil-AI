# 🚀 Cognivigil AI Backend

FastAPI backend for AI-powered exam proctoring system with MongoDB integration.

## 📋 Features

- **🔐 Admin Authentication** - Secure token-based authentication
- **📝 Test Management** - Create, update, delete tests with questions
- **👥 User Management** - Track user performance and statistics
- **🎥 Real-time Detection** - AI-powered object and behavior detection
- **📊 Risk Scoring** - Intelligent risk assessment system
- **📈 Analytics** - Comprehensive statistics and reporting
- **🗄️ MongoDB Integration** - Scalable data storage with Motor

## 🛠️ Tech Stack

- **FastAPI** - Modern Python web framework
- **MongoDB** - NoSQL database with Motor driver
- **YOLOv8** - Real-time object detection
- **MediaPipe** - Face tracking and analysis
- **JWT** - Secure authentication
- **Pydantic** - Data validation and serialization

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8+
python --version

# MongoDB running locally
mongod

# Optional: MongoDB Compass for GUI
```

### Installation

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup

Copy `.env` file and configure:

```bash
# Database Configuration
MONGODB_URL=mongodb://localhost:27017/cognivigil_ai
DATABASE_NAME=cognivigil_ai

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# AI Model Configuration
YOLO_MODEL_PATH=../ai-engine/models/yolov8n.pt
DETECTION_CONFIDENCE_THRESHOLD=0.5
RISK_THRESHOLD_HIGH=75
RISK_THRESHOLD_MEDIUM=50
```

### Start the Backend

```bash
# Option 1: Using startup script (recommended)
python start.py

# Option 2: Direct FastAPI
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Option 3: Using main module
python -m app.main
```

The server will start at: **http://localhost:8000**

## 📚 API Documentation

### Health Check
```bash
GET /health
GET /api/v1/health
```

### Admin Authentication
```bash
POST /api/v1/admin/login
{
  "username": "admin",
  "password": "admin123"
}
```

### Test Management
```bash
GET /api/v1/admin/tests              # Get all tests
POST /api/v1/admin/tests             # Create test
PUT /api/v1/admin/tests/{id}        # Update test
DELETE /api/v1/admin/tests/{id}     # Delete test
GET /api/v1/admin/tests/{id}/details # Get test details
```

### User Management
```bash
GET /api/v1/admin/users              # Get all users
GET /api/v1/admin/users/{id}         # Get user details
GET /api/v1/admin/dashboard/overview # Dashboard stats
```

### Session Management
```bash
POST /api/v1/sessions/start         # Start session
POST /api/v1/sessions/{id}/end      # End session
GET /api/v1/sessions/{id}           # Get session
```

### Detection API
```bash
POST /api/v1/process-frame          # Process frame for detection
GET /api/v1/detection/session/{id}/events     # Get session events
GET /api/v1/detection/session/{id}/risk-score  # Get risk score
```

## 🗄️ Database Schema

### Users Collection
```javascript
{
  "user_id": "user_abc123",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "student",
  "password": "hashed_password",
  "total_tests": 10,
  "average_score": 85.5,
  "risk_level": "low",
  "last_active": ISODate,
  "created_at": ISODate
}
```

### Tests Collection
```javascript
{
  "test_id": "test_xyz789",
  "title": "Mathematics Assessment",
  "description": "Test description",
  "duration": 60,
  "difficulty": "medium",
  "questions": [...],
  "status": "active",
  "attempts": 25,
  "created_at": ISODate
}
```

### Sessions Collection
```javascript
{
  "session_id": "session_def456",
  "user_id": "user_abc123",
  "test_id": "test_xyz789",
  "start_time": ISODate,
  "end_time": ISODate,
  "final_score": 92.5,
  "final_risk_score": 15.0,
  "current_risk_score": 15.0,
  "status": "completed"
}
```

### Events Collection
```javascript
{
  "event_id": "event_ghi789",
  "session_id": "session_def456",
  "event_type": "phone_detected",
  "timestamp": ISODate,
  "confidence": 0.85,
  "risk_score_impact": 50,
  "description": "Phone detected",
  "metadata": {...}
}
```

## 🔧 Development

### Database Initialization

```bash
# Initialize sample data
python app/db/init_db.py

# This creates:
# - 3 sample users
# - 3 sample tests  
# - Sample sessions and events
# - Proper indexes for performance
```

### AI Models

```bash
# Download YOLO model (if not present)
wget https://github.com/ultralytics/ultralytics/releases/download/v8.0.0/yolov8n.pt
# Place in: ../ai-engine/models/yolov8n.pt
```

### Testing

```bash
# Run health check
curl http://localhost:8000/health

# Test admin login
curl -X POST http://localhost:8000/api/v1/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

## 🚨 Error Handling

The backend includes comprehensive error handling:

- **Database Connection Errors** - Automatic retry with fallback
- **AI Model Errors** - Graceful degradation to dummy responses
- **Authentication Errors** - Clear error messages and proper HTTP status codes
- **Validation Errors** - Detailed Pydantic validation feedback

## 🔒 Security Features

- **JWT Authentication** - Secure token-based auth for admin
- **Password Hashing** - bcrypt for secure password storage
- **CORS Protection** - Configurable allowed origins
- **Input Validation** - Pydantic models for all inputs
- **Rate Limiting** - Built-in FastAPI rate limiting

## 📊 Performance

- **Async/Await** - Full async support for scalability
- **Database Indexing** - Optimized queries with proper indexes
- **Connection Pooling** - Motor async MongoDB driver
- **Caching Ready** - Redis integration points available

## 🐛 Debugging

Enable debug mode in `.env`:
```bash
DEBUG=True
LOG_LEVEL=debug
```

Check logs for:
- Database connection status
- AI model loading
- API request/response details
- Error stack traces

## 📦 Deployment

### Docker (Recommended)

```bash
# Build image
docker build -t cognivigil-backend .

# Run container
docker run -p 8000:8000 --env-file .env cognivigil-backend
```

### Production

```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🔗 API Integration

The frontend should connect to:
- **Base URL**: `http://localhost:8000/api/v1`
- **WebSocket**: `ws://localhost:8000/ws` (future feature)
- **Authentication**: Bearer token from `/admin/login`

## 📞 Support

For issues:
1. Check MongoDB is running: `mongod`
2. Verify environment variables
3. Check logs for error messages
4. Test health endpoint: `curl http://localhost:8000/health`

---

**🔥 Built for academic integrity with AI-powered proctoring**
