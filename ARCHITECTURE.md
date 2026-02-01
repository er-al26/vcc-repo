# Architecture Design Document

Student Management Microservices System

---

## System Architecture

### High-Level Architecture

```
┌────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                        │
│                                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Browser  │  │ Terminal │  │  Postman │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
│       │             │              │                   │
│       └─────────────┴──────────────┘                   │
│                     │                                  │
│              HTTP/REST (JSON)                          │
└─────────────────────┼──────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              MICROSERVICES LAYER                         │
│                                                           │
│  ┌────────────────────────────────────────────────┐     │
│  │        VM1: Student Service                    │     │
│  │        192.168.29.252:3001                     │     │
│  │  ┌──────────────────────────────────────────┐ │     │
│  │  │  FastAPI Application                      │ │     │
│  │  │  • GET /students                          │ │     │
│  │  │  • GET /students/{rollno}                 │ │     │
│  │  │  • POST /students                         │ │     │
│  │  │  • GET /students/{rollno}/complete        │ │     │
│  │  │    (calls Marks Service)                  │ │     │
│  │  └──────────────────────────────────────────┘ │     │
│  │  [Students Database - In-Memory]              │     │
│  └────────────┬───────────────────────────────────┘     │
│               │                                          │
│               │ HTTP Request                             │
│               │ GET /marks/{rollno}                      │
│               ▼                                          │
│  ┌────────────────────────────────────────────────┐     │
│  │        VM2: Marks Service                      │     │
│  │        192.168.29.250:3002                     │     │
│  │  ┌──────────────────────────────────────────┐ │     │
│  │  │  FastAPI Application                      │ │     │
│  │  │  • GET /marks                             │ │     │
│  │  │  • GET /marks/{rollno}                    │ │     │
│  │  │  • POST /marks                            │ │     │
│  │  └──────────────────────────────────────────┘ │     │
│  │  [Marks Database - In-Memory]                 │     │
│  └────────────────────────────────────────────────┘     │
│                                                           │
└─────────────────────────────────────────────────────────┘

Legend:
  ──▶  HTTP Request Flow
  ◄──  HTTP Response Flow
  [ ]  Data Store
```

---

## Network Architecture

### Network Topology

```
┌────────────────────────────────────────────────┐
│         Physical Network                        │
│         (192.168.29.x/24)                       │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │      MacBook (Host Machine)              │  │
│  │      Client / Development Machine         │  │
│  └──────────────┬───────────────────────────┘  │
│                 │                                │
│  ┌──────────────┼──────────────────────────┐   │
│  │         WiFi Router                      │   │
│  │         192.168.29.1                     │   │
│  │         (DHCP Server)                    │   │
│  └──────────────┬───────────┬───────────────┘   │
│                 │           │                    │
│        ┌────────▼───┐   ┌───▼────────┐          │
│        │   VM1      │   │   VM2      │          │
│        │ Student    │   │ Marks      │          │
│        │ Service    │   │ Service    │          │
│        │.251:3001   │   │.250:3002   │          │
│        └────────────┘   └────────────┘          │
│         Bridged           Bridged                │
│         Adapter           Adapter                │
└────────────────────────────────────────────────┘
```

### IP Address Allocation

| Component | IP Address | Port | Role |
|-----------|------------|------|------|
| Router/Gateway | 192.168.29.1 | - | DHCP, Routing |
| MacBook | 192.168.29.x | - | Client |
| VM1 (Student Service) | 192.168.29.252 | 3001 | Student Management |
| VM2 (Marks Service) | 192.168.29.250 | 3002 | Marks Management |

---

## Component Design

### 1. Student Service (VM1)

**Responsibilities:**
- Manage student information (rollno, name, age)
- Provide CRUD operations for students
- Aggregate student and marks data
- Act as gateway for complete student information

**Data Model:**
```python
Student {
    rollno: str       # Primary Key (e.g., "B25AI2113")
    name: str         # Student Name
    age: int          # Student Age
    created_at: datetime  # Timestamp
}
```

**API Endpoints:**
```
GET  /                          → Service information
GET  /health                    → Health check
GET  /students                  → List all students
GET  /students/{rollno}         → Get specific student
POST /students                  → Create new student
GET  /students/{rollno}/complete → Get student with marks
```

