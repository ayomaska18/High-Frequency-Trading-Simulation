from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from datetime import datetime, timezone

Base = declarative_base()

class Trader(Base):
    __tablename__ = "traders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    trader_type = Column(String)
    balance = Column(Float, default=1000.0)
    is_bot = Column(Boolean, default=True)

    orders = relationship("Order", back_populates="trader")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    trader_id = Column(Integer, ForeignKey("traders.id"))
    asset = Column(String, index=True)
    is_buy = Column(Boolean, nullable=False)
    price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    order_type = Column(String, nullable=False)
    trader = relationship("Trader", back_populates="orders")
