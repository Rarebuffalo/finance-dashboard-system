from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    """
    Standard OAuth2 response schema for returning an access token.
    FastAPI's built-in OAuth2 logic expects this exact format.
    """
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    """
    Schema representing the internal structure of our decoded JWT payload.
    When a user sends up a token, we decode it into this object to quickly
    evaluate their identity and role without necessarily hitting the database.
    """
    sub: Optional[str] = None
    role: Optional[str] = None
