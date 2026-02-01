# Student Service

Manages student information and provides aggregated student+marks data through inter-service communication.

## 📝 Description

The Student Service is responsible for managing student basic information (roll number, name, age) and serves as the entry point for retrieving complete student data by calling the Marks Service.

## 🎯 Responsibilities

- Store and manage student information
- Provide CRUD operations for students
- Aggregate student and marks data from Marks Service
- Serve as the primary API for client applications

## 📊 Data Model

```python
{
    "rollno": "B25AI2113",
    "name": "Ravi varman",
    "age": 16,
    "created_at": "2026-01-31T..."
}
```

## 🌐 API Endpoints

### GET /
Returns service information

### GET /health
Health check endpoint

**Response:**
```json
{
    "status": "UP",
    "service": "student-service",
    "studentCount": 3
}
```

### GET /students
Get all students

**Response:**
```json
{
    "success": true,
    "count": 3,
    "data": [...]
}
```

### GET /students/{rollno}
Get specific student

**Response:**
```json
{
    "success": true,
    "data": {
        "rollno": "B25AI2113",
        "name": "Ravi varman",
        "age": 16
    }
}
```

### POST /students
Create new student

**Request Body:**
```json
{
    "rollno": "B25AI2116",
    "name": "New Student",
    "age": 17
}
```

**Response:**
```json
{
    "success": true,
    "message": "Student created successfully",
    "data": {...}
}
```

### GET /students/{rollno}/complete
Get complete student information including marks

**Response:**
```json
{
    "success": true,
    "data": {
        "rollno": "B25AI2113",
        "name": "Ravi varman",
        "age": 16,
        "marks": 92.5
    },
    "note": "Marks fetched from Marks Service"
}
```

**Note:** This endpoint demonstrates inter-service communication by calling the Marks Service.

## 🔧 Configuration

**IP Address:** 192.168.29.252
**Port:** 3001
**Marks Service URL:** http://192.168.29.250:3002

To change the Marks Service URL, edit `MARKS_SERVICE_URL` in `main.py`.

## 📦 Dependencies

- fastapi==0.109.0
- uvicorn[standard]==0.27.0
- pydantic==2.5.3
- httpx==0.26.0

## 🚀 Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run manually
python main.py
```

## 🔄 Service Management

```bash
# Install as systemd service
sudo cp student-service.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable student-service
sudo systemctl start student-service

# Check status
sudo systemctl status student-service

# View logs
sudo journalctl -u student-service -f
```

## 🧪 Testing

```bash
# Health check
curl http://localhost:3001/health

# Get all students
curl http://localhost:3001/students

# Get specific student
curl http://localhost:3001/students/B25AI2113

# Get complete student (with marks)
curl http://localhost:3001/students/B25AI2113/complete

# Create student
curl -X POST http://localhost:3001/students \
  -H "Content-Type: application/json" \
  -d '{"rollno": "B25AI2116", "name": "Test", "age": 17}'
```

## 📚 API Documentation

Interactive Swagger UI available at: http://192.168.29.252:3001/docs

## 🔗 Inter-Service Communication

This service communicates with the Marks Service to provide complete student information. The `/students/{rollno}/complete` endpoint:

1. Fetches student data from local database
2. Makes HTTP GET request to Marks Service
3. Combines both data sets
4. Returns aggregated response

**Timeout:** 5 seconds
**Error Handling:** Returns student data without marks if Marks Service is unavailable

## 🛠️ Troubleshooting

### Service won't start
```bash
sudo journalctl -u student-service -n 50
```

### Can't connect to Marks Service
```bash
# Test connection
curl http://192.168.29.250:3002/health
```

### Port already in use
```bash
sudo netstat -tulpn | grep :3001
sudo kill -9 <PID>
```
