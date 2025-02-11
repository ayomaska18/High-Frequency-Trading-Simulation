import time
import random
from src.order import Order

class Trader:
    def __init__(self, trader_id, order_book, strategy="random"):
        self.trader_id = trader_id
        self.order_book = order_book
        self.strategy = strategy 

    def place_limit_order(self, is_buy, price, volume):
        """ Places a limit order at the given price level. """
        order = Order(
            id=int(time.time() * 1000),
            is_buy=is_buy,
            price=price,
            vol=volume,
            timestamp=time.time(),
        )
        self.order_book.limit_order_match(order)
        print(f"Trader {self.trader_id}: LIMIT {'BUY' if is_buy else 'SELL'} {volume} @ {price}")

    def place_market_order(self, is_buy, volume):
        """ Places a market order, taking the best available price. """
        best_price = self.order_book.get_best_ask() if is_buy else self.order_book.get_best_bid()
        if best_price is None:
            print(f"Trader {self.trader_id}: No liquidity for market order!")
            return

        order = Order(
            id=int(time.time() * 1000),
            is_buy=is_buy,
            price=best_price,
            vol=volume,
            timestamp=time.time(),
        )
        self.order_book.market_order_match(order)
        print(f"Trader {self.trader_id}: MARKET {'BUY' if is_buy else 'SELL'} {volume} @ {best_price}")

    def trade(self):
        """ Trader logic: Executes different strategies based on mode. """
        while True:
            time.sleep(random.uniform(0.5, 2))  # Random delay between orders

            if self.strategy == "random":
                # 80% limit orders, 20% market orders
                if random.random() < 0.8:
                    price = round(random.uniform(99.0, 101.0), 2)
                    volume = random.randint(1, 15)
                    self.place_limit_order(is_buy=random.choice([True, False]), price=price, volume=volume)
                else:
                    volume = random.randint(1, 10)
                    self.place_market_order(is_buy=random.choice([True, False]), volume=volume)

            elif self.strategy == "market_maker":
                # Market makers place limit orders at tight spreads
                spread = 0.01  # Small spread
                best_bid = self.order_book.get_best_bid() or 99.0
                best_ask = self.order_book.get_best_ask() or 101.0

                self.place_limit_order(is_buy=True, price=best_bid + spread, volume=random.randint(5, 10))
                self.place_limit_order(is_buy=False, price=best_ask - spread, volume=random.randint(5, 10))

            elif self.strategy == "aggressive_taker":
                # Aggressive trader takes liquidity via market orders
                self.place_market_order(is_buy=random.choice([True, False]), volume=random.randint(1, 10))
