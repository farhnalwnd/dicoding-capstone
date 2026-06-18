"""
Authentication API endpoints.
Handles user registration, login (email + Google OAuth), and user profile.
"""

import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from pymongo.errors import DuplicateKeyError

from app.core.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.core.mongodb import get_users_collection

router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "YOUR_GOOGLE_CLIENT_ID")

# --------------- Constants ---------------
NAME_MAX_LENGTH = 100
PASSWORD_MAX_LENGTH = 128


# ====================================
# Request / Response Models
# ====================================


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=NAME_MAX_LENGTH)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=PASSWORD_MAX_LENGTH)
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
    needs_role_selection: bool = False


# ====================================
# Private Helpers
# ====================================


def _check_user_disabled(user: dict) -> None:
    """Raise HTTP 403 if the user account is disabled."""
    if user.get("disabled", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been disabled. Please contact an administrator.",
        )


def _login_existing_google_user(user: dict) -> AuthResponse:
    """Build an AuthResponse for an existing Google-authenticated user."""
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


def _register_new_google_user(name: str, email: str, users) -> AuthResponse:
    """Register a new Google-authenticated user (role pending selection)."""
    user_doc = {
        "name": name,
        "email": email,
        "password": None,
        "role": None,
        "provider": "google",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        result = users.insert_one(user_doc)
    except DuplicateKeyError:
        # Race condition: another request created the user
        user = users.find_one({"email": email})
        token = create_access_token(
            data={"sub": user["email"], "role": user.get("role")}
        )
        return AuthResponse(
            access_token=token,
            user={
                "id": str(user["_id"]),
                "name": user["name"],
                "email": user["email"],
                "role": user.get("role"),
                "provider": user.get("provider", "google"),
            },
            needs_role_selection=user.get("role") is None,
        )

    token = create_access_token(data={"sub": email, "role": None})
    return AuthResponse(
        access_token=token,
        user={
            "id": str(result.inserted_id),
            "name": name,
            "email": email,
            "role": None,
            "provider": "google",
        },
        needs_role_selection=True,
    )


# ====================================
# Endpoints
# ====================================


@router.post(
    "/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED
)
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
    _check_user_disabled(user)

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
        from google.auth.transport import requests as google_requests
        from google.oauth2 import id_token

        idinfo = id_token.verify_oauth2_token(
            data.credential,
            google_requests.Request(),
            GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=10,
        )
    except ValueError as e:
        print(f"[AUTH] Google token ValueError: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {str(e)}",
        )
    except Exception as e:
        print(f"[AUTH] Google auth exception: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Google authentication failed: {str(e)}",
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
        return _login_existing_google_user(user)
    else:
        # New user — register WITHOUT a role (pending selection)
        return _register_new_google_user(name, email, users)


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get the current authenticated user's profile."""
    return current_user


class SetRoleRequest(BaseModel):
    role: str = Field(..., pattern="^(hr|jobseeker)$")


@router.post("/set-role", response_model=AuthResponse)
async def set_role(
    data: SetRoleRequest, current_user: dict = Depends(get_current_user)
):
    """
    Set the role for a new Google-registered user who hasn't chosen one yet.
    """
    users = get_users_collection()
    email = current_user["email"]
    user = users.find_one({"email": email})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    if user.get("role") is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role has already been set.",
        )

    users.update_one({"email": email}, {"$set": {"role": data.role}})

    token = create_access_token(data={"sub": email, "role": data.role})

    return AuthResponse(
        access_token=token,
        user={
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "role": data.role,
            "provider": user.get("provider", "google"),
        },
    )
