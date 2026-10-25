

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_job_recommendations_returns_matching_skills():
    response = client.post(
        "/job-recommendations",
        json={"skills": ["Python", "SQL"]}
    )

    assert response.status_code == 200

    data = response.json()
    assert "recommendations" in data

    recommendations = data["recommendations"]
    assert isinstance(recommendations, list)

    if recommendations:
        first_job = recommendations[0]

        assert "title" in first_job
        assert "matched_skills" in first_job
        assert "missing_skills" in first_job
        assert "match_percentage" in first_job

        assert 0 <= first_job["match_percentage"] <= 100


def test_job_recommendations_match_percentage_is_correct():
    response = client.post(
        "/job-recommendations",
        json={"skills": ["Python", "SQL"]}
    )

    assert response.status_code == 200

    recommendations = response.json()["recommendations"]

    for job in recommendations:
        matched = job["matched_skills"]
        missing = job["missing_skills"]
        total = len(matched) + len(missing)

        if total > 0:
            expected_percentage = round(len(matched) / total * 100, 2)
            assert job["match_percentage"] == expected_percentage


def test_job_recommendations_are_sorted_by_match_percentage():
    response = client.post(
        "/job-recommendations",
        json={"skills": ["Python", "SQL"]}
    )

    assert response.status_code == 200

    recommendations = response.json()["recommendations"]
    percentages = [
        job["match_percentage"] for job in recommendations
    ]

    assert percentages == sorted(percentages, reverse=True)
