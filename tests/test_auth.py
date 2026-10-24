

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

def test_profile_with_expired_token():
    import jwt
    from datetime import datetime, timedelta, timezone
    from main import SECRET_KEY

    expired_payload = {
        "sub": "1",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=5),
    }

    expired_token = jwt.encode(
        expired_payload,
        SECRET_KEY,
        algorithm="HS256",
    )

    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/profile", headers=headers)

    assert response.status_code == 401

def test_register_with_duplicate_email():
    import uuid

    email = f"test_{uuid.uuid4().hex[:10]}@example.com"
    payload = {
        "name": "Test User",
        "email": email,
        "password": "StrongPassword123!"
    }

    first_response = client.post("/register", json=payload)
    assert first_response.status_code in (200, 201)

    second_response = client.post("/register", json=payload)
    assert second_response.status_code == 409    