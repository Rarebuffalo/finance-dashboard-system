from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any

class Settings(BaseSettings):
    """
    Centralized configuration management using pydantic-settings.
    This reads from the `.env` file automatically, validates types,
    and provides autocompletion/type-hints across the app.
    """
    PROJECT_NAME: str
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database (made optional to allow SQLite overriding)
    POSTGRES_SERVER: str | None = None
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str | None = None
    POSTGRES_PORT: int | None = None
    USE_SQLITE: bool = True

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @property
    def ASYNC_DATABASE_URI(self) -> str:
        """
        Dynamically constructs the database connection string.
        Defaults to SQLite if USE_SQLITE is true, otherwise uses Postgres.
        """
        if self.USE_SQLITE:
            return "sqlite+aiosqlite:///./finance.db"
        
        user = self.POSTGRES_USER
        password = self.POSTGRES_PASSWORD
        server = self.POSTGRES_SERVER
        port = self.POSTGRES_PORT
        db = self.POSTGRES_DB
        return f"postgresql+asyncpg://{user}:{password}@{server}:{port}/{db}"

    # Load from the local .env implicitly if present
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

# Instantiate as a singleton to be imported by the rest of the application
settings = Settings()
