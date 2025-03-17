import asyncio
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, status
from contextlib import asynccontextmanager
from .orderbook import order_book
from .trader import BullTrader, BearTrader, MarketMaker
from .routers import orderbook
from .routers import trader
from .trader_manager import traderManager

async def add_initial_traders():
    initial_traders = [
        BullTrader(trader_id=1, order_book=order_book, max_position=15),
        BearTrader(trader_id=2, order_book=order_book, max_position=15),
        MarketMaker(trader_id=3, order_book=order_book, max_position=15)
    ]
    for t in initial_traders:
        await traderManager.add_trader(t)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await add_initial_traders()
    await traderManager.start() 
    yield
    await traderManager.stop()
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orderbook.router)
app.include_router(trader.router)

traders = []

@app.get("/", status_code=status.HTTP_201_CREATED)
def root():
    return {"message": "Trading Engine Running"}
