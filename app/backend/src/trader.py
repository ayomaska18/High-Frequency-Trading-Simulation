import time
import random
from .order import Order
from collections import defaultdict
from .setting import MAKER_FEE, TAKER_FEE

class Trader:
    def __init__(self, trader_id, name, order_book, is_bot, balance=1000,
                 max_position=15, max_vol = 1):

        self.trader_id = trader_id
        self.name = name
        self.order_book = order_book
        self.balance = balance
        self.positions = defaultdict(int)
        self.open_orders = []
        self.max_position = max_position
        self.max_vol = max_vol
        self.is_bot = is_bot

    # def on_fill(self, order, remaining_vol, filled_vol):
    #     order_id = fill_info['order_id']
    #     filled_qty = fill_info['filled_qty']
    #     fill_price = fill_info['filled_price']
    #     asset = fill_info['asset']
    #     is_buy = fill_info['is_buy']

    #     # Update position
    #     if asset not in self.positions:
    #         self.positions[asset] = 0

    #     if is_buy:
    #         self.positions[asset] += filled_qty
    #     else:
    #         self.positions[asset] -= filled_qty

    #     # Reduce the open order quantity
    #     if order_id in self.open_orders:
    #         self.open_orders[order_id]['remaining_vol'] -= filled_qty
    #         # If the order is fully filled, remove it
    #         if self.open_orders[order_id]['remaining_vol'] <= 0:
    #             del self.open_orders[order_id]

    #     # Debug/log
    #     print(f"[Trader {self.trader_id}] FILLED {filled_qty} {asset} @ {fill_price}. "
    #           f"New {asset} position: {self.positions[asset]}")

    def place_limit_order(self, asset, is_buy, price, volume):
        """Places a limit order. Naively assumes full fill for demonstration."""
        if volume <= 0:
            return

        # If we are hitting position limits, skip placing the order
        # if is_buy and self.positions[asset] >= self.max_vol:
        #     print(f"[Trader {self.trader_id}] Reached max long position, cannot buy more.")
        #     return
        # if not is_buy and self.positions[asset] <= -self.max_vol:
        #     print(f"[Trader {self.trader_id}] Reached max short position, cannot sell more.")
        #     return
        
        id = int(time.time() * 1000)

        order = Order(
            id=id,
            trader_id=self.trader_id,
            asset=asset,
            is_buy=is_buy,
            price=price,
            vol=volume,
            order_type='LIMIT',
            timestamp=time.time(),
        )

        message = self.order_book.limit_order_match(order)

        print('status', message['status'])

        # if remaining_vol: # Partial fill
        #     order.vol = remaining_vol
        #     self.open_orders.append(order.id)
        #     filled_vol = volume - remaining_vol
        # else: # Fully filled
        #     filled_vol = volume

        # self.positions[asset] += filled_vol if is_buy else -filled_vol
        # self.balance -= filled_vol * price
        
        # # Apply maker fee (rebate)
        # self.balance += filled_vol * price * MAKER_FEE

        # print(f"[Trader {self.trader_id}] LIMIT {'BUY' if is_buy else 'SELL'} {volume} @ {price}, "
        #       f"New Position: {self.positions[asset]}")
    
    def place_cancel_order(self, order_id):
        if order_id not in self.open_orders:
            print(f"[Trader {self.id}] Order {order_id} not found in open orders.")
            return

        self.order_book.cancel_order(order_id)
        self.open_orders.remove(order_id)
        print(f"[Trader {self.id}] CANCEL order {order_id}.")

    def place_market_order(self, asset, is_buy, volume):
        print('buy vol', volume)
        """Places a market order, taking the best available price. Naively assumes full fill."""
        if volume <= 0:
            return

        # Same position-limit check
        # if is_buy and self.positions[asset] >= self.max_position:
        #     print(f"[Trader {self.trader_id}] Reached max long position, cannot buy more (MARKET).")
        #     return
        # if not is_buy and self.positions[asset] <= -self.max_position:
        #     print(f"[Trader {self.trader_id}] Reached max short position, cannot sell more (MARKET).")
        #     return

        # Get best available price from the order book
        best_price = (self.order_book.get_best_ask() if is_buy
                      else self.order_book.get_best_bid())
        
        print('current best price', best_price)

        if best_price is None:
            # No liquidity on the opposite side
            print(f"[Trader {self.id}] No liquidity for {'BUY' if is_buy else 'SELL'} market order!")
            return

        order = Order(
            id=int(time.time() * 1000),
            trader_id=self.trader_id,
            asset=asset,
            is_buy=is_buy,
            price=best_price,
            order_type='MARKET',
            vol=volume,
            timestamp=time.time(),
        )

        message = self.order_book.market_order_match(order)

        # if remaining_vol: # Not fully filled
        #     print("Market Order not fully filled")
        #     return
        # else:
        #     self.positions[asset] += volume if is_buy else -volume
        #     self.balance -= volume * best_price
            
        #     # Apply taker fee (cost)
        #     self.balance -= volume * best_price * TAKER_FEE

        #     print(f"[Trader {self.trader_id}] MARKET {'BUY' if is_buy else 'SELL'} {volume} @ {best_price}, "
        #           f"New Position: {self.positions[asset]}, Balance: {self.balance}")

        print('status', message['status'])

    def trade(self):
        pass

    def cancel_excess_orders(self):
        """If we have more than 15 open orders, cancel some (e.g. oldest or random)."""
        print("number of open orders", len(self.open_orders))
        while len(self.open_orders) > self.max_position:
            order_id = self.open_orders[-1]
            self.place_cancel_order(order_id)
            print('canceled excess order')

