from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator, HttpUrl
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database import engine, Base, get_db
from models import Student, Job, User

import jwt
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
load_dotenv()



app = FastAPI()

from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()
security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY is missing from .env file")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

Base.metadata.create_all(bind=engine)


# Student profile validation
class StudentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    skills: str = Field(min_length=2, max_length=200)
    branch: str
    year: int = Field(ge=1, le=4)

    @field_validator("skills")
    @classmethod
    def skills_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Skills cannot be empty or only spaces")
        return value


# Skill-gap request model
class SkillGapRequest(BaseModel):
    student_skills: list[str]
    required_skills: list[str]


@app.get("/")
def home():
    return {"message": "AI Student Career Assistant is running!"}


@app.get("/student")
def get_student():
    return {
        "name": "Tanvi",
        "branch": "Robotics and AI",
        "year": 3
    }


@app.post("/student")
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db)
):
    new_student = Student(
        name=student.name,
        email=student.email,
        skills=student.skills,
        branch=student.branch,
        year=student.year
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return {
        "message": "Student saved successfully",
        "student": {
            "id": new_student.id,
            "name": new_student.name,
            "email": new_student.email,
            "skills": new_student.skills,
            "branch": new_student.branch,
            "year": new_student.year
        }
    }


@app.get("/students")
def get_students(db: Session = Depends(get_db)):
    return db.query(Student).all()


@app.put("/student/{student_id}")
def update_student(
    student_id: int,
    student: StudentCreate,
    db: Session = Depends(get_db)
):
    existing_student = (
        db.query(Student)
        .filter(Student.id == student_id)
        .first()
    )

    if not existing_student:
        raise HTTPException(status_code=404, detail="Student not found")

    existing_student.name = student.name
    existing_student.branch = student.branch
    existing_student.year = student.year
    existing_student.email = student.email
    existing_student.skills = student.skills

    db.commit()
    db.refresh(existing_student)

    return {
        "message": "Student updated successfully",
        "student": {
            "id": existing_student.id,
            "name": existing_student.name,
            "branch": existing_student.branch,
            "year": existing_student.year,
            "email": existing_student.email,
            "skills": existing_student.skills
        }
    }


@app.delete("/student/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    student = (
        db.query(Student)
        .filter(Student.id == student_id)
        .first()
    )

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    db.delete(student)
    db.commit()

    return {"message": "Student deleted successfully"}


@app.get("/db-test")
def db_test():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return {
            "database": "connected",
            "result": result.scalar()
        }


# Skill-gap analysis API
@app.post("/skill-gap")
def analyze_skill_gap(data: SkillGapRequest):
    student_skills = {
        skill.strip().casefold()
        for skill in data.student_skills
        if skill.strip()
    }

    required_skills = []
    seen_skills = set()

    for skill in data.required_skills:
        skill = skill.strip()
        normalized = skill.casefold()

        if skill and normalized not in seen_skills:
            required_skills.append(skill)
            seen_skills.add(normalized)

    matched_skills = [
        skill for skill in required_skills
        if skill.casefold() in student_skills
    ]

    missing_skills = [
        skill for skill in required_skills
        if skill.casefold() not in student_skills
    ]

    total_required = len(required_skills)
    match_percentage = (
        round(len(matched_skills) / total_required * 100, 2)
        if total_required else 0
    )

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_percentage": match_percentage
    }


# Career recommendations
class CareerRecommendationRequest(BaseModel):
    skills: list[str] = Field(min_length=1)

    @field_validator("skills")
    @classmethod
    def validate_skills(cls, skills):
        cleaned_skills = [
            skill.strip()
            for skill in skills
            if skill.strip()
        ]

        if not cleaned_skills:
            raise ValueError("At least one valid skill is required")

        return cleaned_skills


@app.post("/career-recommendations")
def career_recommendations(data: CareerRecommendationRequest):
    student_skills = {
        skill.strip().casefold()
        for skill in data.skills
        if skill.strip()
    }

    career_roles = {
        "Python Developer": ["Python", "SQL", "Git"],
        "Data Analyst": ["Python", "SQL", "Statistics", "Power BI"],
        "AI/ML Engineer": [
            "Python", "Machine Learning", "Statistics", "NumPy"
        ],
        "Robotics Software Engineer": [
            "Python", "C++", "ROS", "Mathematics"
        ]
    }

    recommendations = []

    for role, required_skills in career_roles.items():
        matched = [
            skill for skill in required_skills
            if skill.casefold() in student_skills
        ]

        missing = [
            skill for skill in required_skills
            if skill.casefold() not in student_skills
        ]

        score = round(len(matched) / len(required_skills) * 100, 2)

        recommendations.append({
            "career_role": role,
            "match_percentage": score,
            "matched_skills": matched,
            "missing_skills": missing
        })

    recommendations.sort(
        key=lambda role: role["match_percentage"],
        reverse=True
    )

    return {"recommendations": recommendations}



