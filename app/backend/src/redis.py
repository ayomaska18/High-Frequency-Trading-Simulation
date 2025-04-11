import json
import redis.asyncio as redis 
import asyncio
from datetime import datetime, timezone
from fastapi import HTTPException
from .orderbook import order_book
from .config import settings
from .database import get_db
from sqlalchemy.future import select
from .models import Holding
from .pubsub import publish

ORDER_QUEUE_KEY = "order_queue"
redis_pool = None

async def init_redis():
    global redis_client
    redis_client = redis.from_url(
        settings.redis_host_url, decode_responses=True
    )

async def enqueue_order(order_data: dict):
    order_json = json.dumps(order_data)
    await redis_client.rpush(ORDER_QUEUE_KEY, order_json)

async def dequeue_order(timeout: int = 0) -> dict:
    result = await redis_client.blpop(ORDER_QUEUE_KEY, timeout=timeout)
    if result:
        return json.loads(result[1])
    return None

async def cache_order(order_id: int, order_data: dict, ttl: int = 3600):
    key = f"order:{order_id}"
    order_json = json.dumps(order_data)
    await redis_client.set(key, order_json, ex=ttl)

async def get_cached_order(order_id: int) -> dict:
    key = f"order:{order_id}"
    data = await redis_client.get(key)
    if data:
        return json.loads(data)
    return None

async def process_orders():
    while True:
        try:
            order_data = await dequeue_order()

            holding_data = {
                "trader_id": order_data.trader_id,
                "asset": order_data.asset,
                "price": order_data.price,
                "amount": order_data.volume,
            }
            
            if order_data:
                if order_data['order_type'] == "market":
                    message = order_book.market_order_match(order_data)
                elif order_data['order_type'] == "limit":
                    message = order_book.limit_order_match(order_data)
                elif order_data['order_type'] == "cancel":
                    message = order_book.cancel_order(order_data)
                else:
                    raise HTTPException(status_code=400, detail="Invalid order type")

                if message == 'Insufficient Liquidity to fill order':
                    raise HTTPException(status_code=400, detail="Insufficient Liquidity to fill order")
                
                print("Processed order:", message)

                # publish(order_data)

                async with get_db() as db:
                    await update_holdings(holding_data, db)
        except Exception as e:
            print(f"Error processing order: {e}")
        await asyncio.sleep(0.1)

async def update_holdings(order_data: dict, db):
    try:
        result = await db.execute(
            select(Holding).filter(
                Holding.trader_id == order_data["trader_id"],
                Holding.asset == order_data["asset"]
            )
        )
        holding = result.scalars().first()

        if holding:
            total_amount = holding.amount + (order_data["volume"] if order_data["is_buy"] else -order_data["volume"])
            if total_amount < 0:
                raise HTTPException(status_code=400, detail="Insufficient holdings to sell")

            if order_data["is_buy"]:
                total_cost = (holding.amount * holding.avg_price) + (order_data["volume"] * order_data["price"])
                avg_price = total_cost / total_amount
                holding.avg_price = avg_price

            holding.amount = total_amount
            holding.updated_at = datetime.now(timezone.utc)
        else:
            if order_data["is_buy"]:
                new_holding = Holding(
                    trader_id=order_data["trader_id"],
                    asset=order_data["asset"],
                    amount=order_data["volume"],
                    avg_price=order_data["price"],
                    updated_at=datetime.now(timezone.utc)
                )
                db.add(new_holding)
            else:
                raise HTTPException(status_code=400, detail="Cannot sell an asset that is not held")

        await db.commit()
    except Exception as e:
        await db.rollback()
        print(f"Error updating holdings: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating holdings: {e}")