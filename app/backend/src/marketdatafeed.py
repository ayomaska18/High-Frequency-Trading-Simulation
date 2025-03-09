import os
import json
import time

import websocket
from dotenv import load_dotenv

load_dotenv()

class MarketDataFeed:
    def __init__(self):
        self.subscribers = []
        self.ws_url = "wss://ws.coinapi.io/v1"

        self.hello_msg = {
            "type": "hello",
            "apikey": os.getenv("COINAPI_API_KEY"),
            "heartbeat": False, 
            "subscribe_data_type": ["ohlcv"],
            "subscribe_filter_symbol_id": ["BINANCE_SPOT_BTC_USDT$"]
        }

    def subscribe(self, trader):
        self.subscribers.append(trader)

    def unsubscribe(self, trader):
        self.subscribers.remove(trader)

    def broadcast(self, mid_price):
        for trader in self.subscribers:
            trader.on_market_data(mid_price)

    def on_open(self, ws):
        print("[MarketDataFeed] WebSocket opened, sending subscription message...")
        ws.send(json.dumps(self.hello_msg))

    def on_message(self, ws, message):
        
        try:
            msg = json.loads(message)

            if isinstance(msg, dict) and "price_close" in msg:
                price_close = msg["price_close"]
                self.broadcast(price_close)
            else:
                print("No 'price_close' found in message:", msg)

        except json.JSONDecodeError as e:
            print("JSON parsing error:", e)
        except Exception as e:
            print("Unexpected error extracting 'price_close':", e)

    def on_error(self, ws, error):
        print("[MarketDataFeed] WebSocket error:", error)

    def on_close(self, ws, close_status_code, close_msg):
        print("[MarketDataFeed] WebSocket closed:", close_status_code, close_msg)

    def run(self):
        ws_app = websocket.WebSocketApp(
            self.ws_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        ws_app.run_forever()