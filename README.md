
# AI Student Career Assistant

An AI-powered student career assistance project built using FastAPI, Python, and PostgreSQL. It helps students manage their profiles, identify skill gaps, explore career paths, and receive skill-based job recommendations.

## Features

- Student profile creation and management
- Student records stored in PostgreSQL
- Skill gap analysis
- Career recommendations based on skills
- Job and internship record management
- Job recommendations based on matching skills
- REST API testing through Swagger UI
- Input validation using Pydantic

## Tech Stack

- **Language:** Python
- **Backend:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Validation:** Pydantic
- **API Documentation:** Swagger UI
- **Version Control:** Git and GitHub

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/tanvikhalokar-cloud/AI-Student-Career-Assistant.git
cd AI-Student-Career-Assistant
```

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Install PostgreSQL and create the project database. Configure the database connection in `database.py` using your local PostgreSQL credentials.

Do not upload passwords or other database secrets to GitHub.

### 5. Run the application

```powershell
python -m uvicorn main:app --reload
```

### 6. Open the API documentation

Visit:

http://127.0.0.1:8000/docs

## Main API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Check the application |
| POST | `/student` | Create a student |
| GET | `/students` | List students |
| PUT | `/student/{student_id}` | Update a student |
| DELETE | `/student/{student_id}` | Delete a student |
| POST | `/skill-gap` | Analyze missing skills |
| GET | `/career-recommendations` | Explore career recommendations |
| POST | `/jobs` | Add a job |
| GET | `/jobs` | List saved jobs |
| POST | `/job-recommendations` | Recommend jobs based on skills |

## Current Limitations

Job recommendations currently use jobs saved in the project's database and compare their required skills with the student's skills. Live job scraping and external job feeds are not yet implemented.

## Future Enhancements

- Student registration and login
- Resume upload and parsing
- Live internship and job data integration
- Aptitude and interview preparation
- Student dashboard and frontend
- Deployment and automated testing

## Author

Tanvi Khalokar

## Project Status

Under active development.