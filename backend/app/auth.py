"""
RailFLOW — Auth Utilities.

Password hashing + token creation/verification.
Zero external dependencies — uses only Python stdlib.
"""

import hashlib
import hmac
import secrets
import json
import time
import base64

SECRET_KEY = "railflow-hackathon-2026-secret"


# ── Password Hashing ─────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash password with random salt. Returns 'salt:hash'."""
    salt = secrets.token_hex(16)
    h = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{h}"


def verify_password(password: str, stored: str) -> bool:
    """Verify password against stored 'salt:hash'."""
    salt, h = stored.split(":", 1)
    return hashlib.sha256((password + salt).encode()).hexdigest() == h


# ── Token (HMAC-signed JSON — like JWT but zero deps) ────────

def create_token(user_id: str, role: str) -> str:
    """Create a signed token. Expires in 24 hours."""
    payload = json.dumps({
        "user_id": user_id,
        "role": role,
        "exp": time.time() + 86400,
    })
    payload_b64 = base64.urlsafe_b64encode(payload.encode()).decode()
    sig = hmac.new(SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{sig}"


def decode_token(token: str) -> dict | None:
    """Decode and verify a token. Returns payload dict or None."""
    try:
        payload_b64, sig = token.rsplit(".", 1)
        expected = hmac.new(SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        if payload["exp"] < time.time():
            return None
        return payload
    except Exception:
        return None