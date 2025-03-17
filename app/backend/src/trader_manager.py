import asyncio
from typing import List, Optional
from .trader import Trader  # BullTrader, BearTrader, MarketMaker, etc.

class TraderManager:
    def __init__(self):
        self.traders: List[Trader] = []
        self.tasks: List[asyncio.Task] = []
        self.running: bool = False

    async def add_trader(self, trader: Trader) -> None:
        self.traders.append(trader)
        task = asyncio.create_task(self._trader_task(trader))
        self.tasks.append(task)

    async def remove_trader(self):
        if not self.traders:
            return None
        trader = self.traders.pop()
        task = self.tasks.pop()
        task.cancel()
        return trader

    async def start(self) -> None:
        self.running = True
        self.tasks = [asyncio.create_task(self._trader_task(t)) for t in self.traders]

    async def stop(self) -> None:
        self.running = False
        for task in self.tasks:
            task.cancel()
        self.tasks.clear()

    async def _trader_task(self, trader: Trader):
        while True:
            trader.trade() 
            await asyncio.sleep(0.25)

    def list_traders(self) -> List[Trader]:
        return self.traders

traderManager = TraderManager()
