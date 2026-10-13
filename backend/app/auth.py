"""Small cookie-based authentication for this local assessment app."""
import base64
import hashlib
import hmac
import json
import os
import secrets
import time

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .database import get_db
from .models import User

SESSION_COOKIE = "carepoint_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 7
# Override this local-development key through APP_SECRET_KEY outside the assessment setup.
SECRET_KEY = os.getenv("APP_SECRET_KEY", "local-assessment-only-change-this-secret-key")


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return f"{salt.hex()}:{hashed.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt_hex, expected_hex = stored_hash.split(":", 1)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), 310_000)
        return hmac.compare_digest(actual.hex(), expected_hex)
    except (ValueError, TypeError):
        return False


def create_session_token(user_id: int) -> str:
    payload = json.dumps({"user_id": user_id, "expires": int(time.time()) + SESSION_MAX_AGE}, separators=(",", ":")).encode()
    encoded = base64.urlsafe_b64encode(payload).rstrip(b"=").decode()
    signature = hmac.new(SECRET_KEY.encode(), encoded.encode(), hashlib.sha256).digest()
    return f"{encoded}.{base64.urlsafe_b64encode(signature).rstrip(b'=').decode()}"


def get_current_user(
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please sign in to continue.")
    try:
        encoded, signature_text = session_token.split(".", 1)
        expected = hmac.new(SECRET_KEY.encode(), encoded.encode(), hashlib.sha256).digest()
        actual = base64.urlsafe_b64decode(signature_text + "=" * (-len(signature_text) % 4))
        if not hmac.compare_digest(actual, expected):
            raise unauthorized
        payload_bytes = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
        payload = json.loads(payload_bytes)
        if payload["expires"] < int(time.time()):
            raise unauthorized
        user = db.get(User, payload["user_id"])
        if user is None:
            raise unauthorized
        return user
    except (AttributeError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        raise unauthorized
