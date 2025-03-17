from fastapi import FastAPI, WebSocket, APIRouter, status, WebSocketDisconnect, HTTPException
from ..orderbook import order_book 
from .. trader import BullTrader, BearTrader, MarketMaker, NoiseTrader
from pydantic import BaseModel
from ..trader_manager import traderManager

router = APIRouter(
    prefix="/trader",
    tags=['trader']
)

class TraderCreationRequest(BaseModel):
    name: str
    max_position: int = 15

@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_trader(request: TraderCreationRequest):

    if "bull" in request.name.lower():
        new_trader = BullTrader(
            trader_id=len(traderManager.traders) + 1,
            order_book=order_book,
            max_position=request.max_position
        )
    elif "bear" in request.name.lower():
        new_trader = BearTrader(
            trader_id=len(traderManager.traders) + 1,
            order_book=order_book,
            max_position=request.max_position
        )
    elif "noise" in request.name.lower():
        new_trader = NoiseTrader(
            trader_id=len(traderManager.traders) + 1,
            order_book=order_book,
            max_position=request.max_position
        )
    else:
        new_trader = MarketMaker(
            trader_id=len(traderManager.traders) + 1,
            order_book=order_book,
            max_position=request.max_position
        )

    await traderManager.add_trader(new_trader)
    return {
        "message": f"Trader {request.name} added successfully!",
        "trader_id": new_trader.trader_id
    }

@router.delete("/", status_code=status.HTTP_200_OK)
async def remove_trader():
    """
    Example endpoint to remove the most recently added trader (or adapt logic).
    """
    removed = await traderManager.remove_trader()
    if removed is None:
        raise HTTPException(status_code=404, detail="No available trader to remove.")
    return {
        "message": f"Removed Trader with ID {removed.trader_id}."
    }

@router.get("/", status_code=status.HTTP_200_OK)
def list_traders():
    """
    Return all currently registered traders.
    """
    return [
        {
            "trader_id": t.trader_id,
            "type": t.__class__.__name__,
            "max_position": t.max_position
        }
        for t in traderManager.list_traders()
    ]