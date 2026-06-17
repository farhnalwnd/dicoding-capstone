import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app.core.auth import hash_password
from app.main import app

@pytest.fixture
def client():
    app.dependency_overrides = {}
    return TestClient(app)


class MockCollection:
    def __init__(self):
        self.users = []

    def find_one(self, query):
        for u in self.users:
            if all(u.get(k) == v for k, v in query.items()):
                return u
        return None

    def insert_one(self, doc):
        email = doc.get("email")
        if self.find_one({"email": email}):
            from pymongo.errors import DuplicateKeyError
            raise DuplicateKeyError("Duplicate email")
        
        doc["_id"] = "mock_user_id"
        self.users.append(doc)
        
        class InsertResult:
            inserted_id = doc["_id"]
        return InsertResult()

    def create_index(self, *args, **kwargs):
        pass

    def update_one(self, query, update_dict):
        user = self.find_one(query)
        if user and "$set" in update_dict:
            user.update(update_dict["$set"])
        class UpdateResult:
            modified_count = 1 if user else 0
        return UpdateResult()

@pytest.fixture
def mock_db(monkeypatch):
    mock_coll = MockCollection()
    # Pre-populate with one user
    mock_coll.users.append({
        "_id": "existing_user_id",
        "name": "Existing User",
        "email": "existing@example.com",
        "password": hash_password("password123"),
        "role": "hr",
        "provider": "email"
    })
    
    monkeypatch.setattr("app.api.auth_endpoints.get_users_collection", lambda: mock_coll)
    monkeypatch.setattr("app.core.auth.get_users_collection", lambda: mock_coll)
    return mock_coll

def test_register_success(mock_db, client):
    payload = {
        "name": "New Candidate",
        "email": "new@example.com",
        "password": "securepassword",
        "role": "jobseeker"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    
    data = response.json()
    assert "access_token" in data
    assert data["user"]["name"] == "New Candidate"
    assert data["user"]["email"] == "new@example.com"
    assert data["user"]["role"] == "jobseeker"

def test_register_duplicate_email(mock_db, client):
    payload = {
        "name": "Dupe User",
        "email": "existing@example.com",
        "password": "securepassword",
        "role": "hr"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "already registered" in response.json()["detail"]

def test_login_success(mock_db, client):
    payload = {
        "email": "existing@example.com",
        "password": "password123"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "existing@example.com"
    assert data["user"]["role"] == "hr"

def test_login_invalid_credentials(mock_db, client):
    payload = {
        "email": "existing@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid email or password" in response.json()["detail"]

def test_get_me_success(mock_db, client):
    # Log in first to get a token
    login_response = client.post("/api/auth/login", json={
        "email": "existing@example.com",
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["email"] == "existing@example.com"
    assert data["role"] == "hr"

def test_get_me_unauthorized(mock_db, client):
    response = client.get("/api/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
