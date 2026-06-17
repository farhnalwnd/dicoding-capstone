from bson import ObjectId
from app.core.auth import get_current_user
from datetime import datetime, timezone
from typing import List, Dict, Any

class MockCursor:
    def __init__(self, data):
        self.data = data

    def sort(self, *args, **kwargs):
        return self

    def __iter__(self):
        return iter(self.data)

class MockCandidatesCollection:
    def __init__(self):
        self.candidates = [
            {
                "_id": ObjectId("666fe5a3f8c24017b990050c"),
                "candidate_name": "Ahmad",
                "match_score": 90.0,
                "job_title": "Python Developer",
                "status": "screening",
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "_id": ObjectId("666fe5a3f8c24017b990050d"),
                "candidate_name": "Budi",
                "match_score": 85.0,
                "job_title": "Backend Engineer",
                "status": "talent_pool",
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "_id": ObjectId("666fe5a3f8c24017b990050e"),
                "candidate_name": "Citra",
                "match_score": 95.0,
                "job_title": "Frontend Developer",
                "status": "talent_pool",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        ]

    def find(self, query=None):
        if query is None:
            return MockCursor(self.candidates)
        
        filtered = []
        for c in self.candidates:
            match = True
            for k, v in query.items():
                if c.get(k) != v:
                    match = False
                    break
            if match:
                filtered.append(c)
        return MockCursor(filtered)

    def find_one(self, query):
        for c in self.candidates:
            if all(c.get(k) == v for k, v in query.items()):
                return c
        return None

    def update_one(self, filter_query, update_query):
        obj_id = filter_query.get("_id")
        set_fields = update_query.get("$set", {})
        
        matched_count = 0
        for c in self.candidates:
            if c["_id"] == obj_id:
                c.update(set_fields)
                matched_count = 1
                break
                
        class MockUpdateResult:
            def __init__(self, count):
                self.matched_count = count
        return MockUpdateResult(matched_count)

    def count_documents(self, query=None):
        if not query:
            return len(self.candidates)
        count = 0
        for c in self.candidates:
            match = True
            for k, v in query.items():
                if c.get(k) != v:
                    match = False
                    break
            if match:
                count += 1
        return count


def test_get_candidates(monkeypatch, client):
    mock_db = MockCandidatesCollection()
    monkeypatch.setattr(
        "app.api.hr_endpoints.get_candidates_collection",
        lambda: mock_db
    )

    response = client.get("/api/candidates")
    assert response.status_code == 200
    res_data = response.json()
    assert len(res_data) == 3
    assert res_data[0]["candidate_name"] == "Ahmad"
    assert "id" in res_data[0]


def test_get_talent_pool(monkeypatch, client):
    mock_db = MockCandidatesCollection()
    monkeypatch.setattr(
        "app.api.hr_endpoints.get_candidates_collection",
        lambda: mock_db
    )

    response = client.get("/api/talent-pool")
    assert response.status_code == 200
    res_data = response.json()
    assert len(res_data) == 2
    assert all(c["status"] == "talent_pool" for c in res_data)


def test_patch_candidate_status(monkeypatch, client):
    mock_db = MockCandidatesCollection()
    monkeypatch.setattr(
        "app.api.hr_endpoints.get_candidates_collection",
        lambda: mock_db
    )

    response = client.patch(
        "/api/candidates/666fe5a3f8c24017b990050d/status",
        json={"status": "interview"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert mock_db.candidates[1]["status"] == "interview"


def test_patch_candidate_status_invalid_fields(monkeypatch, client):
    response = client.patch(
        "/api/candidates/666fe5a3f8c24017b990050d/status",
        json={"status": "invalid_status_name"}
    )
    assert response.status_code == 422


def test_patch_candidate_status_not_found(monkeypatch, client):
    mock_db = MockCandidatesCollection()
    monkeypatch.setattr(
        "app.api.hr_endpoints.get_candidates_collection",
        lambda: mock_db
    )

    response = client.patch(
        "/api/candidates/666fe5a3f8c24017b990050f/status",
        json={"status": "interview"}
    )
    assert response.status_code == 404


def test_get_hr_stats(monkeypatch, client):
    mock_db = MockCandidatesCollection()
    monkeypatch.setattr(
        "app.api.hr_endpoints.get_candidates_collection",
        lambda: mock_db
    )

    response = client.get("/api/dashboard/hr-stats")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["total_candidates"] == 3
    assert res_data["screening"] == 1
    assert res_data["talent_pool"] == 2
    assert res_data["interview"] == 0
    assert res_data["rejected"] == 0


def test_role_protection(monkeypatch, client):
    from app.main import app
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "mock_jobseeker_id",
        "name": "Mock Jobseeker",
        "email": "seeker@example.com",
        "role": "jobseeker",
        "provider": "email"
    }

    try:
        response = client.get("/api/talent-pool")
        assert response.status_code == 403
        
        response = client.patch(
            "/api/candidates/666fe5a3f8c24017b990050d/status",
            json={"status": "interview"}
        )
        assert response.status_code == 403
    finally:
        # Reset overrides back to default mock hr
        app.dependency_overrides[get_current_user] = lambda: {
            "id": "mock_user_id",
            "name": "Mock User",
            "email": "mock@example.com",
            "role": "hr",
            "provider": "email"
        }
