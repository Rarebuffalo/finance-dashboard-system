from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import Token
from app.services.user_service import UserService

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate, 
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Creates a new user account safely and hashes the password via the UserService.
    """
    user_service = UserService(db)
    return await user_service.register_user(user_in)


@router.post("/login", response_model=Token)
async def login(
    db: AsyncSession = Depends(get_db),
    # OAuth2PasswordRequestForm automatically parses form-data, generating Swagger interactive tests!
    # Because FastAPI standard expects a `username` field, we map our `email` string to it on the client.
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Verifies the email and password against the DB and yields an Access Token containing 
    the logged-in User ID and Role.
    """
    user_service = UserService(db)
    user = await user_service.authenticate(
        email=form_data.username, password=form_data.password
    )
    
    if not user:
        # Standard safety: Don't tell the client if the email exists but password was wrong. Just say 'Incorrect'.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Cryptographically sign the identity payload to generate the Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user.id), role=user.role, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
