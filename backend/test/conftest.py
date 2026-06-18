import os
import sys
from pathlib import Path

# Set dummy environment variables for testing BEFORE importing the app
os.environ["MONGO_URI"] = "mongodb://localhost:27017"
os.environ["JWT_SECRET_KEY"] = "dummy_test_secret_key_12345"
os.environ["JWT_ALGORITHM"] = "HS256"

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.core.auth import get_current_user  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def client():
    # Setup mock user to bypass auth in existing tests
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "mock_user_id",
        "name": "Mock User",
        "email": "mock@example.com",
        "role": "hr",
        "provider": "email",
    }
    yield TestClient(app)
    # Clean up overrides
    app.dependency_overrides = {}