class Client(Trader):
    def __init__(self, trader_id, name, order_book, is_bot, max_position=15, max_vol = 1):
        super().__init__(
            trader_id = trader_id,
            name = name,
            order_book = order_book,
            is_bot = is_bot,
            max_position = max_position,
            balance = 1000,
            max_vol = max_vol,
        )



class MarketMaker(Trader):
    def __init__(self, trader_id, name, order_book, max_position, is_bot,
                 base_spread=0.0005,    # narrower base spread
                 inventory_coefficient=0.0005
                 ):
        super().__init__(
            trader_id = trader_id,
            name = name,
            order_book = order_book,
            is_bot = is_bot,
            max_position = max_position,
            balance = 1000,
            max_vol = 15,
        )
        self.base_spread = base_spread
        self.inv_coef = inventory_coefficient

    def trade(self):
        # Possibly skip 50% instead of 30%
        if random.random() < 0.5:
            return
        
        best_ask_price = self.order_book.get_best_ask()
        best_bid_price = self.order_book.get_best_bid() 

        if best_bid_price is None or best_ask_price is None:
            return

        spread = best_ask_price - best_bid_price
        if spread <= 0:
            # In case of malformed or crossed book
            return
        
        mid_price = (best_ask_price + best_bid_price) / 2
        
        base_spread_abs = self.base_spread * mid_price

        if spread > 2 * base_spread_abs:
            # The market is wide, so we narrow our quotes. 
            # Example: cut the existing spread in half.
            dynamic_spread = spread / 2  
        else:
            # The market is already tight, so quote around our base spread. 
            dynamic_spread = base_spread_abs
        

        buy_price = best_ask_price - 0.01
        sell_price = best_bid_price + 0.01

        if buy_price < sell_price:
            return # prevent crossing

        volume = random.uniform(0.001, 0.005)

        # Place limit buy
        self.place_limit_order('BTC', True, buy_price, volume)
        # Place limit sell
        self.place_limit_order('BTC', False, sell_price, volume)

        # If too many open orders
        if len(self.open_orders) > self.max_position:
            self.cancel_excess_orders()


# class MomentumTrader(Trader):
#     def __init__(self, trader_id, order_book, max_position, lookback):
#         super().__init__(trader_id, order_book, max_position)
#         self.lookback = lookback
#         self.prices = []

#     def add_price(self, price):
#         self.prices.append(price)

#     def trade(self):
#         if len(self.prices) < self.lookback:
#             return
        
#         price_change = self.prices[-1] - self.prices[0]
#         volume = random.randint(1, 10)

#         if price_change > 0:
#             self.place_market_order(is_buy=True, volume=volume)
#         elif price_change < 0:
#             self.place_market_order(is_buy=False, volume=volume)

# class MeanReversionTrader(Trader):
#     def __init__(self, trader_id, order_book, balance=1000, max_position=100, fair_price = 100000, threshold=2000):   
#         super().__init__(trader_id, order_book, balance, max_position)
#         self.fair_price = fair_price
#         self.threshold = threshold

#     def on_market_data(self, mid_price, asset):
#         print("Recevied mid price ", mid_price)
#         if random.random() < 0.5:
#             return  # skip trading half the time, for example

#         if mid_price < (self.fair_price - self.threshold):
#             volume = random.uniform(0.001, 0.005)
#             self.place_market_order(asset='BTC', is_buy=True, volume=volume)
#         elif mid_price > (self.fair_price + self.threshold):
#             volume = random.randint(0.001, 0.005)
#             self.place_market_order(asset='BTC', is_buy=False, volume=volume)