**Dependencies:**
- FastAPI (web framework)
- Uvicorn (ASGI server)
- Pydantic (data validation)
- HTTPX (HTTP client for inter-service calls)

**Configuration:**
```python
MARKS_SERVICE_URL = "http://192.168.29.250:3002"
PORT = 3001
HOST = "0.0.0.0"
```

---

### 2. Marks Service (VM2)

**Responsibilities:**
- Manage marks information (rollno, marks)
- Provide CRUD operations for marks
- Validate marks range (0-100)
- Respond to Student Service requests

**Data Model:**
```python
Marks {
    rollno: str       # Foreign Key (references Student)
    marks: float      # Marks/Score (0-100)
    created_at: datetime  # Timestamp
}
```

**API Endpoints:**
```
GET  /                   → Service information
GET  /health             → Health check
GET  /marks              → List all marks
GET  /marks/{rollno}     → Get marks for specific student
POST /marks              → Create new marks entry
```

**Dependencies:**
- FastAPI (web framework)
- Uvicorn (ASGI server)
- Pydantic (data validation)

**Configuration:**
```python
PORT = 3002
HOST = "0.0.0.0"
```

---

## Data Flow Diagrams

### Flow 1: Get Student Basic Information

```
Client
  │
  ├─ GET /students/B25AI2113
  │
  ▼
Student Service (VM1)
  │
  ├─ Query local database
  ├─ Find student by rollno
  │
  ▼
Return: {rollno, name, age}
```

### Flow 2: Get Marks Only

```
Client
  │
  ├─ GET /marks/B25AI2113
  │
  ▼
Marks Service (VM2)
  │
  ├─ Query local database
  ├─ Find marks by rollno
  │
  ▼
Return: {rollno, marks}
```

### Flow 3: Get Complete Student (Inter-Service Communication)

```
Client
  │
  ├─ GET /students/B25AI2113/complete
  │
  ▼
Student Service (VM1)
  │
  ├─ Step 1: Query local database
  ├─ Find student: {rollno, name, age}
  │
  ├─ Step 2: Call Marks Service via HTTP
  │   │
  │   └─► GET http://192.168.29.250:3002/marks/B25AI2113
  │         │
  │         ▼
  │      Marks Service (VM2)
  │         │
  │         ├─ Query marks database
  │         ├─ Find marks: {rollno, marks}
  │         │
  │         └─► Return: {rollno, marks: 92.5}
  │
  ├─ Step 3: Combine data
  ├─ Merge: {rollno, name, age} + {marks}
  │
  ▼
Return: {rollno, name, age, marks}
```

**This demonstrates:**
- Service decomposition
- HTTP-based inter-service communication
- Data aggregation
- Synchronous request-response pattern

---

## Inter-Service Communication

### Communication Pattern: Synchronous HTTP/REST

**How it works:**
1. Student Service receives request for complete student data
2. Student Service makes HTTP GET request to Marks Service
3. Marks Service processes request and returns data
4. Student Service combines both data sets
5. Student Service returns aggregated response to client

**Technology:**
- Protocol: HTTP/1.1
- Format: JSON
- Method: GET
- Timeout: 5 seconds
- Error Handling: Returns student data without marks if service unavailable

**Code Pattern:**
```python
# Student Service calls Marks Service
async with httpx.AsyncClient(timeout=5.0) as client:
    response = await client.get(
        f"{MARKS_SERVICE_URL}/marks/{rollno}"
    )
    marks_data = response.json()
```

**Why this approach?**
- Simple to implement
- Easy to debug
- Follows REST principles
- Language agnostic
- Works across network boundaries

---

## Data Architecture

### Student Service Database

**Storage:** In-Memory Python List
**Purpose:** Demonstration / Development

```python
students_db = [
    {
        "rollno": "B25AI2113",
        "name": "Ravi varman",
        "age": 16,
        "created_at": datetime.now()
    },
    {
        "rollno": "B25AI2114",
        "name": "Rahul Kumar",
        "age": 17,
        "created_at": datetime.now()
    },
    {
        "rollno": "B25AI2115",
        "name": "Priya Sharma",
        "age": 16,
        "created_at": datetime.now()
    }
]
```

