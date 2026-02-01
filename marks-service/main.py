from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List
from datetime import datetime
import uvicorn

app = FastAPI(title="Marks Service", version="1.0.0")

# Data Models
class MarksCreate(BaseModel):
    rollno: str
    marks: float

class Marks(MarksCreate):
    created_at: datetime

# In-memory database
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

# Helper function
def find_marks(rollno: str):
    for marks in marks_db:
        if marks["rollno"] == rollno:
            return marks
    return None

# API Endpoints
@app.get("/")
async def root():
    return {
        "service": "Marks Service",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "all_marks": "/marks",
            "marks_by_rollno": "/marks/{rollno}"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "UP",
        "service": "marks-service",
        "recordCount": len(marks_db)
    }

@app.get("/marks")
async def get_all_marks():
    return {
        "success": True,
        "count": len(marks_db),
        "data": marks_db
    }

@app.get("/marks/{rollno}")
async def get_marks(rollno: str):
    marks = find_marks(rollno)
    if not marks:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "error": f"Marks for {rollno} not found"}
        )
    return {"success": True, "data": marks}

@app.post("/marks", status_code=201)
async def create_marks(marks: MarksCreate):
    # Validate marks range
    if marks.marks < 0 or marks.marks > 100:
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": "Marks must be between 0 and 100"}
        )
    
    # Check if marks already exist
    if find_marks(marks.rollno):
        raise HTTPException(
            status_code=409,
            detail={"success": False, "error": "Marks already exist for this student"}
        )
    
    new_marks = {
        "rollno": marks.rollno,
        "marks": marks.marks,
        "created_at": datetime.now()
    }
    marks_db.append(new_marks)
    return {
        "success": True,
        "message": "Marks created successfully",
        "data": new_marks
    }

if __name__ == "__main__":
    print("=" * 50)
    print("📊 Marks Service Started")
    print(f"📍 Running on: http://192.168.29.250:3002")
    print(f"📚 API Docs: http://192.168.29.250:3002/docs")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=3002)
