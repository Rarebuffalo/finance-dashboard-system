from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import Optional
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.models.user import User
from app.core.security import get_password_hash, verify_password

class UserService:
    """
    The Service Layer houses the core business logic.
    For example: "If I am registering a user, check if their email already exists first."
    This sits securely between the HTTP API Endpoints and the Database Repositories.
    """
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)

    async def register_user(self, user_in: UserCreate) -> User:
        # Business logic: Email must be unique
        user = await self.repo.get_by_email(email=user_in.email)
        if user:
            # We raise a 400 Bad Request if the rule is violated
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists."
            )
        
        # We NEVER store plaintext. We hash the password before sending to DB.
        db_user = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            role=user_in.role
        )
        return await self.repo.create(db_user)
        
    async def get_user_by_id(self, user_id: int) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        user = await self.repo.get_by_email(email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
