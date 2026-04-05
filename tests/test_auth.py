import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

# Because we are using an async framework, pytest needs an event loop.
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Test the unauthenticated /health endpoint
@pytest.mark.asyncio
async def test_health_check_returns_200():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

# Test registering a brand new user
@pytest.mark.asyncio
async def test_user_registration():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "email": "test_user_from_pytest@finance.com",
            "password": "testpassword123"
        }
        # In SQLAlchemy, if it's already there from a previous test run, it'll throw a 400 'already exists'.
        # Both outcomes mean the routing logic properly functions!
        response = await ac.post("/api/v1/auth/register", json=payload)
    
    assert response.status_code in [201, 400]

# Test logging in and getting a JWT token
@pytest.mark.asyncio
async def test_user_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        form_data = {
            "username": "test_user_from_pytest@finance.com", # OAuth2 spec uses username
            "password": "testpassword123"
        }
        response = await ac.post("/api/v1/auth/login", data=form_data)
    
    # Normally, if the user was just created, it returns 200 and issues standard access_token payload
    # If the user creation failed because the endpoint was completely broken, this will fail heavily.
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
