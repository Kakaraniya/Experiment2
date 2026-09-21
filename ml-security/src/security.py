from __future__ import annotations

import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or secrets.token_urlsafe(32)
if os.getenv("APP_ENV", "lab").lower() == "production" and len(JWT_SECRET_KEY) < 32:
    raise RuntimeError("JWT_SECRET_KEY must be set and contain at least 32 characters in production")

JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))
DEMO_USERNAME = os.getenv("DEMO_USERNAME", "student")
DEMO_PASSWORD_HASH = os.getenv(
    "DEMO_PASSWORD_HASH",
    "$argon2id$v=19$m=65536,t=3,p=4$eInGkUyIIBNaY8JGfzVp+w$KJPx/pCIWqOM6jetEFR8m+gTGxZycsHzVtROxz2aiVI",
)

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Plaintext passwords are never stored in source code; this is an Argon2id hash for the
# classroom account. Override it with DEMO_PASSWORD_HASH in a real deployment.
USERS = {
    DEMO_USERNAME: {
        "username": DEMO_USERNAME,
        "role": "student",
        "hashed_password": DEMO_PASSWORD_HASH,
    }
}


def authenticate_user(username: str, password: str) -> dict[str, str] | None:
    user = USERS.get(username)
    if not user or not password_hash.verify(password, user["hashed_password"]):
        return None
    return user


def create_access_token(username: str, role: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"sub": username, "role": role, "exp": expires_at}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict[str, str]:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")
        if not username or not role or username not in USERS:
            raise credentials_error
        return {"username": username, "role": role}
    except jwt.InvalidTokenError as exc:
        raise credentials_error from exc


def require_role(required_role: str):
    def role_dependency(user: dict[str, str] = Depends(get_current_user)) -> dict[str, str]:
        if user["role"] != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return role_dependency
