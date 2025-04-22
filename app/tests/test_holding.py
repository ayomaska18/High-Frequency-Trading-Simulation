import pytest
from httpx import AsyncClient
from httpx import ASGITransport
from app.backend.src.main import app

@pytest.mark.asyncio
async def test_get_holdings():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/holding/1")
    assert res.status_code == 201
    assert isinstance(res.json(), list)

    
    print("Response JSON:", res.json())
    print("Response Text:", res.text)
