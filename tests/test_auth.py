

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_profile_without_token():
    response = client.get("/profile")

    assert response.status_code == 401


def test_profile_with_invalid_token():
    headers = {
        "Authorization": "Bearer invalid.token.value"
    }

    response = client.get("/profile", headers=headers)

    assert response.status_code == 401
