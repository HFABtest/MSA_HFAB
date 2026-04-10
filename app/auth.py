"""
Session-based authentication middleware.

Uses signed cookies via itsdangerous. No external dependencies.
"""

import secrets
from fastapi import Request, HTTPException
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

SECRET_KEY = None
SERIALIZER = None
SESSION_MAX_AGE = 60 * 60 * 24 * 7  # 7 days
COOKIE_NAME = "mognad_session"


def init_auth(secret_key: str = None):
    global SECRET_KEY, SERIALIZER
    SECRET_KEY = secret_key or secrets.token_hex(32)
    SERIALIZER = URLSafeTimedSerializer(SECRET_KEY)


def create_session_token(user_id: int, role: str) -> str:
    return SERIALIZER.dumps({"uid": user_id, "role": role})


def verify_session_token(token: str) -> dict | None:
    try:
        data = SERIALIZER.loads(token, max_age=SESSION_MAX_AGE)
        return data
    except (BadSignature, SignatureExpired):
        return None


def get_current_user(request: Request) -> dict | None:
    """Extract user from session cookie. Returns {"uid": int, "role": str} or None."""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    return verify_session_token(token)


def require_auth(request: Request) -> dict:
    """Raise 401 if not authenticated."""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


def require_admin(request: Request) -> dict:
    """Raise 403 if not admin."""
    user = require_auth(request)
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
