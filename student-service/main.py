from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import httpx
import uvicorn

app = FastAPI(title="Student Service", version="1.0.0")

# Configuration
MARKS_SERVICE_URL = "http://192.168.29.250:3002"

# Data Models
class StudentCreate(BaseModel):
    rollno: str
    name: str
    age: int

class Student(StudentCreate):
    created_at: datetime

class StudentComplete(Student):
    marks: Optional[float] = None

# In-memory database
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

# Helper function
def find_student(rollno: str):
    for student in students_db:
        if student["rollno"] == rollno:
            return student
    return None

# API Endpoints
@app.get("/")
async def root():
    return {
        "service": "Student Service",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "students": "/students",
            "student_by_rollno": "/students/{rollno}",
            "complete_student": "/students/{rollno}/complete"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "UP",
        "service": "student-service",
        "studentCount": len(students_db)
    }

@app.get("/students")
async def get_all_students():
    return {
        "success": True,
        "count": len(students_db),
        "data": students_db
    }

@app.get("/students/{rollno}")
async def get_student(rollno: str):
    student = find_student(rollno)
    if not student:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "error": f"Student {rollno} not found"}
        )
    return {"success": True, "data": student}

@app.post("/students", status_code=201)
async def create_student(student: StudentCreate):
    # Check if student already exists
    if find_student(student.rollno):
        raise HTTPException(
            status_code=409,
            detail={"success": False, "error": "Student already exists"}
        )
    
    new_student = {
        "rollno": student.rollno,
        "name": student.name,
        "age": student.age,
        "created_at": datetime.now()
    }
    students_db.append(new_student)
    return {
        "success": True,
        "message": "Student created successfully",
        "data": new_student
    }

@app.get("/students/{rollno}/complete")
async def get_student_complete(rollno: str):
    """
    Get complete student information including marks from Marks Service
    This demonstrates inter-service communication
    """
    # Get student data from local database
    student = find_student(rollno)
    if not student:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "error": f"Student {rollno} not found"}
        )
    
    # Fetch marks from Marks Service (VM2)
    marks_data = None
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{MARKS_SERVICE_URL}/marks/{rollno}"
            )
            if response.status_code == 200:
                marks_response = response.json()
                marks_data = marks_response.get("data", {}).get("marks")
    except httpx.RequestError as e:
        print(f"Error connecting to Marks Service: {e}")
        # Continue without marks data
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    # Combine student and marks data
    complete_data = {
        **student,
        "marks": marks_data
    }
    
    return {
        "success": True,
        "data": complete_data,
        "note": "Marks fetched from Marks Service" if marks_data else "Marks unavailable"
    }

if __name__ == "__main__":
    print("=" * 50)
    print("👨‍🎓 Student Service Started")
    print(f"📍 Running on: http://192.168.29.252:3001")
    print(f"📚 API Docs: http://192.168.29.252:3001/docs")
    print(f"🔗 Marks Service: {MARKS_SERVICE_URL}")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=3001)
