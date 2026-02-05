from passlib.context import CryptContext
import secrets
import hashlib

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def generate_refresh_token() -> str:
    """Generate a random refresh token"""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """Hash a token for storage in database"""
    return hashlib.sha256(token.encode()).hexdigest()
