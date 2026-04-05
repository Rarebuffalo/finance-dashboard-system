from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, UserRole
from app.schemas.token import TokenPayload
from app.services.user_service import UserService

"""
OAuth2PasswordBearer is a special utility in FastAPI.
It tells FastAPI: "Whenever an endpoint requires this variable, look for a 
HTTP Header named 'Authorization' containing 'Bearer <token>'."
It also automatically adds a neat login form to the interactive Swagger UI!
"""
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> User:
    """
    Core Dependency: Decodes the JWT and returns the User object.
    You simply inject `user: User = Depends(get_current_user)` into any 
    API route to instantly protect it!
    """
    try:
        # 1. We decode the payload cryptographically
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # 2. We validate the data inside the payload using Pydantic
        token_data = TokenPayload(**payload)
        if token_data.sub is None:
            raise HTTPException(status_code=403, detail="Could not validate credentials")
    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials. Token may be expired or tampered with.",
        )
    
    # 3. We quickly fetch the user from the database to ensure they haven't been deleted or banned
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id=int(token_data.sub))
    
    if not user:
        raise HTTPException(status_code=404, detail="User no longer exists.")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user.")
    
    return user

class RequireRole:
    """
    A Dependable Class used for Role Based Access Control (RBAC).
    
    Usage Example: 
    @app.post("/secret-data")
    async def secret(user: User = Depends(RequireRole([UserRole.ADMIN, UserRole.ANALYST]))):
        ...
    """
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        # Checks if the user's role (pulled from DB/Token) matches the allowed list.
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You do not have the required permissions. Required: {[r.value for r in self.allowed_roles]}."
            )
        return current_user
