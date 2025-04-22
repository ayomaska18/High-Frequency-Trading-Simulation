import pytest
from httpx import AsyncClient
from httpx import ASGITransport
from app.backend.src.main import app

import pytest
from httpx import AsyncClient, ASGITransport
from app.backend.src.main import app

@pytest.mark.asyncio
async def test_trader_order_holding_flow():
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        
        # 1. Create a trader
        trader_payload = {
            "name": "FlowTester",
            "trader_type": "client",
            "balance": 1000.0,
            "is_bot": False
        }
        trader_res = await client.post("/trader/", json=trader_payload)
        assert trader_res.status_code == 201
        trader_data = trader_res.json()
        trader_id = trader_data.get("trader_id") or trader_data.get("id")
        assert trader_id is not None

        print("Response JSON:", trader_res.json())
        print("Response Text:", trader_res.text)

        print("Response JSON:", trader_id.json())
        print("Response Text:", trader_id.text)

        # 2. Submit a buy order
        order_payload = {
            "trader_id": trader_id,
            "asset": "BTC",
            "is_buy": True,
            "price": 80000,
            "volume": 0.01,
            "order_type": "limit"
        }
        order_res = await client.post("/order/", json=order_payload)
        assert order_res.status_code == 201
        assert "message" in order_res.json()

        print("Response JSON:", order_res.json())
        print("Response Text:", order_res.text)

        # 3. Retrieve holdings
        holding_res = await client.get(f"/holding/{trader_id}")
        assert holding_res.status_code == 201
        holdings = holding_res.json()

        assert isinstance(holdings, list)
        assert any(h["asset"] == "BTC" for h in holdings)

        print("Response JSON:", holding_res.json())
        print("Response Text:", holding_res.text)

