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
import time

router = APIRouter(
    prefix="/order",
    tags=['order']
)

@router.websocket("/ws/{trader_id}")
async def websocket_endpoint(websocket: WebSocket, trader_id: int, db: Session = Depends(get_db)):
    await websocket.accept()
    queue = await subscribe(trader_id)

    try:
        while True:
            message = await queue.get()
            order = schemas.OrderBase(**message)

            db_order = models.Order(
                id=order.id,
                trader_id=order.trader_id,
                asset=order.asset,
                is_buy=order.is_buy,
                price=order.price,
                order_type=order.order_type,
                volume=order.volume,
                timestamp=int(time.time())
            )

            db.add(db_order)
            await db.commit()
            await db.refresh(db_order)

            await websocket.send_json(jsonable_encoder(order)) 
    except WebSocketDisconnect:
        print(f"[WebSocket] Trader {trader_id} disconnected")
    except Exception as e:
        print(f"[WebSocket] Error: {e}")

@router.get("/{trader_id}", status_code=status.HTTP_201_CREATED)
async def get_order(trader_id: int, db: Session = Depends(get_db)):
    try:
        result = await db.execute(select(models.Order).filter(models.Order.trader_id == trader_id))
        orders = result.scalars().all()

        if not orders:
            raise HTTPException(status_code=404, detail=f"No orders found for trader ID {trader_id}")

        return [
            schemas.OrderBase(
                id=order.id,
                trader_id=order.trader_id,
                asset=order.asset,
                is_buy=order.is_buy,
                price=order.price,
                order_type=order.order_type,
                volume=order.volume,
                timestamp=order.timestamp,
            )
            for order in orders
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching orders: {e}")

@router.post("/", status_code=status.HTTP_201_CREATED)
async def execute_order(order:schemas.OrderCreate, db: Session = Depends(get_db)):
    try:
        new_order = models.Order(**order.model_dump())

        if new_order.order_type == "market":
            message = order_book.market_order_match(new_order)
        elif new_order.order_type == "limit":
            message = order_book.limit_order_match(new_order)
        elif new_order.order_type == "cancel":
            message = order_book.cancel_order(new_order)
        else:
            raise HTTPException(status_code=400, detail="Invalid order type")
        
        if message == 'Insufficient Liquidity to fill order':
            raise HTTPException(status_code=400, detail="Insufficient Liquidity to fill order")

        return message
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error executing order: {e}")
    
@router.delete("/{order_id}", status_code=status.HTTP_200_OK)
async def delete_order(order_id: int, db: Session = Depends(get_db)):
    """
    Delete an order by its ID.
    """
    try:
        result = await db.execute(select(models.Order).filter(models.Order.id == order_id))
        order = result.scalars().first()

        if not order:
            raise HTTPException(status_code=404, detail=f"Order with ID {order_id} not found")

        await db.delete(order)
        await db.commit()

        order_book.remove_order(order_id)

        return {"message": f"Order with ID {order_id} has been deleted."}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting order: {e}")






