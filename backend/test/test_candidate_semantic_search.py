from io import BytesIO
import torch

def test_candidate_semantic_search_json(monkeypatch, client):
    # Mock SentenceTransformer encode method
    monkeypatch.setattr(
        "app.api.endpoints.model.encode",
        lambda *args, **kwargs: torch.tensor([0.1] * 384)
    )

    response = client.post(
        "/api/jobs/semantic-search",
        json={"query": "Python developer"}
    )

    assert response.status_code == 200
    res_data = response.json()
    assert "results" in res_data
    assert len(res_data["results"]) > 0
    assert "candidate_name" in res_data["results"][0]
    assert "similarity_score" in res_data["results"][0]
    assert "skills" in res_data["results"][0]

def test_candidate_semantic_search_form(monkeypatch, client):
    monkeypatch.setattr(
        "app.api.endpoints.model.encode",
        lambda *args, **kwargs: torch.tensor([0.1] * 384)
    )

    response = client.post(
        "/api/jobs/semantic-search",
        data={"query": "Machine Learning"}
    )

    assert response.status_code == 200
    res_data = response.json()
    assert "results" in res_data
    assert len(res_data["results"]) > 0

def test_legacy_job_semantic_search(monkeypatch, client):
    def mock_extract_text(*args, **kwargs):
        return "Python FastAPI"

    class MockCollection:
        def find(self, query):
            return [
                {
                    "title": "Backend Developer",
                    "company": "ABC",
                    "location": "Jakarta",
                    "url": "http://example.com",
                    "description_embedding": [0.1] * 384
                }
            ]

    monkeypatch.setattr(
        "app.api.endpoints.extract_text",
        mock_extract_text
    )

    monkeypatch.setattr(
        "app.api.endpoints.model.encode",
        lambda *args, **kwargs: torch.tensor([0.1] * 384)
    )

    monkeypatch.setattr(
        "app.api.endpoints.get_jobs_collection",
        lambda: MockCollection()
    )

    files = {
        "cv": (
            "cv.pdf",
            BytesIO(b"dummy"),
            "application/pdf"
        )
    }

    response = client.post(
        "/api/jobs/semantic-search",
        files=files
    )

    assert response.status_code == 200
    res_data = response.json()
    assert isinstance(res_data, list)
    assert len(res_data) > 0
    assert "title" in res_data[0]
    assert "score" in res_data[0]
