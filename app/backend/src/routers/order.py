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
import time
import datetime

router = APIRouter(
    prefix="/order",
    tags=['order']
)

@router.websocket("/ws/{trader_id}")
async def websocket_endpoint(websocket: WebSocket, trader_id: int, db: Session = Depends(get_db)):
    await websocket.accept()
    queue = subscribe(trader_id)

    try:
        while True:
            message = await queue.get()
            await websocket.send_json(jsonable_encoder(message))
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
            schemas.OrderGet(
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
        timestamp = datetime.datetime.now()

        new_order = models.Order(
            trader_id=order.trader_id,
            asset=order.asset,
            is_buy=order.is_buy,
            price=order.price,
            volume=order.volume,
            order_type=order.order_type,
            timestamp=timestamp,  # Use backend-generated timestamp
        )

        db.add(new_order)
        await db.commit()
        await db.refresh(new_order)

        order_data = {
            "id": new_order.id,
            "trader_id": new_order.trader_id,
            "asset": new_order.asset,
            "is_buy": new_order.is_buy,
            "price": new_order.price,
            "volume": new_order.volume,
            "order_type": new_order.order_type,
            "timestamp": new_order.timestamp.isoformat(),
        }
    
        await cache_order(new_order.id, order_data)
        await enqueue_order(order_data)

        result = await db.execute(
            select(models.Holding).filter(
                models.Holding.trader_id == order.trader_id,
                models.Holding.asset == order.asset
            )
        )
        holding = result.scalars().first()

        if holding:
            total_amount = holding.amount + (order.volume if order.is_buy else -order.volume)
            if total_amount < 0:
                raise HTTPException(status_code=400, detail="Insufficient holdings to sell")

            if order.is_buy:
                total_cost = (holding.amount * holding.avg_price) + (order.volume * order.price)
                avg_price = total_cost / total_amount
                holding.avg_price = avg_price

            holding.amount = total_amount
            holding.updated_at = timestamp
        else:
            if order.is_buy:
                new_holding = models.Holding(
                    trader_id=order.trader_id,
                    asset=order.asset,
                    amount=order.volume,
                    avg_price=order.price,
                    updated_at=timestamp
                    )
                db.add(new_holding)
            else:
                raise HTTPException(status_code=400, detail="Cannot sell an asset that is not held")

        await db.commit()
        

        return {"message": "Order has been received successfully."}
    
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






