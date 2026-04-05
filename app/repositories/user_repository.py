from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from typing import Optional

class UserRepository:
    """
    The Repository Pattern abstracts away the direct database queries.
    Instead of scattering `session.execute(select(...))` all around our services,
    we put them here. This makes it incredibly easy to swap out databases or test
    business logic without needing a running DB.
    """
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_by_email(self, email: str) -> Optional[User]:
        # Using SQLAlchemy 2.0 style select statement
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        # return the first instance found, or None
        return result.scalars().first()

    async def get_by_id(self, user_id: int) -> Optional[User]:
        # `get()` is a highly optimized primary key lookup function in SQLAlchemy
        return await self.session.get(User, user_id)

    async def create(self, user: User) -> User:
        self.session.add(user)
        # We explicitly commit the transaction here.
        await self.session.commit()
        # Refresh grabs the freshly generated DB ID and attaches it to the model.
        await self.session.refresh(user)
        return user
