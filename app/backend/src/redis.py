import json
import redis.asyncio as redis 
import asyncio
from fastapi import HTTPException
from .orderbook import order_book
from .config import settings

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
        except Exception as e:
            print(f"Error processing order: {e}")
        await asyncio.sleep(0.1)