# Job creation request validation
class JobCreate(BaseModel):
    title: str = Field(min_length=2, max_length=100)
    company: str = Field(min_length=2, max_length=100)
    required_skills: str = Field(min_length=2, max_length=300)
    job_type: str = Field(min_length=2, max_length=50)
    location: str | None = None
    apply_link: HttpUrl | None = None

    @field_validator("title", "company", "required_skills", "job_type")
    @classmethod
    def reject_blank_fields(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("This field cannot be blank")

        return value

    @field_validator("location")
    @classmethod
    def clean_location(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None

    
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

def create_access_token(user_id: int, email: str):
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token



def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        user_id = int(payload.get("sub"))
    except (jwt.InvalidTokenError, TypeError, ValueError):
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise credentials_exception

    return user



@app.get("/profile")
def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "message": "Profile fetched successfully",
        "user": {
            "id": current_user.id,
            "email": current_user.email
        }
    }


@app.post("/register")
def register_user(data: UserRegister, db: Session = Depends(get_db)):
    email = str(data.email).strip().lower()

    existing_user = db.query(User).filter(
        User.email == email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email is already registered"
        )

    new_user = User(
        email=email,
        hashed_password=password_hash.hash(data.password)
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not register user. Please try again."
        )

    return {
        "message": "Registration successful",
        "user": {
            "id": new_user.id,
            "email": new_user.email
        }
    }



@app.post("/login")
def login_user(data: UserLogin, db: Session = Depends(get_db)):
    email = str(data.email).strip().lower()

    user = db.query(User).filter(User.email == email).first()

    if not user or not password_hash.verify(
        data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        user_id=user.id,
        email=user.email
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email
        }
    }




# Create job with duplicate protection
@app.post("/jobs")
def create_job(data: JobCreate, db: Session = Depends(get_db)):
    title = data.title.strip()
    company = data.company.strip()

    if not title or not company:
        raise HTTPException(
            status_code=422,
            detail="Job title and company cannot be blank"
        )

    existing_job = (
        db.query(Job)
        .filter(
            func.lower(func.trim(Job.title)) == title.casefold(),
            func.lower(func.trim(Job.company)) == company.casefold()
        )
        .first()
    )

    if existing_job:
        raise HTTPException(
            status_code=409,
            detail="This job already exists for this company"
        )

    new_job = Job(
        title=title,
        company=company,
        required_skills=data.required_skills.strip(),
        job_type=data.job_type.strip(),
        location=data.location.strip() if data.location else None,
        apply_link=str(data.apply_link) if data.apply_link else None
    )

    try:
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not save the job. Please try again."
        )

    return {
        "message": "Job created successfully",
        "job": {
            "id": new_job.id,
            "title": new_job.title,
            "company": new_job.company,
            "required_skills": new_job.required_skills,
            "job_type": new_job.job_type,
            "location": new_job.location,
            "apply_link": new_job.apply_link
        }
    }


@app.get("/jobs")
def get_jobs(db: Session = Depends(get_db)):
    return db.query(Job).all()


# Job recommendations
class JobRecommendationRequest(BaseModel):
    skills: list[str] = Field(min_length=1)


@app.post("/job-recommendations")
def recommend_jobs(
    data: JobRecommendationRequest,
    db: Session = Depends(get_db)
):
    student_skills = {
        skill.strip().casefold()
        for skill in data.skills
        if skill.strip()
    }

    jobs = db.query(Job).all()
    recommendations = []

    for job in jobs:
        required_skills = [
            skill.strip()
            for skill in job.required_skills.split(",")
            if skill.strip()
        ]

        matched_skills = [
            skill for skill in required_skills
            if skill.casefold() in student_skills
        ]

        missing_skills = [
            skill for skill in required_skills
            if skill.casefold() not in student_skills
        ]

        total_skills = len(required_skills)
        match_percentage = (
            round(len(matched_skills) / total_skills * 100, 2)
            if total_skills else 0
        )

        recommendations.append({
            "job_id": job.id,
            "title": job.title,
            "company": job.company,
            "job_type": job.job_type,
            "location": job.location,
            "apply_link": job.apply_link,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "match_percentage": match_percentage
        })

    recommendations.sort(
        key=lambda job: job["match_percentage"],
        reverse=True
    )

    return {"recommendations": recommendations}
