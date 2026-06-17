from io import BytesIO


def test_semantic_search(monkeypatch, client):

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

    import torch

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