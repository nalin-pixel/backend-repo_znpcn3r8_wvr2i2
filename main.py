import os
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="NUPal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------- Models ----------------------
class ChatRequest(BaseModel):
    message: str

class StudyPlanRequest(BaseModel):
    major: str = "Computer Science"
    current_semester: int = 3
    total_semesters: int = 8

class SkillGapRequest(BaseModel):
    job_title: str
    required_skills: List[str]
    resume_text: Optional[str] = ""
    resume_skills: Optional[List[str]] = None

class ReservationRequest(BaseModel):
    court: str
    date: str
    time: str
    name: str

class ElectiveSuggestionRequest(BaseModel):
    desired_code: str
    current_schedule: List[dict]

# ---------------------- Root & Health ----------------------
@app.get("/")
def read_root():
    return {"service": "NUPal Backend", "status": "ok"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the NUPal backend!"}

# ---------------------- Home Analytics ----------------------
@app.get("/api/analytics")
def analytics():
    return {
        "gpa": 3.62,
        "upcoming": {
            "course": "CS302 - Algorithms",
            "time": "Today 2:00 PM",
            "location": "Room B-214"
        },
        "completed_credits": 78,
        "current_credits": 15,
        "attendance": 92,
    }

# ---------------------- Advising ----------------------
@app.post("/api/advising/chat")
def advising_chat(req: ChatRequest):
    text = req.message.lower()
    if "prereq" in text or "prerequisite" in text:
        reply = (
            "Most 300-level CS courses require CS201 (Data Structures) and CS202 (OOP). "
            "Check your study plan to ensure these are completed."
        )
    elif "gpa" in text:
        reply = "Your current GPA is 3.62. Keep it above 3.5 for honors eligibility."
    elif "elective" in text:
        reply = (
            "Popular electives this term: AI in Healthcare, Mobile Dev, Cloud Fundamentals. "
            "Consider time fit with your chosen block."
        )
    else:
        reply = (
            "I'm your NUPal Advisor. Ask about prerequisites, course load, or electives. "
            "You can also generate a multi-semester plan below."
        )
    return {"role": "assistant", "message": reply}

@app.post("/api/study-plan")
def study_plan(req: StudyPlanRequest):
    core_sequence = [
        ("CS201", "Data Structures"),
        ("CS202", "OOP"),
        ("CS301", "Databases"),
        ("CS302", "Algorithms"),
        ("CS303", "Operating Systems"),
        ("CS304", "Computer Networks"),
        ("CS401", "Machine Learning"),
        ("CS402", "Distributed Systems"),
    ]
    semesters = []
    idx = max(0, req.current_semester - 1)
    for s in range(req.current_semester, req.total_semesters + 1):
        courses = []
        # Add up to 3 core + 2 electives per semester
        for _ in range(3):
            if idx < len(core_sequence):
                code, title = core_sequence[idx]
                courses.append({"code": code, "title": title, "credits": 3})
                idx += 1
        courses.append({"code": f"EL{s}1", "title": "Technical Elective", "credits": 3})
        courses.append({"code": f"EL{s}2", "title": "Open Elective", "credits": 3})
        semesters.append({
            "semester": s,
            "total_credits": sum(c["credits"] for c in courses),
            "courses": courses
        })
    return {"major": req.major, "plan": semesters}

# ---------------------- Campus Services ----------------------
@app.get("/api/campus/food")
def food_menu():
    return {
        "pickup_only": True,
        "items": [
            {
                "id": 1,
                "name": "Grilled Chicken Wrap",
                "price": 6.5,
                "image": "https://images.unsplash.com/photo-1550317138-10000687a72b?q=80&w=1400&auto=format&fit=crop"
            },
            {
                "id": 2,
                "name": "Veggie Bowl",
                "price": 7.0,
                "image": "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?q=80&w=1400&auto=format&fit=crop"
            },
            {
                "id": 3,
                "name": "Iced Latte",
                "price": 3.25,
                "image": "https://images.unsplash.com/photo-1517705008128-361805f42e86?q=80&w=1400&auto=format&fit=crop"
            }
        ],
        "hero_image": "https://images.unsplash.com/photo-1559339352-11d035aa65de?q=80&w=1600&auto=format&fit=crop"
    }

@app.get("/api/campus/courts")
def courts():
    return {
        "courts": [
            {"name": "Paddle Court 1", "type": "paddle"},
            {"name": "Paddle Court 2", "type": "paddle"},
            {"name": "Football Field", "type": "football"},
            {"name": "Basketball Court", "type": "basketball"},
        ],
        "slots": [
            "08:00-09:00", "09:00-10:00", "10:00-11:00", "16:00-17:00", "17:00-18:00", "18:00-19:00"
        ]
    }

@app.post("/api/campus/courts/reserve")
def reserve_slot(req: ReservationRequest):
    # Demo: pretend success without persistence
    return {"status": "reserved", "court": req.court, "date": req.date, "time": req.time}

@app.get("/api/campus/study-groups")
def study_groups(course: str = "CS301"):
    return {
        "course": course,
        "groups": [
            {"id": 1, "title": f"{course} - Evening Group", "members": 5, "time": "Mon 6pm", "avatar_seed": "A"},
            {"id": 2, "title": f"{course} - Library Session", "members": 3, "time": "Wed 4pm", "avatar_seed": "B"},
            {"id": 3, "title": f"{course} - Weekend Sprint", "members": 6, "time": "Sat 11am", "avatar_seed": "C"},
        ]
    }

@app.get("/api/campus/bus-schedules")
def bus_schedules():
    return {
        "routes": [
            {"route": "Blue Line", "time": "Every 20m", "days": "Mon-Fri"},
            {"route": "Campus Loop", "time": "Every 10m", "days": "Daily"},
            {"route": "City Express", "time": "07:30, 08:30, 17:30", "days": "Mon-Fri"},
        ]
    }

# ---------------------- Career Advising ----------------------
@app.get("/api/career/overview")
def career_overview():
    return {
        "major": "Computer Science",
        "skills": {
            "Python": 88,
            "Databases": 72,
            "Algorithms": 80,
            "Cloud": 60,
            "Data Visualization": 55
        }
    }

@app.get("/api/career/jobs")
def career_jobs():
    return {
        "jobs": [
            {
                "id": 101,
                "title": "Backend Intern",
                "company": "Nimbus Tech",
                "skills": ["Python", "APIs", "Databases"],
                "description": "Build APIs and work with PostgreSQL/Mongo."
            },
            {
                "id": 102,
                "title": "Data Analyst Intern",
                "company": "Insight Labs",
                "skills": ["Python", "SQL", "Pandas", "Visualization"],
                "description": "Analyze datasets and build dashboards."
            },
            {
                "id": 103,
                "title": "Mobile Developer Intern",
                "company": "AppForge",
                "skills": ["React Native", "JavaScript", "APIs"],
                "description": "Help build cross-platform mobile features."
            },
        ]
    }

@app.post("/api/career/skill-gap")
def skill_gap(req: SkillGapRequest):
    resume_skills = {s.strip().lower() for s in (req.resume_skills or [])}
    # naive extraction from resume_text
    text = (req.resume_text or "").lower()
    for token in ["python", "sql", "pandas", "react", "apis", "databases", "statistics", "cloud", "docker", "linux"]:
        if token in text:
            resume_skills.add(token)
    required = {s.lower() for s in req.required_skills}
    matched = sorted(list(required & resume_skills))
    missing = sorted(list(required - resume_skills))
    fit = int(100 * (len(matched) / max(1, len(required))))
    return {
        "job_title": req.job_title,
        "fit_percent": fit,
        "matched_skills": matched,
        "missing_skills": missing,
        "suggestions": [
            "Strengthen fundamentals with a short online course",
            "Build a small project to demonstrate missing skills",
            "Add quantified results to your resume bullets"
        ]
    }

# ---------------------- Course Scheduling ----------------------
@app.get("/api/schedule/blocks")
def schedule_blocks():
    return {
        "blocks": [
            {
                "id": "A",
                "title": "Block A",
                "courses": [
                    {"code": "CS301", "title": "Databases", "day": "Mon", "time": "10:00-11:30", "room": "B-101"},
                    {"code": "CS302", "title": "Algorithms", "day": "Wed", "time": "12:00-13:30", "room": "B-214"},
                    {"code": "MTH210", "title": "Probability", "day": "Thu", "time": "14:00-15:30", "room": "A-303"}
                ]
            },
            {
                "id": "B",
                "title": "Block B",
                "courses": [
                    {"code": "CS303", "title": "Operating Systems", "day": "Tue", "time": "09:00-10:30", "room": "C-120"},
                    {"code": "CS304", "title": "Networks", "day": "Thu", "time": "10:00-11:30", "room": "B-105"},
                    {"code": "HUM110", "title": "Ethics", "day": "Fri", "time": "13:00-14:30", "room": "D-008"}
                ]
            },
        ]
    }

@app.post("/api/schedule/suggest")
def schedule_suggest(req: ElectiveSuggestionRequest):
    # Simple demo suggestion logic
    alt_blocks = [
        {"id": "A", "diff": "Switch Algorithms to Tue"},
        {"id": "B", "diff": "Move Networks to Wed"}
    ]
    electives = [
        {"code": "DS310", "title": "Data Science", "day": "Mon", "time": "16:00-17:30"},
        {"code": "SE220", "title": "Software Eng II", "day": "Tue", "time": "12:00-13:30"},
        {"code": "AI340", "title": "Intro to AI", "day": "Thu", "time": "16:00-17:30"}
    ]
    return {"recommended_blocks": alt_blocks, "recommended_electives": electives}

# ---------------------- Database test ----------------------
@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        from database import db
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = getattr(db, 'name', '✅ Connected')
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except ImportError:
        response["database"] = "❌ Database module not found"
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
