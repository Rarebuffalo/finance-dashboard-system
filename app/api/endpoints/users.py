from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserResponse, UserUpdate
from app.api.dependencies import get_current_user, RequireRole

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def read_user_me(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Fetch the currently logged in User's profile.
    """
    return current_user


@router.get("/all", response_model=list[UserResponse])
async def read_all_users(
    current_user: User = Depends(RequireRole([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Admin Only endpoint showcasing proper RBAC functionality.
    """
    result = await db.execute(select(User))
    return list(result.scalars().all())


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(RequireRole([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Admin Only endpoint to modify a user's role or status.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data:
        from app.core.security import get_password_hash
        user.hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        
    for field, value in update_data.items():
        setattr(user, field, value)
        
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(RequireRole([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """
    Admin Only endpoint to completely delete a system user. 
    (Note: In a true production app, Soft Delete via is_active is preferred).
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    await db.delete(user)
    await db.commit()
