"""Password hashing, JWT creation, and tenant-aware authorization helpers."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import os
import secrets
from typing import Optional

import bcrypt
import jwt
from fastapi import Cookie, Depends, Header, HTTPException, status


JWT_SECRET = os.getenv("JWT_SECRET_KEY", "marotrade-dev-secret-change-me-before-production-2026")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES", "60"))
REMEMBER_TOKEN_DAYS = int(os.getenv("REMEMBER_TOKEN_DAYS", "30"))


@dataclass(frozen=True)
class AuthContext:
    user_id: str
    organization_id: str
    membership_role: str
    email: str


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(
    *,
    user_id: str,
    organization_id: str,
    membership_role: str,
    email: str,
    remember: bool = False,
) -> tuple[str, int]:
    now = datetime.now(timezone.utc)
    lifetime = timedelta(days=REMEMBER_TOKEN_DAYS) if remember else timedelta(minutes=ACCESS_TOKEN_MINUTES)
    expires_at = now + lifetime
    payload = {
        "sub": user_id,
        "org": organization_id,
        "role": membership_role,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "type": "access",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM), int(lifetime.total_seconds())


def decode_access_token(token: str) -> AuthContext:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise ValueError("invalid token type")
        return AuthContext(
            user_id=str(payload["sub"]),
            organization_id=str(payload["org"]),
            membership_role=str(payload["role"]),
            email=str(payload["email"]),
        )
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session invalide ou expirée.",
        ) from exc


def generate_one_time_token() -> tuple[str, str]:
    raw = secrets.token_urlsafe(32)
    return raw, hashlib.sha256(raw.encode("utf-8")).hexdigest()


def hash_one_time_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _extract_token(authorization: Optional[str], access_token: Optional[str]) -> Optional[str]:
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1].strip()
    return access_token


async def get_current_auth(
    authorization: Optional[str] = Header(default=None),
    access_token: Optional[str] = Cookie(default=None),
) -> AuthContext:
    token = _extract_token(authorization, access_token)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentification requise.")
    return decode_access_token(token)


def require_roles(*roles: str):
    async def dependency(auth: AuthContext = Depends(get_current_auth)) -> AuthContext:
        if auth.membership_role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Droits insuffisants.")
        return auth

    return dependency
