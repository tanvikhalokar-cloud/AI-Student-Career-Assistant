

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_job_rejects_blank_title():
    payload = {
        "title": "   ",
        "company": "Demo Technologies",
        "required_skills": "Python, SQL",
        "job_type": "Internship",
        "location": "Remote",
        "apply_link": None,
    }

    response = client.post("/jobs", json=payload)

    assert response.status_code == 422


def test_job_rejects_blank_required_skills():
    payload = {
        "title": "Python Developer",
        "company": "Demo Technologies",
        "required_skills": "   ",
        "job_type": "Internship",
        "location": "Remote",
        "apply_link": None,
    }

    response = client.post("/jobs", json=payload)

    assert response.status_code == 422
