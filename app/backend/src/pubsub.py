import asyncio
from collections import defaultdict

_subscribers = defaultdict(asyncio.Queue)

def subscribe(trader_id: int) -> asyncio.Queue:
    return _subscribers[trader_id]

def publish(trader_id: int, message: dict):
    queue = _subscribers[trader_id]
    queue.put_nowait(message)
