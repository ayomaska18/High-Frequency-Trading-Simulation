import asyncio
from collections import defaultdict

_subscribers = defaultdict(asyncio.Queue)

def subscribe(trader_id: int) -> asyncio.Queue:
    return _subscribers[trader_id]

def publish(message: dict):
    for queue in _subscribers.values():
        queue.put_nowait(message)