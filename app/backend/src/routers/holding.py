from fastapi import FastAPI, WebSocket, APIRouter, status, WebSocketDisconnect, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from ..orderbook import order_book 
from .. trader import BullTrader, BearTrader, MarketMaker, NoiseTrader
from pydantic import BaseModel
from ..trader_manager import traderManager
from .. import schemas, models
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from ..pubsub import subscribe
from ..redis import enqueue_order, cache_order
from ..schemas import HoldingBase
import time
import datetime

router = APIRouter(
    prefix="/holding",
    tags=['holding']
)

@router.get("/{trader_id}", status_code=status.HTTP_201_CREATED)
async def get_holding(trader_id: int, db: Session = Depends(get_db)):
    try:
        result = await db.execute(select(models.Holding).filter(models.Holding.trader_id == trader_id))
        holdings = result.scalars().all()

        if not holdings:
            return []

        return [
            schemas.HoldingBase(
                trader_id=holding.trader_id,
                asset=holding.asset,
                amount=holding.amount,
                avg_price=holding.avg_price,
                updated_at=holding.updated_at
            )
            for holding in holdings
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching holdings: {e}")





