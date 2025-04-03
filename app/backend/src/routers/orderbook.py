from fastapi import FastAPI, WebSocket, APIRouter, status, WebSocketDisconnect
import json
import asyncio
import time
from ..orderbook import order_book 
from ..influxdb import write_to_influxdb

router = APIRouter(
    prefix="/orderbook",
    tags=['orderbook']
)

clients = set()

@router.get("/", status_code=status.HTTP_201_CREATED)
async def get_order_book():
    order_book_snapshot = order_book.fetch_order_book()
    return order_book_snapshot

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)

    prices = []
    window_start = time.time()

    try:
        while True:
            try:
                data = order_book.fetch_order_book()
                best_bid = order_book.get_best_bid()
                best_ask = order_book.get_best_ask()

                if best_bid is None or best_ask is None or best_bid == 0 or best_ask == 0:
                    mid_price = 0
                else:
                    mid_price = (best_bid + best_ask) / 2

                mid_price = round(mid_price, 8) if mid_price else 0
                prices.append(mid_price)
                current_time = time.time()  

                if current_time - window_start >= 5:
                    open_price = prices[0] if prices else 0
                    high_price = max(prices) if prices else 0
                    low_price = min(prices) if prices else 0
                    close_price = prices[-1] if prices else 0

                    ohlc = {
                        "open": open_price,
                        "high": high_price,
                        "low": low_price,
                        "close": close_price
                    }

                    response = {
                        "bids": data["bids"],
                        "asks": data["asks"],
                        "mid_price": mid_price,
                        "OHLC": ohlc,
                        "time": int(current_time)
                    }

                    try:
                        await write_to_influxdb(int(current_time), ohlc, "BTC")
                    except Exception as e:
                        print(f"Error writing to InfluxDB: {e}")

                    await websocket.send_text(json.dumps(response))

                    window_start = current_time
                    prices = []
                else:
                    response = {
                        "bids": data["bids"],
                        "asks": data["asks"],
                        "mid_price": mid_price,
                        "OHLC": None,
                        "time": int(current_time)
                    }

                    await websocket.send_text(json.dumps(response))

            except WebSocketDisconnect:
                print("Client disconnected")
                break
            except Exception as e:
                print(f"Error inside WebSocket loop: {e}")

            await asyncio.sleep(0.25) 

    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        print("WebSocket Disconnected")
        clients.discard(websocket)
