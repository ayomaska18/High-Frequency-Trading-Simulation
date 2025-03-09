from fastapi import FastAPI, WebSocket, APIRouter, status
import json
import asyncio
from ..orderbook import order_book 

router = APIRouter(
    prefix="/orderbook",
    tags=['orderbook']
)

clients = set()

@router.get("/", status_code=status.HTTP_201_CREATED)
async def get_order_book():
    """Fetch the latest order book snapshot."""
    order_book_snapshot = order_book.fetch_order_book()
    return order_book_snapshot

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint to send real-time order book updates."""
    await websocket.accept()
    clients.add(websocket)
    try:
        while True:
            data = await order_book.fetch_order_book()
            await websocket.send_text(json.dumps(data))
    except Exception as e:
        print(f"WebSocket Error: {e}")
        await websocket.close(code=1008, reason="Server error")
        clients.remove(websocket)
