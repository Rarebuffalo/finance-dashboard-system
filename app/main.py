from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

from contextlib import asynccontextmanager
from app.core.database import engine, SessionLocal
from app.models.base import Base
# Import all models here so `Base.metadata.create_all()` discovers them
from app.models.user import User
from app.models.record import FinancialRecord

from app.core.init_db import initialize_seeding

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs precisely once when the server starts up.
    # It dynamically generates our SQLite schema based on our Python classes.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # Auto-seed the database if it's empty
    async with SessionLocal() as db:
        await initialize_seeding(db)
        
    yield
    # We could put shutdown logic here.

def create_app() -> FastAPI:
    """
    The application factory. This pattern is great for testing because it allows
    you to create multiple instances of the app (e.g., test vs dev).
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        description="Backend API for managing financial records and role-based access control.",
        lifespan=lifespan,
        # Used for rendering the auto-docs cleanly
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Cross-Origin Resource Sharing (CORS) Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], 
        allow_credentials=True,
        allow_methods=["*"], 
        allow_headers=["*"], 
    )

    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    from slowapi.middleware import SlowAPIMiddleware

    # Rate Limiting instantiation
    limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    @app.get("/health", tags=["Health"])
    @limiter.exempt
    async def health_check():
        """
        API Health Endpoint.
        Often pinged by load balancers or uptime monitoring tools to ensure 
        the server is responsive.
        """
        return {"status": "healthy", "version": settings.VERSION}

    from app.api.router import api_router
    # Here we mount all of our sub-routers onto the main application, using the /api/v1 prefix
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app

# Initialize the application instance
app = create_app()
