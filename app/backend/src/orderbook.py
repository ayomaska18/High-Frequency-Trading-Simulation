from .limit_tree import LimitTree
from .ask import Ask
from .bid import Bid
from .order import Order
from .setting import *
from .utility import enforce_tick_size, convert_to_price
import time
import random
import requests
import os
import asyncio
from IPython.display import display
from dotenv import load_dotenv
from .pubsub import publish

load_dotenv()

class OrderBook:
    def __init__(self):
        self.bid_tree = Bid()
        self.ask_tree = Ask()
        self.order_map = {} 

    def add_order(self, order: Order):
        limit_tree = self.bid_tree if order.is_buy == True else self.ask_tree
        price = enforce_tick_size(order.price)
        limit = limit_tree.insert_limit(price)
        limit.add(order)
        self.order_map[order.id] = order

    def cancel_order(self, order_id):
        if order_id not in self.order_map:
            return

        order = self.order_map[order_id]

        price = enforce_tick_size(order.price)

        limit_tree = self.bid_tree if order.is_buy == True else self.ask_tree

        limit = limit_tree.limit_map[price]
        limit.remove(order)

        del self.order_map[order_id]

        if not limit.order_head: 
            limit_tree.remove_limit(price)
        
        return {'status': 'Order Cancelled'}
        

    def get_best_bid(self):
        return convert_to_price(self.bid_tree.best_limit)

    def get_best_ask(self):
        return convert_to_price(self.ask_tree.best_limit)
    
    def display_order_book(self):
        print("\n" + "="*50)
        print(" ORDER BOOK")
        print("="*50)
        print(f"{'Price':<15} | {'Ask Size':<10} | {'Bid Size':<10}")
        print("-" * 50)

        ask_prices = self._get_sorted_orders(self.ask_tree, ascending=True)
        bid_prices = self._get_sorted_orders(self.bid_tree, ascending=False)

        all_prices = sorted(set(ask_prices.keys()).union(set(bid_prices.keys())), reverse=True)

        for price in all_prices:
            formatted_price = price / PRICE_MULTIPLIER  # Convert back to decimal
            ask_size = ask_prices.get(price, 0)
            bid_size = bid_prices.get(price, 0)
            print(f"{formatted_price:<15.8f} | {ask_size:<10} | {bid_size:<10}")

        print("="*50)

    def _get_sorted_orders(self, tree, ascending=True):
        result = {}
        self._inorder_traverse(tree.root, result)
        return dict(sorted(result.items(), reverse=not ascending))

    def _inorder_traverse(self, node, result):
        if node is None:
            return
        self._inorder_traverse(node.left, result)
        result[node.price] = node.get_total_vol()
        self._inorder_traverse(node.right, result)

    async def send_fill_event(self, message):
        await publish(message)
    
    def market_order_match(self, order):
        from .trader_manager import traderManager
        limit_tree = self.ask_tree if order.is_buy else self.bid_tree
        
        while limit_tree.limit_map and order.vol > 0:
            best_limit_price = limit_tree.get_best_limit()

            best_limit = limit_tree.limit_map[best_limit_price]

            if not best_limit:
                print("Insufficient Liquidity to fill order")
                return {'status': 'Insufficient Liquidity to fill order'}    
           
            if not best_limit:
                print(f"[Warning] Limit node for {best_limit_price} disappeared. Moving on. (market order)")
                break

            while best_limit.order_head and order.vol > 0:
                head_order = best_limit.order_head
                trade_quantity = min(order.vol, head_order.vol)

                order.vol -= trade_quantity
                head_order.vol -= trade_quantity

                if head_order.vol <= 0:
                    self.cancel_order(head_order.id)

                    asyncio.create_task(self.send_fill_event({
                        "order_id": head_order.id,
                        "asset": head_order.asset,
                        "is_buy": head_order.is_buy,
                        "trader_id": head_order.trader_id,
                        "price": head_order.price,
                        "volume": trade_quantity,
                        "order_type": head_order.order_type,
                    }))

                if order.vol == 0:
                    asyncio.create_task(self.send_fill_event({
                        "order_id": order.id,
                        "asset": order.asset,
                        "is_buy": order.is_buy,
                        "trader_id": order.trader_id,
                        "price": head_order.price,
                        "volume": trade_quantity,
                        "order_type": order.order_type,
                    }))

            if not best_limit.order_head:
                limit_tree.remove_limit(best_limit_price)
                limit_tree.update_best_worst_price(best_limit_price)

        if not limit_tree.limit_map and order.vol:
            print("Insufficient Liquidity to fill order")
            return {'status': 'Insufficient Liquidity to fill order'}    
        return {'status': 'Order Filled'}
            
    def limit_order_match(self, order: Order):
        from .trader_manager import traderManager
        limit_tree = self.ask_tree if order.is_buy else self.bid_tree
        limit_price = enforce_tick_size(order.price)

        print("limit_price: ", limit_price)

        while order.vol > 0 and limit_tree.limit_map:
            best_limit_price = limit_tree.get_best_limit() 
            limit_node = limit_tree.get_limit(limit_price)

            if not limit_node:
                print(f"[Warning] Limit node for {limit_node.price} disappeared. Moving on. (limit order)")
                break

            while limit_node.order_head and order.vol > 0:
                head_order = limit_node.order_head
                trade_quantity = min(order.vol, head_order.vol)

                if trade_quantity < 1e-8:
                    print("[Warning] Extremely small trade_quantity — breaking to avoid infinite loop.")
                    order.vol = 0
                    self.cancel_order(head_order.id)
                    break

                order.vol -= trade_quantity
                head_order.vol -= trade_quantity

                if head_order.vol <= 0:
                    self.cancel_order(head_order.id)
                    asyncio.create_task(self.send_fill_event({
                        "order_id": head_order.id,
                        "asset": head_order.asset,
                        "is_buy": head_order.is_buy,
                        "trader_id": head_order.trader_id,
                        "price": head_order.price,
                        "volume": trade_quantity,
                        "order_type": head_order.order_type,
                    }))

                if order.vol == 0:
                    asyncio.create_task(self.send_fill_event({
                        "order_id": order.id,
                        "asset": order.asset,
                        "is_buy": order.is_buy,
                        "trader_id": order.trader_id,
                        "price": head_order.price,
                        "volume": trade_quantity,
                        "order_type": order.order_type,
                    }))

            if limit_node and not limit_node.order_head: # remove price level from ob
                limit_tree.remove_limit(best_limit_price)
                limit_tree.update_best_worst_price(best_limit_price) # update best price if applicable
                print('remove limit node from order book')

        if order.vol > 0: # if current order is not fully filled, add to ob
            self.add_order(order)
            print(f"Partial fill. {order.vol} remains, resting at limit price {limit_price / PRICE_MULTIPLIER:.4f}")
            return {'status': 'Partial Fill - Order Resting'}

        return {'status': 'Order Filled'}


    def get_curent_order_book_snapshot(self):
        api_key = os.getenv("COINAPI_API_KEY")
        url = "https://rest.coinapi.io/v1/orderbooks/BINANCE_SPOT_BTC_USDT/current"
        payload = {}
        headers = {
            'Accept': 'text/plain',
            'X-CoinAPI-Key': api_key
                  }
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code != 200:
            return "Error fetching order book snapshot"
        
        data = response.json()
    
        bids, asks = data['bids'], data['asks']

        return bids, asks


    def initialize_order_book(self):
        """ Populates the order book with a fair price of 100 and random volume levels. """
        bids, asks = self.get_curent_order_book_snapshot()

        for i, bid in enumerate(bids):
            bid_price = bid["price"]
            bid_vol = bid["size"]

            bid_order = Order(
                id=i,
                trader_id=None,
                asset="BTC",
                is_buy=True,
                price=bid_price,
                vol=bid_vol,
                order_type="LIMIT",
                timestamp=time.time()
            )

            self.add_order(bid_order)
            # print(f"Order Added: BUY {bid_vol} @ {bid_price}")

        offset = len(bids) 
        for j, ask in enumerate(asks):
            ask_price = ask["price"]
            ask_vol = ask["size"]

            ask_order = Order(
                id=offset + j,
                trader_id=None,
                asset="BTC",
                is_buy=False,
                price=ask_price,
                vol=ask_vol,
                order_type="LIMIT",
                timestamp=time.time()
            )
            
            self.add_order(ask_order)
            # print(f"Order Added: SELL {ask_vol} @ {ask_price}")

        print("\nOrder book initialized from snapshot!\n")

    def fetch_order_book(self):
        bids_limit_map_copy = list(self.bid_tree.limit_map.items())
        asks_limit_map_copy = list(self.ask_tree.limit_map.items())

        bids = []
        asks = []

        for price, limit in bids_limit_map_copy:
            price_decimal = round(price / 10**8, 4)
            total_volume = sum(order.vol for order in limit.iter_orders())
            if total_volume > 0:
                bids.append([price_decimal, total_volume])

        for price, limit in asks_limit_map_copy:
            price_decimal = round(price / 10**8, 4)
            total_volume = sum(order.vol for order in limit.iter_orders())
            if total_volume > 0:
                asks.append([price_decimal, total_volume])

        bids.sort(key=lambda x: x[0], reverse=True)
        asks.sort(key=lambda x: x[0])
        
        return {"bids": bids, "asks": asks}


