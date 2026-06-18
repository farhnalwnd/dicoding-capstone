"""
Authentication core module.
Handles JWT token creation/verification, password hashing, and FastAPI dependencies.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.mongodb import get_users_collection

# ====================================
# Configuration
# ====================================

_SECRET_KEY = None
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))


def _get_secret_key() -> str:
    """Lazy-load JWT_SECRET_KEY so the module can be imported without it."""
    global _SECRET_KEY
    if _SECRET_KEY is None:
        _SECRET_KEY = os.getenv("JWT_SECRET_KEY")
        if not _SECRET_KEY:
            raise RuntimeError(
                "JWT_SECRET_KEY environment variable is required. "
                "Set it before starting the server."
            )
    return _SECRET_KEY


# ====================================
# Password Hashing
# ====================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain text password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ====================================
# JWT Token
# ====================================


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token with the given data payload."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, _get_secret_key(), algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode and verify a JWT access token. Raises HTTPException on failure."""
    try:
        payload = jwt.decode(token, _get_secret_key(), algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ====================================
# FastAPI Dependencies
# ====================================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    query_token: Optional[str] = Query(None, alias="token"),
) -> dict:
    """
    FastAPI dependency that extracts and returns the current user from the JWT token.
    Raises 401 if no token is provided or if the token is invalid.
    """
    actual_token = token or query_token
    if actual_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(actual_token)
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    users = get_users_collection()
    user = users.find_one({"email": email})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "provider": user.get("provider", "email"),
    }


def require_role(*allowed_roles: str):
    """
    FastAPI dependency factory for Role-Based Access Control.
    Usage: Depends(require_role("hr")) or Depends(require_role("hr", "jobseeker"))
    """

    async def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join(allowed_roles)}",
            )
        return current_user

    return role_checker
