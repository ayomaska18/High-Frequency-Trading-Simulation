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

    model_config = {
        "from_attributes": True
    }

class OrderBase(BaseModel):
    asset: str
    is_buy: bool
    trader_id: int
    price: float
    volume: float
    order_type: str
    # timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class OrderGet(OrderBase):
    id: int

    model_config = {
        "from_attributes": True
    }


class OrderCreate(OrderBase):
    pass

class OrderResponse(BaseModel):
    id: int
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "from_attributes": True
    }

class HoldingBase(BaseModel):
    trader_id: int
    asset: str
    amount: float = 0.0
    avg_price: float = 0.0
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


