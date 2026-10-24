

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_student_rejects_invalid_email():
    payload = {
        "name": "Test Student",
        "email": "invalid-email",
        "skills": "Python, SQL",
        "branch": "Robotics and AI",
        "year": 3,
    }

    response = client.post("/student", json=payload)

    assert response.status_code == 422


def test_student_rejects_invalid_year():
    payload = {
        "name": "Test Student",
        "email": "validation.test@example.com",
        "skills": "Python, SQL",
        "branch": "Robotics and AI",
        "year": 5,
    }

    response = client.post("/student", json=payload)

    assert response.status_code == 422
