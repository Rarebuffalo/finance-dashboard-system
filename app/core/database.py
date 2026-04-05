from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator

from app.core.config import settings

# 1. Create the engine
# The engine manages the pool of connections to the database.
# `echo=False` prevents SQLAlchemy from logging every single SQL statement, 
# which is good for performance but can be turned to `True` for debugging.
engine = create_async_engine(
    settings.ASYNC_DATABASE_URI,
    echo=False,
    future=True 
)

# 2. Session Factory
# AsyncSessionMaker produces new `AsyncSession` objects. 
# We use autocommit=False / autoflush=False so we have granular control over exactly
# when data is committed to the database (important for transaction integrity).
SessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession
)

# 3. Dependency Injector
# This is an incredibly powerful feature of FastAPI.
# This generator function safely opens and closes database connections on a per-request basis.
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides a transactional scope around a series of operations.
    If an error occurs in the endpoint, the `finally` block ensures 
    the connection is cleanly returned to the pool, preventing memory/connection leaks.
    """
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
