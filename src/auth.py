import hashlib
import hmac
import os
import secrets
import time
from typing import Optional, Tuple

SECRET_KEY = os.environ.get("SESSION_SECRET", "med-diary-secret-key-change-in-production-2026")

def hash_password(password: str) -> str:
    """Generate a secure PBKDF2-HMAC-SHA256 password hash with salt."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    )
    return f"{salt}${key.hex()}"

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored salt$hash."""
    try:
        salt, key_hex = stored_hash.split("$", 1)
        expected_key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000
        )
        return hmac.compare_digest(expected_key.hex(), key_hex)
    except Exception:
        return False

def create_session_token(user_id: int) -> str:
    """Create a signed session token: user_id:timestamp:signature"""
    ts = str(int(time.time()))
    payload = f"{user_id}:{ts}"
    signature = hmac.new(
        SECRET_KEY.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return f"{payload}:{signature}"

def verify_session_token(token: Optional[str], max_age_seconds: int = 30 * 86400) -> Optional[int]:
    """Verify session token and return user_id if valid, else None."""
    if not token or ":" not in token:
        return None
    try:
        parts = token.split(":")
        if len(parts) != 3:
            return None
        user_id_str, ts_str, signature = parts
        payload = f"{user_id_str}:{ts_str}"
        expected_sig = hmac.new(
            SECRET_KEY.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(expected_sig, signature):
            return None
        
        # Check token age (default 30 days)
        ts = int(ts_str)
        if time.time() - ts > max_age_seconds:
            return None
            
        return int(user_id_str)
    except Exception:
        return None
