

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_login_with_unregistered_email():
    response = client.post(
        "/login",
        json={
            "email": "nobody.unknown.2026@example.com",
            "password": "WrongPassword123!"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"



def test_login_with_wrong_password():
    response = client.post(
        "/login",
        json={
            "email": "tanvi.signup@example.com",
            "password": "DefinitelyWrongPassword123!"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"
