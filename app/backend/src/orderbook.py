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
from IPython.display import display
from dotenv import load_dotenv

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
    
    def market_order_match(self, order):
        limit_tree = self.ask_tree if order.is_buy else self.bid_tree
        
        while limit_tree.limit_map and order.vol > 0:
            best_limit = limit_tree.get_best_limit()
            print("best_limit", best_limit)

            if not best_limit:
                print("Insufficient Liquidity to fill order")
                return order.vol    

            limit = limit_tree.limit_map[best_limit]
            print('limit:', limit)

            while limit.order_head and order.vol > 0: # current price level orders
                head_order = limit.order_head
                trade_quantity = min(order.vol, head_order.vol)
                
                if trade_quantity < 1e-8:
                    # Force volumes to zero or break
                    print("[Warning] trade_quantity is extremely small, breaking to avoid infinite loop.")
                    order.vol = 0
                    head_order.vol = 0
                    break

                order.vol -= trade_quantity
                head_order.vol -= trade_quantity

                if head_order.vol == 0:
                    self.cancel_order(head_order.id)
                print('trade_quantity', trade_quantity)
                
            if not limit.order_head:
                limit_tree.remove_limit(best_limit)
                limit_tree.update_best_worst_price(best_limit)
        
        if not limit_tree.limit_map and order.vol:
            print("Insufficient Liquidity to fill order")
            return order.vol
        
        return 0
            
    def limit_order_match(self, order):
        """ 
        Matches an incoming order with the best available order in the order book. 
        1. check if order is a buy or sell order
        2. check if the price level is in the order book (dict)
        3. if price level is in the order book, get the head order of the order list, else add order to the order book
        4. if incoming_order.vol == order.vol, remove order from linked_list
        5. if incoming_order.vol < order.vol, reduce vol of the head order
        6. if incoming_order.vol > order.vol, remove head order, get next order - the remaining vol, repeat until incoming_order.vol == 0 (parital fill)
        7. if still have remaining vol, add the order to the order book
        8. update tree if no order in current price level
        9. update best, worst bid and ask
        9. return status
        """
        limit_tree = self.ask_tree if order.is_buy else self.bid_tree
        
        price = enforce_tick_size(order.price)

        if price in limit_tree.limit_map:
            limit = limit_tree.limit_map[price]
        else:
            self.add_order(order)
            return order.vol
        
        while limit.order_head and order.vol > 0:
            head_order = limit.order_head

            trade_quantity = min(order.vol, head_order.vol)

            print(f"Limit Order Trade: {trade_quantity} @ {price}")
            order.vol -= trade_quantity
            head_order.vol -= trade_quantity

            if head_order.vol == 0:
                self.cancel_order(head_order.id)
                
        if not limit.order_head:
            limit_tree.remove_limit(price)
            limit_tree.update_best_worst_price(price)
        
        if order.vol > 0:
            self.add_order(order) 
            print('Order filled partially')
            return order.vol
        
        return 0

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
                asset="BTC",
                is_buy=True,
                price=bid_price,
                vol=bid_vol,
                timestamp=time.time()
            )

            self.add_order(bid_order)
            print(f"Order Added: BUY {bid_vol} @ {bid_price}")

        offset = len(bids) 
        for j, ask in enumerate(asks):
            ask_price = ask["price"]
            ask_vol = ask["size"]

            ask_order = Order(
                id=offset + j,
                asset="BTC",
                is_buy=False,
                price=ask_price,
                vol=ask_vol,
                timestamp=time.time()
            )
            
            self.add_order(ask_order)
            print(f"Order Added: SELL {ask_vol} @ {ask_price}")

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

        print(bids)
        print(asks)
        
        return {"bids": bids, "asks": asks}


order_book = OrderBook()
order_book.initialize_order_book()