# class InstitutionalTrader(Trader):
#     def __init__(self, trader_id, order_book, max_position=500):
#         super().__init__(trader_id, order_book, max_position)

#     def trade(self):
#         while True:
#             time.sleep(random.uniform(2, 5))
#             trade_size = random.randint(20, 50)
#             if self.position < 0:
#                 self.place_limit_order(is_buy=True, price=self.fair_price - 10, volume=trade_size)
#             else:
#                 self.place_limit_order(is_buy=False, price=self.fair_price + 10, volume=trade_size)

# class RetailTrader(Trader):
#     def __init__(self, trader_id, order_book, max_position=500):
#         super().__init__(trader_id, order_book, max_position)

#     def trade(self, asset):
#         while True:
#             best_bid = self.order_book.get_best_bid()
#             best_ask = self.order_book.get_best_ask()
#             spread = best_ask - best_bid

#             action = random.random()
#             volume = random.randint(1, 5)
#             if action < 0.3:
#                 self.place_limit_order(asset, is_buy=True, price=best_ask, volume=volume)
#             else:
#                 if self.positions[asset] > 0 and self.positions[asset] > volume:
#                     self.place_limit_order(asset, is_buy=False, price=best_bid + spread, volume=volume)
#             time.sleep(2)
#             # else:
#             #     print('RetailTrader: Placing Market Order')
#             #     self.place_market_order(is_buy=False, volume=volume)

class BullTrader(Trader):
    def __init__(self, trader_id, name, order_book, is_bot, max_position=15, max_vol=1, buy_probability=0.8):
        super().__init__(
            trader_id = trader_id,
            name = name,
            order_book = order_book,
            is_bot = is_bot,
            max_position = max_position,
            balance = 1000,
            max_vol = 15,
        )
        self.buy_probability = buy_probability 

    def trade(self):
        # Throttle or skip sometimes
        if random.random() > self.buy_probability:
            return
        best_ask_price = self.order_book.get_best_ask()

        volume = random.uniform(0.01, 0.1)

        # self.cancel_excess_orders()

        # current_pos = self.positions.get('BTC', 0.0)
        # if current_pos >= self.max_vol:
        #     self.place_market_order('BTC', False, volume)
        #     print(f"reduce long position by {volume}, current position: {current_pos}")
        #     return

        buy_price = best_ask_price
        self.place_market_order('BTC', True, volume)
        print(f"market buy {volume} BTC at {buy_price}")


class BearTrader(Trader):
    def __init__(self, trader_id, name, order_book, is_bot, max_position=15, max_vol=1, sell_probability=0.8):
        super().__init__(
            trader_id = trader_id,
            name = name,
            order_book = order_book,
            is_bot = is_bot,
            max_position = max_position,
            max_vol = max_vol,
            balance = 1000,
        )
        self.sell_probability = sell_probability

    def trade(self):
        # Throttle or skip sometimes
        if random.random() > self.sell_probability:
            return
        
        best_bid_price = self.order_book.get_best_bid()

        volume = random.uniform(0.01, 0.1)

        # self.cancel_excess_orders()

        # current_pos = self.positions.get('BTC', 0.0)
        # if current_pos >= self.max_vol:
        #     self.place_market_order('BTC', True, volume)
        #     print(f"reduce long position by {volume}, current position: {current_pos}")
        #     return

        buy_price = best_bid_price
        self.place_market_order('BTC', False, volume)
        print(f"market sell {volume} BTC at {buy_price}")

class NoiseTrader(Trader):
    def __init__(self, trader_id, name, order_book, is_bot, max_position=1):
        super().__init__(
            trader_id = trader_id,
            name = name,
            order_book = order_book,
            is_bot = is_bot,
            max_position = max_position,
            max_vol = 1,
            balance = 1000,
        )

    def trade(self):
        if random.random() < 0.5:
            return

        is_buy = bool(random.getrandbits(1)) 
        volume = random.uniform(0.001, 0.01)

        best_ask_price = self.order_book.get_best_ask()
        best_bid_price = self.order_book.get_best_bid()

        mid_price = (best_ask_price + best_bid_price) / 2

        price_offset = random.uniform(0.0, 0.1) * mid_price

        if is_buy:
            price = best_ask_price - price_offset
        else:
            price = best_bid_price + price_offset

        # # position check
        # current_pos = self.positions.get('BTC', 0.0)
        # if is_buy and current_pos >= self.max_position:
        #     # skip
        #     return
        # if not is_buy and current_pos <= -self.max_position:
        #     # skip
        #     return

        self.place_limit_order('BTC', is_buy, price, volume)


