from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone

class TraderBase(BaseModel):
    name: str
    trader_type: str
    balance: float = 1000.0
    is_bot: bool

class TraderCreate(TraderBase):
    pass

class TraderResponse(TraderBase):
    trader_id: int
    orders: Optional[List["OrderResponse"]] = []

    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    id: int
    asset: str
    is_buy: bool
    trader_id: int
    price: float
    volume: float
    order_type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class OrderCreate(OrderBase):
    pass

class OrderResponse(BaseModel):
    message: str

    class Config:
        orm_mode = True


