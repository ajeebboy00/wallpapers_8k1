import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple
import bcrypt
from jose import JWTError, jwt

from app.core.config import settings
from app.core.constants import UserRole
from app.core.exceptions import UnauthorizedException

def get_password_hash(password: str) -> str:
    """Hash a plaintext password using salted bcrypt with cost factor 12."""
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a salted bcrypt hash."""
    try:
        plain_bytes = plain_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except Exception:
        return False

def hash_token(raw_token: str) -> str:
    """Computes SHA-256 hash of an opaque token for secure database storage."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

def generate_refresh_token() -> Tuple[str, str]:
    """Generates an opaque cryptographic refresh token and its SHA-256 hash."""
    raw_token = secrets.token_urlsafe(64)
    token_hash = hash_token(raw_token)
    return raw_token, token_hash

def create_access_token(
    user_id: uuid.UUID,
    role: UserRole,
    email: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Generates a cryptographically signed HMAC-SHA256 JWT access token."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode: Dict[str, Any] = {
        "sub": str(user_id),
        "email": email,
        "role": role.value if hasattr(role, "value") else str(role),
        "jti": str(uuid.uuid4()),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "token_type": "access"
    }

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a JWT access token, raising UnauthorizedException if invalid."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("token_type") != "access":
            raise UnauthorizedException("Invalid token type")
        return payload
    except JWTError as exc:
        raise UnauthorizedException(f"Could not validate credentials: {str(exc)}")

def create_password_reset_token(email: str) -> str:
    """Generates a short-lived 15-minute token for password reset."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=15)
    to_encode = {
        "sub": email,
        "exp": int(expire.timestamp()),
        "token_type": "password_reset"
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def verify_password_reset_token(token: str) -> Optional[str]:
    """Validates password reset token and returns email if valid."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("token_type") != "password_reset":
            return None
        return payload.get("sub")
    except JWTError:
        return None
