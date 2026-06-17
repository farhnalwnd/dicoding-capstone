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
                "status": "interview",
                "matched_skills": ["Python", "FastAPI"],
                "missing_skills": ["Docker"],
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "_id": ObjectId("666fe5a3f8c24017b990050d"),
                "candidate_name": "Budi",
                "match_score": 85.0,
                "job_title": "Backend Engineer",
                "status": "interview",
                "interview_status": "scheduled",
                "interview_date": "2026-06-20",
                "interview_time": "10:00 AM",
                "meeting_link": "https://meet.google.com/abc-defg-hij",
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
        obj_id = query.get("_id")
        for c in self.candidates:
            if c["_id"] == obj_id:
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


def test_get_interviews(monkeypatch, client):
    mock_db = MockCandidatesCollection()
    monkeypatch.setattr(
        "app.api.hr_endpoints.get_candidates_collection",
        lambda: mock_db
    )

    response = client.get("/api/interviews")
    assert response.status_code == 200
    res_data = response.json()
    assert len(res_data) == 2
    assert res_data[0]["candidate_name"] == "Ahmad"
    assert res_data[0]["interview_status"] == "pending"
    assert res_data[1]["candidate_name"] == "Budi"
    assert res_data[1]["interview_status"] == "scheduled"


def test_schedule_candidate_interview(monkeypatch, client):
    mock_db = MockCandidatesCollection()
    monkeypatch.setattr(
        "app.api.hr_endpoints.get_candidates_collection",
        lambda: mock_db
    )

    response = client.post(
        "/api/candidates/666fe5a3f8c24017b990050c/schedule",
        json={
            "date": "2026-06-25",
            "time": "02:00 PM",
            "meeting_link": "https://meet.google.com/xyz-pdqr-wuv"
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    # Check that document was updated
    candidate = mock_db.candidates[0]
    assert candidate["interview_status"] == "scheduled"
    assert candidate["interview_date"] == "2026-06-25"
    assert candidate["interview_time"] == "02:00 PM"
    assert candidate["meeting_link"] == "https://meet.google.com/xyz-pdqr-wuv"


def test_generate_candidate_questions(monkeypatch, client):
    mock_db = MockCandidatesCollection()
    monkeypatch.setattr(
        "app.api.hr_endpoints.get_candidates_collection",
        lambda: mock_db
    )

    response = client.post("/api/candidates/666fe5a3f8c24017b990050c/generate-questions")
    assert response.status_code == 200
    res_data = response.json()
    assert "questions" in res_data
    assert len(res_data["questions"]) > 0
    assert "Python" in res_data["questions"][0]
    
    # Check stored in database
    assert "interview_questions" in mock_db.candidates[0]
    assert len(mock_db.candidates[0]["interview_questions"]) > 0


def test_interview_scheduler_role_protection(monkeypatch, client):
    from app.main import app
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "mock_jobseeker_id",
        "name": "Mock Jobseeker",
        "email": "seeker@example.com",
        "role": "jobseeker",
        "provider": "email"
    }

    try:
        response = client.get("/api/interviews")
        assert response.status_code == 403
        
        response = client.post(
            "/api/candidates/666fe5a3f8c24017b990050c/schedule",
            json={
                "date": "2026-06-25",
                "time": "02:00 PM",
                "meeting_link": "https://meet.google.com/xyz-pdqr-wuv"
            }
        )
        assert response.status_code == 403
        
        response = client.post("/api/candidates/666fe5a3f8c24017b990050c/generate-questions")
        assert response.status_code == 403
    finally:
        app.dependency_overrides[get_current_user] = lambda: {
            "id": "mock_user_id",
            "name": "Mock User",
            "email": "mock@example.com",
            "role": "hr",
            "provider": "email"
        }
