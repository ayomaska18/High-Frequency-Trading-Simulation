from .orderbook import order_book
from .marketdatafeed import MarketDataFeed
from .trader import BullTrader, BearTrader, MarketMaker
import threading
import uvicorn
from fastapi import FastAPI, status
from contextlib import asynccontextmanager
from .routers import orderbook

feed = MarketDataFeed()

traders = [
    BullTrader(trader_id=1, order_book=order_book, max_position=1),
    BullTrader(trader_id=2, order_book=order_book, max_position=1),
    BullTrader(trader_id=3, order_book=order_book, max_position=5),
    BearTrader(trader_id=4, order_book=order_book, max_position=5),
    BearTrader(trader_id=5, order_book=order_book, max_position=5),
    BearTrader(trader_id=6, order_book=order_book, max_position=5),
    MarketMaker(trader_id=7, order_book=order_book, max_position=15),
]

for trader in traders:
    feed.subscribe(trader)

def start_market_data_feed():
    """ Run the market data feed in a separate thread. """
    feed.run()

def start_trader(trader):
    """ Start trader in a separate thread. """
    while True:
        trader.on_market_data(order_book.get_best_bid()) 

def run_background_tasks():
    """Start market data feed and traders in background threads."""
    feed_thread = threading.Thread(target=start_market_data_feed, daemon=True)
    feed_thread.start()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown tasks"""
    run_background_tasks()  
    yield
    print("Shutting down...")  

app = FastAPI(lifespan=lifespan)

app.include_router(orderbook.router)

@app.get("/", status_code=status.HTTP_201_CREATED)
def root():
    print('hello')

