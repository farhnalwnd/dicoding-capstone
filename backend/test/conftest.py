import sys
from pathlib import Path

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.auth import get_current_user

@pytest.fixture
def client():
    # Setup mock user to bypass auth in existing tests
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "mock_user_id",
        "name": "Mock User",
        "email": "mock@example.com",
        "role": "hr",
        "provider": "email"
    }
    yield TestClient(app)
    # Clean up overrides
    app.dependency_overrides = {}
