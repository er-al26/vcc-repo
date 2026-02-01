# Marks Service

Manages student marks/grades and provides marks data to other services.

## Description

The Marks Service is responsible for storing and managing student marks. It provides a simple API for CRUD operations on marks data and serves requests from the Student Service.

## Responsibilities

- Store and manage marks information
- Provide CRUD operations for marks
- Validate marks range (0-100)
- Respond to inter-service requests from Student Service

## Data Model

```python
{
    "rollno": "B25AI2113",
    "marks": 92.5,
    "created_at": "2026-01-31T..."
}
```

## API Endpoints

### GET /
Returns service information

### GET /health
Health check endpoint

**Response:**
```json
{
    "status": "UP",
    "service": "marks-service",
    "recordCount": 3
}
```

### GET /marks
Get all marks

**Response:**
```json
{
    "success": true,
    "count": 3,
    "data": [...]
}
```

### GET /marks/{rollno}
Get marks for specific student

**Response:**
```json
{
    "success": true,
    "data": {
        "rollno": "B25AI2113",
        "marks": 92.5,
        "created_at": "..."
    }
}
```

### POST /marks
Create new marks entry

**Request Body:**
```json
{
    "rollno": "B25AI2116",
    "marks": 87.5
}
```

**Validation:**
- Marks must be between 0 and 100
- Roll number must be unique (no duplicates)

**Response:**
```json
{
    "success": true,
    "message": "Marks created successfully",
    "data": {...}
}
```

**Error Responses:**
- 400: Marks out of range (0-100)
- 404: Marks not found for given rollno
- 409: Marks already exist for this student

## Configuration

**IP Address:** 192.168.29.250
**Port:** 3002

## Dependencies

- fastapi==0.109.0
- uvicorn[standard]==0.27.0
- pydantic==2.5.3

## Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run manually
python main.py
```

## Service Management

```bash
# Install as systemd service
sudo cp marks-service.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable marks-service
sudo systemctl start marks-service

# Check status
sudo systemctl status marks-service

# View logs
sudo journalctl -u marks-service -f
```

## Testing

```bash
# Health check
curl http://localhost:3002/health

# Get all marks
curl http://localhost:3002/marks

# Get specific marks
curl http://localhost:3002/marks/B25AI2113

# Create marks
curl -X POST http://localhost:3002/marks \
  -H "Content-Type: application/json" \
  -d '{"rollno": "B25AI2116", "marks": 87.5}'
```

## API Documentation

Interactive Swagger UI available at: http://192.168.29.250:3002/docs

## Inter-Service Communication

This service is called by the Student Service when complete student information is requested. The Student Service makes HTTP GET requests to `/marks/{rollno}` to fetch marks data.

**Expected callers:**
- Student Service (192.168.29.252)
- Direct client requests

## Troubleshooting

### Service won't start
```bash
sudo journalctl -u marks-service -n 50
```

### Port already in use
```bash
sudo netstat -tulpn | grep :3002
sudo kill -9 <PID>
```

### Marks validation error
Ensure marks are between 0 and 100.

## Data Validation

### Marks Field
- **Type:** Float
- **Range:** 0.0 - 100.0
- **Required:** Yes

### Roll Number Field
- **Type:** String
- **Unique:** Yes
- **Required:** Yes

## Storage

Currently uses in-memory storage (Python list). In production, this would be replaced with:
- PostgreSQL
- MongoDB
- MySQL

## Security

Current implementation includes:
- Input validation via Pydantic
- Range validation for marks
- Duplicate prevention

Recommended additions for production:
- API key authentication
- Rate limiting
- HTTPS/TLS
