from fastapi import APIRouter
from app.api.endpoints import auth, users, records, dashboard

# This acts as the centralized manager for our sub-routers
api_router = APIRouter()

# Authentication endpoints like /api/v1/auth/login
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Secure user endpoints like /api/v1/users/me
api_router.include_router(users.router, prefix="/users", tags=["User Profile"])

# Financial records management endpoints like /api/v1/records
api_router.include_router(records.router, prefix="/records", tags=["Financial Records"])

# Dashboard aggregation endpoints like /api/v1/dashboard/summary
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard Summary"])
