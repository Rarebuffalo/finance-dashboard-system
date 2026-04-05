from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import UserRole

# ==============================================================================
# Base Pydantic Schema
# Pydantic validates incoming JSON body requests. If a client sends a 
# badly formatted email, Pydantic throws a 422 Exception automatically.
# ==============================================================================
class UserBase(BaseModel):
    # EmailStr uses the 'email-validator' package under the hood
    email: EmailStr
    is_active: bool = True
    role: UserRole = UserRole.VIEWER

# Schema used exactly when a new user registers
class UserCreate(UserBase):
    password: str

# Schema for updating a user (all fields optional)
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

# ==============================================================================
# Output Schema
# This defines what the API returns. Notice it DOES NOT include `password` or `hashed_password`.
# ==============================================================================
class UserResponse(UserBase):
    id: int

    class Config:
        # Crucial for SQLAlchemy: Tells Pydantic to read data even if it's not a dict,
        # but rather a class object (like user.id, user.email)
        from_attributes = True
