from bson import ObjectId
from app.core.auth import get_current_user
from datetime import datetime, timezone, timedelta
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
                "domain": "it",
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "_id": ObjectId("666fe5a3f8c24017b990050d"),
                "candidate_name": "Budi",
                "match_score": 85.0,
                "job_title": "Backend Engineer",
                "status": "hired",
                "matched_skills": ["Python"],
                "missing_skills": ["FastAPI", "Docker"],
                "domain": "it",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
            },
            {
                "_id": ObjectId("666fe5a3f8c24017b990050e"),
                "candidate_name": "Cici",
                "match_score": 75.0,
                "job_title": "HR Specialist",
                "status": "screening",
                "matched_skills": ["Recruiting"],
                "missing_skills": ["Sourcing"],
                "domain": "hr",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
            }
        ]

    def count_documents(self, query=None):
        if not query:
            return len(self.candidates)
        filtered = list(self.find(query))
        return len(filtered)

    def find(self, query=None, projection=None):
        if not query:
            return MockCursor(self.candidates)
        
        filtered = []
        for c in self.candidates:
            match = True
            for k, v in query.items():
                if k == "status":
                    if isinstance(v, dict) and "$in" in v:
                        if c.get("status") not in v["$in"]:
                            match = False
                    elif c.get("status") != v:
                        match = False
                elif k == "domain":
                    if c.get("domain") != v:
                        match = False
                elif k == "created_at":
                    if isinstance(v, dict):
                        c_date = c.get("created_at")
                        if "$gte" in v and c_date < v["$gte"]:
                            match = False
                        if "$lte" in v and c_date > v["$lte"]:
                            match = False
                        if "$lt" in v and c_date >= v["$lt"]:
                            match = False
            if match:
                filtered.append(c)
        return MockCursor(filtered)

    def aggregate(self, pipeline):
        pipeline_str = str(pipeline)
        if "$unwind" in pipeline_str:
            counts = {}
            for c in self.candidates:
                skills = c.get("matched_skills", []) + c.get("missing_skills", [])
                for s in skills:
                    counts[s] = counts.get(s, 0) + 1
            sorted_skills = sorted(counts.items(), key=lambda x: x[1], reverse=True)
            return [{"_id": skill, "count": count} for skill, count in sorted_skills]
        elif "$group" in pipeline_str:
            counts = {}
            for c in self.candidates:
                d = c.get("domain")
                counts[d] = counts.get(d, 0) + 1
            return [{"_id": d, "count": count} for d, count in counts.items()]
        return []

class MockActivityCollection:
    def __init__(self):
        self.activities = [
            {
                "candidate_id": "666fe5a3f8c24017b990050c",
                "candidate_name": "Ahmad",
                "action": "added",
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            {
                "candidate_id": "666fe5a3f8c24017b990050c",
                "candidate_name": "Ahmad",
                "action": "interview",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        ]

    def aggregate(self, pipeline):
        # Return activity timeline counts grouped by day
        timeline = {}
        for act in self.activities:
            day = act["timestamp"][:10]
            action = act["action"]
            if day not in timeline:
                timeline[day] = {"_id": {"day": day, "action": action}, "count": 1}
            else:
                timeline[day]["count"] += 1
        return list(timeline.values())

def test_hr_dashboard_stats(monkeypatch, client):
    mock_db = MockCandidatesCollection()
    monkeypatch.setattr(
        "app.services.analytics_service.get_candidates_collection",
        lambda: mock_db
    )

    response = client.get("/api/hr-dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "counts" in data
    assert data["counts"]["total_candidates"] == 3
    assert data["counts"]["interview"] == 1
    assert "scores" in data
    assert data["scores"]["highest"] == 90.0

def test_hr_dashboard_funnel(monkeypatch, client):
    mock_db = MockCandidatesCollection()
    monkeypatch.setattr(
        "app.services.analytics_service.get_candidates_collection",
        lambda: mock_db
    )

    response = client.get("/api/hr-dashboard/funnel")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    assert data[0]["stage"] == "Applicants"
    assert data[0]["count"] == 3

def test_hr_dashboard_skills(monkeypatch, client):
    mock_db = MockCandidatesCollection()
    monkeypatch.setattr(
        "app.services.analytics_service.get_candidates_collection",
        lambda: mock_db
    )

    response = client.get("/api/hr-dashboard/skills")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["skill"] == "Python"
    assert data[0]["count"] == 2

def test_hr_dashboard_categories(monkeypatch, client):
    mock_db = MockCandidatesCollection()
    monkeypatch.setattr(
        "app.services.analytics_service.get_candidates_collection",
        lambda: mock_db
    )

    response = client.get("/api/hr-dashboard/categories")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

def test_hr_dashboard_timeline(monkeypatch, client):
    mock_act = MockActivityCollection()
    monkeypatch.setattr(
        "app.services.analytics_service.get_activity_collection",
        lambda: mock_act
    )

    response = client.get("/api/hr-dashboard/timeline")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

def test_hr_dashboard_role_protection(monkeypatch, client):
    from app.main import app
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "mock_jobseeker_id",
        "name": "Mock Jobseeker",
        "email": "seeker@example.com",
        "role": "jobseeker",
        "provider": "email"
    }

    try:
        response = client.get("/api/hr-dashboard/stats")
        assert response.status_code == 403
    finally:
        app.dependency_overrides[get_current_user] = lambda: {
            "id": "mock_user_id",
            "name": "Mock User",
            "email": "mock@example.com",
            "role": "hr",
            "provider": "email"
        }
