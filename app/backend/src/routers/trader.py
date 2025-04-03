from fastapi import FastAPI, WebSocket, APIRouter, status, WebSocketDisconnect, HTTPException, Depends
from ..orderbook import order_book 
from .. trader import BullTrader, BearTrader, MarketMaker, NoiseTrader, Client
from pydantic import BaseModel
from ..trader_manager import traderManager
from .. import schemas, models
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.future import select

router = APIRouter(
    prefix="/trader",
    tags=['trader']
)

class TraderCreationRequest(BaseModel):
    name: str
    max_position: int = 15

@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_trader(trader:schemas.TraderCreate, db: Session = Depends(get_db)):
    print(f"Added trader to database: {trader}")
    try:
        
        new_trader =  models.Trader(**trader.model_dump())
        
        db.add(new_trader)
        await db.commit()
        await db.refresh(new_trader)

        if new_trader.is_bot:
            new_trader = {
                "trader_id": new_trader.id,
                "name": new_trader.name,
                "trader_type": new_trader.trader_type,
                "max_position": 15,
                "is_bot": new_trader.is_bot
            }
        
            await traderManager.add_trader(new_trader, db)

        return schemas.TraderResponse(
            name = new_trader.name,
            id=new_trader.id,
            trader_type=new_trader.trader_type,
            balance=new_trader.balance,
            is_bot=new_trader.is_bot,
            orders=[]
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding trader: {e}")

@router.delete("/{trader_type}", status_code=status.HTTP_200_OK)
async def remove_trader(trader_type: str, db: Session = Depends(get_db)):
    """
    Example endpoint to remove the most recently added trader (or adapt logic).
    """
    try:
        trader_id = await traderManager.remove_trader(trader_type)

        print(trader_id)

        if not trader_id:
            raise HTTPException(status_code=404, detail="Trader not found in TraderManager.")
        
        result = await db.execute(select(models.Trader).filter(models.Trader.id == trader_id))
        db_trader = result.scalars().first()

        if db_trader:
            await db.delete(db_trader)
            await db.commit()
            print(f"Removed trader from database: {trader_id}")
        else:
            print(f"Trader with ID {trader_id} not found in database.")

        return {"message": f"Removed Trader with trader type {trader_type}."}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error removing trader: {e}")

@router.get("/", status_code=status.HTTP_200_OK)
async def list_traders(db: Session = Depends(get_db)):
    """
    Return all currently registered traders.
    """
    try:
        result = await db.execute(select(models.Trader))
        db_traders = result.scalars().all()
        return [
            schemas.TraderResponse(
                id=trader.id,
                name=trader.name,
                trader_type=trader.trader_type,
                balance=trader.balance,
                is_bot=trader.is_bot,
                orders=[]
            )
            for trader in db_traders
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing traders: {e}")
    
@router.get("/{trader_id}", response_model=schemas.TraderResponse, status_code=status.HTTP_200_OK)
async def get_trader(trader_id: int, db: Session = Depends(get_db)):
    """
    Fetch trader details by trader ID.
    """
    try:
        result = await db.execute(select(models.Trader).filter(models.Trader.id == trader_id))
        db_trader = result.scalars().first()

        if not db_trader:
            raise HTTPException(status_code=404, detail="Trader not found")

        return schemas.TraderResponse(
            id=db_trader.id,
            name=db_trader.name,
            trader_type=db_trader.trader_type,
            balance=db_trader.balance,
            is_bot=db_trader.is_bot,
            orders=[]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trader: {e}")