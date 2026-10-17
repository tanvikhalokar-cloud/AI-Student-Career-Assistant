from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import engine, Base, get_db
from models import Student,Job


app = FastAPI()

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
            raise ValueError(
                "Skills cannot be empty or only spaces"
            )
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
    students = db.query(Student).all()
    return students


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
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

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
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

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


# Skill-Gap Analysis API
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

        score = round(
            len(matched) / len(required_skills) * 100, 2
        )

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

class JobCreate(BaseModel):
    title: str = Field(min_length=2, max_length=100)
    company: str = Field(min_length=2, max_length=100)
    required_skills: str = Field(min_length=2, max_length=300)
    job_type: str = Field(min_length=2, max_length=50)
    location: str | None = None
    apply_link: str | None = None


@app.post("/jobs")
def create_job(data: JobCreate, db: Session = Depends(get_db)):
    new_job = Job(
        title=data.title,
        company=data.company,
        required_skills=data.required_skills,
        job_type=data.job_type,
        location=data.location,
        apply_link=data.apply_link
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

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