**Production Alternative:** PostgreSQL, MongoDB

### Marks Service Database

**Storage:** In-Memory Python List
**Purpose:** Demonstration / Development

```python
marks_db = [
    {
        "rollno": "B25AI2113",
        "marks": 92.5,
        "created_at": datetime.now()
    },
    {
        "rollno": "B25AI2114",
        "marks": 88.0,
        "created_at": datetime.now()
    },
    {
        "rollno": "B25AI2115",
        "marks": 95.5,
        "created_at": datetime.now()
    }
]
```

**Production Alternative:** PostgreSQL, MongoDB

**Note:** In production, both services would use persistent databases with proper indexing, relationships, and backup strategies.

---

## Security Architecture

### Current Security Measures

1. **Network Isolation**
   - Services on private network (192.168.29.x)
   - Not directly exposed to internet

2. **Input Validation**
   - Pydantic models validate all inputs
   - Type checking for all fields
   - Range validation for marks (0-100)

3. **Error Handling**
   - Proper HTTP status codes
   - No sensitive data in error messages
   - Graceful degradation (returns student data even if marks unavailable)

### Recommended Enhancements

1. **Authentication & Authorization**
   - JWT tokens for API access
   - API keys for inter-service communication
   - Role-based access control (RBAC)

2. **HTTPS/TLS**
   - SSL certificates for encrypted communication
   - Certificate-based authentication

3. **Rate Limiting**
   - Per-IP request limits
   - DDoS protection

4. **Input Sanitization**
   - SQL injection prevention (when using DB)
   - XSS protection

---

## Scalability Considerations

### Current Architecture (Single Instance)

```
Client → Student Service (1 instance)
              ↓
         Marks Service (1 instance)
```

### Scaled Architecture (Multiple Instances)

```
                    ┌─→ Student Service 1
Client → Load → Student Service 2
         Balancer   └─→ Student Service 3
                         ↓
                    ┌─→ Marks Service 1
                    └─→ Marks Service 2
```

### Scaling Strategies

1. **Horizontal Scaling**
   - Add more VM instances
   - Load balancer distributes requests
   - Each service can scale independently

2. **Database Scaling**
   - Master-slave replication
   - Sharding by rollno
   - Caching layer (Redis)

3. **Service Discovery**
   - Consul/Eureka for dynamic service registration
   - Health checking
   - Automatic failover

---

## Design Principles Demonstrated

### 1. Microservices Architecture
- Single responsibility per service
- Independent deployment
- Technology flexibility

### 2. Service Decomposition
- Student management separate from marks
- Clear boundaries
- Loose coupling

### 3. API-First Design
- Well-defined REST APIs
- Automatic documentation (Swagger)
- Version control ready

### 4. Fault Tolerance
- Graceful degradation
- Timeout handling
- Error recovery

### 5. Observability
- Health check endpoints
- Logging via journalctl
- Status monitoring

---

## 🎓 Learning Outcomes

This architecture teaches:
- Distributed systems design
- Microservices communication patterns
- RESTful API design
- Service orchestration
- Network programming
- Production deployment
- System architecture documentation

---

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Application** | FastAPI | Web framework |
| **Server** | Uvicorn | ASGI server |
| **Validation** | Pydantic | Data validation |
| **HTTP Client** | HTTPX | Inter-service calls |
| **Language** | Python 3.10+ | Backend development |
| **OS** | Ubuntu 22.04 | Server environment |
| **Process Manager** | SystemD | Service management |
| **Virtualization** | VirtualBox | VM management |
| **Network** | Bridged Adapter | VM networking |

---

## Conclusion

This architecture demonstrates a production-ready microservices system with:

**Key Features:**
- Clear service boundaries
- RESTful communication
- Independent scalability
- Fault tolerance
- Easy maintenance

**Real-World Applications:**
- E-commerce systems
- Banking applications
- Social media platforms
- Cloud services

**Production Readiness:**
- SystemD integration
- Health monitoring
- Error handling
- Automatic restart

---

**Architecture Version:** 1.0  
**Last Updated:** January 31, 2026  
**Status:** Complete and Tested
