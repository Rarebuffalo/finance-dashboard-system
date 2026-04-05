from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt
from typing import Any, Union
from app.core.config import settings

# `pwd_context` handles the cryptographic hashing.
# Bcrypt is the industry standard for password hashing.
# It automatically generates and merges salts so two identical passwords still have different hashes.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the hashed string in the database."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashes a password for storing securely in the database."""
    return pwd_context.hash(password)

def create_access_token(
    subject: Union[str, Any], role: str, expires_delta: Optional[timedelta] = None
) -> str:
    """
    Creates a JSON Web Token (JWT).
    The stateless nature of JWTs means the backend doesn't need to store a "session" in memory or the DB.
    The token itself contains the user's ID (`sub`) and `role`, signed cryptographically by our `SECRET_KEY`.
    If anyone tampers with the token on the client side, the cryptographic signature will fail verification.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Payload of the token
    to_encode = {
        "exp": expire,                      # Expiration time
        "sub": str(subject),                # Subject (Usually User ID)
        "role": role                        # Injecting role directly into token for quick RBAC checks
    }
    
    # We sign the dictionary with PyJWT
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
