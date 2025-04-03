import asyncio
from typing import List, Optional, Dict, Type
from .trader import Trader  # BullTrader, BearTrader, MarketMaker, etc.
from . import models
from sqlalchemy.orm import Session
from .trader import *
from .orderbook import order_book



class TraderManager:
    def __init__(self):
        self.traders: Dict[Type[Trader], List[Trader]] = {
            BullTrader: [],
            BearTrader: [],
            MarketMaker: [],
            NoiseTrader: [],
        }
        self.tasks: List[asyncio.Task] = []
        self.running: bool = False
        self.trader_id_map: Dict[int, Trader] = {}

    async def add_trader(self, trader: dict) -> None:
        print(trader)
        try:
            if "bull" in trader["trader_type"].lower():
                new_trader = BullTrader(
                    name=trader['name'],
                    trader_id=trader['trader_id'],
                    order_book=order_book,
                    max_position=15,
                    is_bot=trader['is_bot']
                )
            elif "bear" in trader["trader_type"].lower():
                new_trader = BearTrader(
                    name=trader['name'],
                    trader_id=trader['trader_id'],
                    order_book=order_book,
                    max_position=15,
                    is_bot=trader['is_bot']
                )
            elif "noise" in trader["trader_type"].lower():
                new_trader = NoiseTrader(
                    name=trader['name'],
                    trader_id=trader['trader_id'],
                    order_book=order_book,
                    max_position=15,
                    is_bot = trader['is_bot']
                )
            elif "mm" in trader["trader_type"].lower():
                new_trader = MarketMaker(
                    name=trader['name'],
                    trader_id=trader['trader_id'],
                    order_book=order_book,
                    max_position=15,
                    is_bot = trader['is_bot']
                )
            
            trader_type = type(new_trader)
            self.traders[trader_type].append(new_trader)
            self.trader_id_map[trader['trader_id']] = new_trader

            if self.running:
                task = asyncio.create_task(self._trader_task(new_trader))
                task.set_name(f"trader-{trader['trader_id']}")
                self.tasks.append(task)
        except Exception as e:
            print(f"Error adding trader in trader manager: {e}")

    async def add_initial_traders(self, trader: Trader, db: Session) -> None:
        db_trader = models.Trader(
            name=trader['name'],
            trader_type=trader['trader_type'],
            balance=1000.0,
            is_bot=trader['is_bot'],
        )
        db.add(db_trader)
        await db.commit()
        await db.refresh(db_trader)

        if "bull" in trader["trader_type"].lower():
            new_trader = BullTrader(
                name=trader['name'],
                trader_id=db_trader.id,
                order_book=order_book,
                max_position=15,
                is_bot=trader['is_bot']
            )
        elif "bear" in trader["trader_type"].lower():
            new_trader = BearTrader(
                name=trader['name'],
                trader_id=db_trader.id,
                order_book=order_book,
                max_position=15,
                is_bot=trader['is_bot']
            )
        elif "noise" in trader["trader_type"].lower():
            new_trader = NoiseTrader(
                name=trader['name'],
                trader_id=db_trader.id,
                order_book=order_book,
                max_position=15,
                is_bot = trader['is_bot']
            )
        else:
            new_trader = MarketMaker(
                name=trader['name'],
                trader_id=db_trader.id,
                order_book=order_book,
                max_position=15,
                is_bot = trader['is_bot']
            )
        
        trader_type = type(new_trader)
        self.traders[trader_type].append(new_trader)
        self.trader_id_map[db_trader.id] = new_trader

        if self.running:
            task = asyncio.create_task(self._trader_task(trader))
            task.set_name(f"trader-{trader.trader_id}")
            self.tasks.append(task)

    async def remove_trader(self, trader_type):
        trader_type_map = {
            "bull": BullTrader,
            "bear": BearTrader,
            "noise": NoiseTrader,
            "mm": MarketMaker
        }

        if trader_type.lower() not in trader_type_map:
            print(f"Invalid trader type: {trader_type}")
            return None
        
        trader_class = trader_type_map[trader_type.lower()]

        if trader_class not in self.traders or not self.traders[trader_class]:
            print(f"No traders of type {trader_type} found in TraderManager.")
            return None
        
        trader = self.traders[trader_class].pop()
        self.trader_id_map.pop(trader.trader_id, None)
        print(f"Removed trader from TraderManager: {trader.trader_id}")

        task = next((t for t in self.tasks if t.get_name() == f"trader-{trader.trader_id}"), None)
        if task:
            task.cancel()
            self.tasks.remove(task)
            print(f"Cancelled task for trader: {trader.trader_id}")

        return trader.trader_id

    async def start(self) -> None:
        self.running = True
        for trader_list in self.traders.values():
            for trader in trader_list:
                task = asyncio.create_task(self._trader_task(trader))
                task.set_name(f"trader-{trader.trader_id}")
                self.tasks.append(task)

    async def stop(self) -> None:
        self.running = False
        for task in self.tasks:
            task.cancel()
        self.tasks.clear()

    async def _trader_task(self, trader: Trader):
        while True:
            try:
                trader.trade()
                await asyncio.sleep(0.25)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in trader task (ID: {trader.trader_id}): {e}")

    def list_traders(self) -> List[Trader]:
        return self.traders
    
    def get_trader_by_id(self, id: int) -> Optional[Trader]:
        return self.trader_id_map.get(id, None)

traderManager = TraderManager()