order_book = OrderBook()
order_book.initialize_order_book()
# print(order_book.get_best_ask)
# print(order_book.get_best_bid)

# def test_best_bid_example():
#     # Clear the order book first if you have a method for that
#     # For example:
#     # order_book.bid_tree = Bid()
#     # order_book.ask_tree = Ask()
#     # order_book.order_map = {}
#     order_book = OrderBook()

#     # Create some buy orders at various prices
#     buy_order_1 = Order(
#         id=1,
#         asset="BTC",
#         is_buy=True,
#         price=100.00,   # USD
#         vol=1.0,
#         timestamp=time.time()
#     )

#     buy_order_2 = Order(
#         id=2,
#         asset="BTC",
#         is_buy=True,
#         price=105.50,
#         vol=0.5,
#         timestamp=time.time()
#     )

#     buy_order_3 = Order(
#         id=3,
#         asset="BTC",
#         is_buy=True,
#         price=103.20,
#         vol=2.0,
#         timestamp=time.time()
#     )

#     # Add these orders to the order book
#     order_book.add_order(buy_order_1)
#     order_book.add_order(buy_order_2)
#     order_book.add_order(buy_order_3)

#     # Optionally, add some sell orders so we have an ask side:
#     sell_order_1 = Order(
#         id=4,
#         asset="BTC",
#         is_buy=False,
#         price=108.10,
#         vol=1.0,
#         timestamp=time.time()
#     )
#     order_book.add_order(sell_order_1)

#     # Now print out the best bid and best ask
#     print("Best Bid:", order_book.get_best_bid())  # Expect 105.50
#     print("Best Ask:", order_book.get_best_ask())  # Expect 108.10

#     # Display the order book to see how everything lines up
#     order_book.display_order_book()

# if __name__ == "__main__":
#     test_best_bid_example()

