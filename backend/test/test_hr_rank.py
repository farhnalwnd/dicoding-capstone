from io import BytesIO


def test_hr_rank(monkeypatch, client):

    monkeypatch.setattr(
        "app.api.hr_endpoints.extract_text",
        lambda *args, **kwargs: "Python FastAPI"
    )

    monkeypatch.setattr(
        "app.api.hr_endpoints.extract_candidate_name",
        lambda *args, **kwargs: "John Doe"
    )

    monkeypatch.setattr(
        "app.api.hr_endpoints.get_similarity_score",
        lambda *args, **kwargs: 90.0
    )

    monkeypatch.setattr(
        "app.api.hr_endpoints.match_cv_jd_hybrid",
        lambda *args, **kwargs: (["Python", "FastAPI"], ["Docker"])
    )

    files = [
        (
            "cvs",
            (
                "cv.pdf",
                BytesIO(b"dummy pdf"),
                "application/pdf"
            )
        )
    ]

    data = {
        "job_description": "Python Developer",
        "domain": "IT"
    }

    response = client.post(
        "/api/hr/rank",
        files=files,
        data=data
    )

    assert response.status_code == 200

    result = response.json()

    assert len(result) == 1
    assert result[0]["name"] == "John Doe"
    assert result[0]["score"] == 86.5  # (90 * 0.85) + (2/3 * 100 * 0.15) = 76.5 + 10 = 86.5