import asyncio
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, status
from contextlib import asynccontextmanager
from .orderbook import order_book
from .trader import BullTrader, BearTrader, MarketMaker
from .routers import orderbook
from .routers import trader
from .trader_manager import traderManager
from .routers import order
from .database import engine, init_db, SessionLocal
from .redis import init_redis
from .routers import holding
import logging

logger = logging.getLogger("TraderManager")

async def add_initial_traders():
    initial_traders = [
        {"trader_id": 1, "name": "BullTrader1", "trader_type": "bull", "max_position": 15, "is_bot": True},
        {"trader_id": 2, "name": "BearTrader1", "trader_type": "bear", "max_position": 15, "is_bot": True},
        {"trader_id": 3, "name": "MarketMaker1", "trader_type": "mm", "max_position": 15, "is_bot": True},
        {"trader_id": 4, "name": "NoiseTrader1", "trader_type": "noise", "max_position": 15, "is_bot": True},
    ]

    async with SessionLocal() as session:
        for t in initial_traders:
            await traderManager.add_initial_traders(t, session)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await init_redis()
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
app.include_router(order.router)
app.include_router(holding.router)

traders = []

print('application started')

@app.get("/", status_code=status.HTTP_201_CREATED)
def root():
    return {"message": "Trading Engine Running"}
