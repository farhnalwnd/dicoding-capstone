"""
Authentication API endpoints.
Handles user registration, login (email + Google OAuth), and user profile.
"""

import os
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field
from pymongo.errors import DuplicateKeyError

from app.core.mongodb import get_users_collection
from app.core.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "YOUR_GOOGLE_CLIENT_ID")


# ====================================
# Request / Response Models
# ====================================

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    role: str = Field(..., pattern="^(hr|jobseeker)$")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleAuthRequest(BaseModel):
    credential: str  # Google ID token from frontend


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


# ====================================
# Endpoints
# ====================================

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest):
    """Register a new user with email and password."""
    users = get_users_collection()

    # Check if user already exists
    existing = users.find_one({"email": data.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered. Please login instead.",
        )

    user_doc = {
        "name": data.name,
        "email": data.email,
        "password": hash_password(data.password),
        "role": data.role,
        "provider": "email",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        result = users.insert_one(user_doc)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered. Please login instead.",
        )

    token = create_access_token(data={"sub": data.email, "role": data.role})

    return AuthResponse(
        access_token=token,
        user={
            "id": str(result.inserted_id),
            "name": data.name,
            "email": data.email,
            "role": data.role,
            "provider": "email",
        },
    )


@router.post("/login", response_model=AuthResponse)
async def login(data: LoginRequest):
    """Login with email and password."""
    users = get_users_collection()
    user = users.find_one({"email": data.email})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    # Check if user registered via Google (no password)
    if not user.get("password"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This account uses Google Sign-In. Please login with Google.",
        )

    if not verify_password(data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    # Check if user is disabled
    if user.get("disabled", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been disabled. Please contact an administrator.",
        )

    # Record last login timestamp
    now_iso = datetime.now(timezone.utc).isoformat()
    users.update_one({"email": data.email}, {"$set": {"last_login": now_iso}})

    token = create_access_token(data={"sub": user["email"], "role": user["role"]})

    return AuthResponse(
        access_token=token,
        user={
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "provider": user.get("provider", "email"),
        },
    )


@router.post("/google", response_model=AuthResponse)
async def google_auth(data: GoogleAuthRequest):
    """
    Authenticate with Google OAuth.
    Receives a Google ID token from the frontend, verifies it,
    and creates or retrieves the user account.
    """
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests

        idinfo = id_token.verify_oauth2_token(
            data.credential,
            google_requests.Request(),
            GOOGLE_CLIENT_ID,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token.",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google authentication failed. Please try again.",
        )

    email = idinfo.get("email")
    name = idinfo.get("name", email.split("@")[0] if email else "User")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account has no email address.",
        )

    users = get_users_collection()
    user = users.find_one({"email": email})

    if user:
        # Existing user — login
        token = create_access_token(data={"sub": user["email"], "role": user["role"]})
        return AuthResponse(
            access_token=token,
            user={
                "id": str(user["_id"]),
                "name": user["name"],
                "email": user["email"],
                "role": user["role"],
                "provider": user.get("provider", "google"),
            },
        )
    else:
        # New user — register with default role "jobseeker"
        user_doc = {
            "name": name,
            "email": email,
            "password": None,
            "role": "jobseeker",
            "provider": "google",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        try:
            result = users.insert_one(user_doc)
        except DuplicateKeyError:
            # Race condition: another request created the user
            user = users.find_one({"email": email})
            token = create_access_token(data={"sub": user["email"], "role": user["role"]})
            return AuthResponse(
                access_token=token,
                user={
                    "id": str(user["_id"]),
                    "name": user["name"],
                    "email": user["email"],
                    "role": user["role"],
                    "provider": user.get("provider", "google"),
                },
            )

        token = create_access_token(data={"sub": email, "role": "jobseeker"})
        return AuthResponse(
            access_token=token,
            user={
                "id": str(result.inserted_id),
                "name": name,
                "email": email,
                "role": "jobseeker",
                "provider": "google",
            },
        )


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get the current authenticated user's profile."""
    return current_user
