from fastapi import FastAPI, Depends
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import engine, Base, get_db
from models import Student


app = FastAPI()

Base.metadata.create_all(bind=engine)


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
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
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
def update_student(student_id: int, student: StudentCreate, db: Session = Depends(get_db)):
    existing_student = db.query(Student).filter(Student.id == student_id).first()

    if not existing_student:
        return {"message": "Student not found"}

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
            "skills": existing_student.skills,
        }
    }
@app.delete("/student/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()

    if not student:
        return {"message": "Student not found"}

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