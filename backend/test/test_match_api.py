from io import BytesIO


def test_match_detailed(monkeypatch, client):

    def mock_extract_text(*args, **kwargs):
        return """
        Python Developer
        Python FastAPI Docker MongoDB
        """

    def mock_analyze(*args, **kwargs):
        return {
            "match_score": 90,
            "recommendation": "Strong Match",
            "matched_skills": [
                "Python",
                "FastAPI"
            ],
            "missing_skills": []
        }

    monkeypatch.setattr(
        "app.api.endpoints.extract_text",
        mock_extract_text
    )

    monkeypatch.setattr(
        "app.api.endpoints.analyze_cv_jd",
        mock_analyze
    )

    files = {
        "cv": (
            "cv.pdf",
            BytesIO(b"dummy pdf"),
            "application/pdf"
        )
    }

    data = {
        "job_description": "Python Developer",
        "domain": "IT"
    }

    response = client.post(
        "/api/match-detailed",
        files=files,
        data=data
    )

    assert response.status_code == 200

    result = response.json()

    assert result["match_score"] == 90
    assert result["recommendation"] == "Strong Match"