

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_career_recommendations_returns_all_roles():
    response = client.post(
        "/career-recommendations",
        json={"skills": ["Python", "SQL", "Git"]}
    )

    assert response.status_code == 200

    data = response.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) == 4


def test_career_recommendations_sorted_by_match_percentage():
    response = client.post(
        "/career-recommendations",
        json={"skills": ["Python", "SQL", "Git"]}
    )

    assert response.status_code == 200

    recommendations = response.json()["recommendations"]
    percentages = [
        role["match_percentage"] for role in recommendations
    ]

    assert percentages == sorted(percentages, reverse=True)


def test_career_recommendations_match_percentage_is_correct():
    response = client.post(
        "/career-recommendations",
        json={"skills": ["Python", "SQL", "Git"]}
    )

    assert response.status_code == 200

    recommendations = response.json()["recommendations"]

    for role in recommendations:
        matched = role["matched_skills"]
        missing = role["missing_skills"]
        total = len(matched) + len(missing)

        expected_percentage = round(len(matched) / total * 100, 2)

        assert role["match_percentage"] == expected_percentage



def test_career_recommendations_with_empty_skills():
    response = client.post(
        "/career-recommendations",
        json={"skills": []}
    )

    assert response.status_code == 422

def test_career_recommendations_rejects_blank_skills():
    response = client.post(
        "/career-recommendations",
        json={"skills": ["   "]}
    )

    assert response.status_code == 422