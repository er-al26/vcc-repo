# Student Management Microservices

A distributed microservices system for managing student information and marks across multiple Virtual Machines.

## Project Overview

This project demonstrates a practical implementation of microservices architecture with:
- **2 Independent Services** running on separate VMs
- **Inter-Service Communication** via HTTP/REST
- **FastAPI Framework** for high-performance APIs
- **SystemD Integration** for production deployment

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      HOST MACHINE                                │
│                                                                  │
│  ┌─────────────────────┐         ┌─────────────────────┐        │
│  │   VM1 (server1)     │         │   VM2 (server2)     │        │
│  │   192.168.29.252    │         │   192.168.29.250    │        │
│  │                     │  HTTP   │                     │        │
│  │  Student Service ───┼────────►│  Marks Service      │        │
│  │  Port: 3001         │         │  Port: 3002         │        │
│  └─────────────────────┘         └─────────────────────┘        │
│                                                                  │
│              ▲         Bridged Network      ▲                    │
│              └──────────────────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

 For detailed architecture diagrams and design documentation, see [ARCHITECTURE.md](ARCHITECTURE.md)

## Services

| Service | VM | Port | Responsibility |
|---------|-----|------|----------------|
| Student Service | VM1 (192.168.29.252) | 3001 | Manages student info (rollno, name, age) |
| Marks Service | VM2 (192.168.29.250) | 3002 | Manages student marks/grades |

### Student Service Endpoints
- `GET /students` - List all students
- `GET /students/{rollno}` - Get student by roll number
- `POST /students` - Create new student
- `GET /students/{rollno}/complete` - Get student WITH marks (inter-service call)

### Marks Service Endpoints
- `GET /marks` - List all marks
- `GET /marks/{rollno}` - Get marks by roll number
- `POST /marks` - Create new marks entry

## Quick Start

### Prerequisites
- 2 VMs running Ubuntu Server 22.04
- Python 3.10+
- VirtualBox with Bridged Network

### Deploy Student Service (VM1)
```bash
ssh user@192.168.29.252
mkdir -p ~/microservices/student-service
cd ~/microservices/student-service

# Copy main.py, requirements.txt, student-service.service

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

sudo cp student-service.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable student-service
sudo systemctl start student-service
```

### Deploy Marks Service (VM2)
```bash
ssh user@192.168.29.250
mkdir -p ~/microservices/marks-service
cd ~/microservices/marks-service

# Copy main.py, requirements.txt, marks-service.service

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

sudo cp marks-service.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable marks-service
sudo systemctl start marks-service
```

## Testing

### Health Checks
```bash
curl http://192.168.29.252:3001/health
curl http://192.168.29.250:3002/health
```

### Inter-Service Communication Test
```bash
curl http://192.168.29.252:3001/students/B25AI2113/complete
```

Expected response:
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

### Create Student & Marks
```bash
# Create student
curl -X POST http://192.168.29.252:3001/students \
  -H "Content-Type: application/json" \
  -d '{"rollno": "B25AI2116", "name": "New Student", "age": 17}'

# Create marks
curl -X POST http://192.168.29.250:3002/marks \
  -H "Content-Type: application/json" \
  -d '{"rollno": "B25AI2116", "marks": 89.5}'
```

## API Documentation

Interactive Swagger UI:
- Student Service: http://192.168.29.252:3001/docs
- Marks Service: http://192.168.29.250:3002/docs

## Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.10+ |
| Framework | FastAPI 0.109.0 |
| Server | Uvicorn 0.27.0 |
| Validation | Pydantic 2.5.3 |
| HTTP Client | HTTPX 0.26.0 |
| OS | Ubuntu Server 22.04 LTS |

## Project Structure

```
student-microservices/
├── README.md
├── ARCHITECTURE.md
│
├── student-service/
│   ├── main.py
│   ├── requirements.txt
│   ├── student-service.service
│   └── README.md
│
└── marks-service/
    ├── main.py
    ├── requirements.txt
    ├── marks-service.service
    └── README.md
```

## Service Management

```bash
# Start
sudo systemctl start student-service
sudo systemctl start marks-service

# Stop
sudo systemctl stop student-service
sudo systemctl stop marks-service

# Status
sudo systemctl status student-service
sudo systemctl status marks-service

# Logs
sudo journalctl -u student-service -f
sudo journalctl -u marks-service -f
```

## Configuration

Update IP addresses in `student-service/main.py`:
```python
MARKS_SERVICE_URL = "http://192.168.29.250:3002"
```

**Note:** IP addresses are assigned dynamically by your router via DHCP. They will change if:
- You connect to a different network/internet
- You create a new VM
- Router restarts or reassigns IPs

To find current IP, run `ip addr show` on each VM and update the configuration accordingly.

## Author

**Allabaksh S**
- Roll No: M25AI2123
- Institution: IIT Jodhpur
- Program: B.Tech in AI

## License

This project is for educational purposes.
