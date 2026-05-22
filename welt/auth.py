"""Auth-Utilities: bcrypt + JWT für das Menschenprofil-System."""

import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path

import bcrypt
import jwt

_SECRET_FILE = Path(__file__).parent / ".jwt_secret"
_TOKEN_DAYS = 7
_ALGORITHM = "HS256"


def _load_secret() -> str:
    env = os.environ.get("WELT_JWT_SECRET")
    if env:
        return env
    if _SECRET_FILE.exists():
        return _SECRET_FILE.read_text(encoding="utf-8").strip()
    secret = secrets.token_hex(32)
    _SECRET_FILE.write_text(secret, encoding="utf-8")
    _SECRET_FILE.chmod(0o600)
    return secret


_SECRET = _load_secret()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), hash.encode())


def create_token(user_id: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(days=_TOKEN_DAYS),
    }
    return jwt.encode(payload, _SECRET, algorithm=_ALGORITHM)


def verify_token(token: str) -> dict:
    decoded = jwt.decode(token, _SECRET, algorithms=[_ALGORITHM])
    return {
        "user_id": decoded.get("user_id") or decoded["sub"],
        "role": decoded["role"],
        "username": decoded["sub"],
    }
