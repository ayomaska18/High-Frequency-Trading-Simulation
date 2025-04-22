import pytest
from httpx import AsyncClient
from httpx import ASGITransport
from app.backend.src.main import app

@pytest.mark.asyncio
async def test_create_order():
    transport = ASGITransport(app=app)
    payload = {
        
        "asset": "BTC",
        "is_buy": True,
        "trader_id": 1,
        "price": 80000,
        "volume": 0.01,
        "order_type": "market"
    }
    
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/order/", json=payload)
    assert res.status_code == 201
    assert "message" in res.json()

    print("Response JSON:", res.json())
    print("Response Text:", res.text)
