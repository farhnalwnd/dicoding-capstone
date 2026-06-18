from io import BytesIO


class MockInsertResult:
    inserted_id = "mock_candidate_id"


class MockCandidatesCollection:
    def insert_one(self, doc):
        return MockInsertResult()


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
        lambda *args, **kwargs: (["Python", "FastAPI"], ["Docker"], {"Python": 100.0, "FastAPI": 100.0, "Docker": 0.0})
    )

    monkeypatch.setattr(
        "app.api.hr_endpoints.get_candidates_collection",
        lambda: MockCandidatesCollection()
    )

    monkeypatch.setattr(
        "app.api.hr_endpoints.log_activity",
        lambda *args, **kwargs: None
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
    assert result[0]["score"] == 66.25  # 70% Semantic (63.0) + 10% Effective Coverage (2.5) + 20% Domain Relevance (0.75)