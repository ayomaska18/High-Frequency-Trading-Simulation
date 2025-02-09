from src.limit_tree import LimitTree
from src.ask import Ask
from src.bid import Bid
from src.order import Order
from src.setting import *
from src.utility import enforce_tick_size
import matplotlib.pyplot as plt
import time
import random


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

        if not limit.order_head:  # Remove price level if no orders left
            limit_tree.remove_limit(price)
        

    def get_best_bid(self):
        return self.bid_tree.best_limit

    def get_best_ask(self):
        return self.ask_tree.best_limit
    
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

            if not best_limit:
                print("Insufficient Liquidity to fill order")
                return

            limit = limit_tree.limit_map[best_limit]

            while limit.order_head and order.vol > 0: # current price level orders
                head_order = limit.order_head
                trade_quantity = min(order.vol, head_order.vol)

                if order.is_buy:
                    print(f"Market Order Buy: {trade_quantity} @ {best_limit}")
                else:
                    print(f"Market Order Sell: {trade_quantity} @ {best_limit}")

                order.vol -= trade_quantity
                head_order.vol -= trade_quantity

                if head_order.vol == 0:
                    self.cancel_order(head_order.id)
                
            if not limit.order_head:
                limit_tree.remove_limit(best_limit)
                limit_tree.update_best_worst_price(best_limit)
        
        if not limit_tree.limit_map and order.vol:
            print("Insufficient Liquidity to fill order")
            return
        
        return "Order Filled"
            
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
            return "Price not in order book. Order added to order book."
        
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
            return       
        
        return "Order Filled"
    
    def plot_order_book(self):
        bid_prices = []
        bid_volumes = []
        ask_prices = []
        ask_volumes = []

        # Extract bids
        for price, limit in self.bid_tree.limit_map.items():
            price_decimal = price / 10**8  # Convert back to decimal
            if MIN_PRICE <= price_decimal <= MAX_PRICE:
                bid_prices.append(price_decimal)
                bid_volumes.append(sum(order.vol for order in limit.iter_orders()))

        # Extract asks
        for price, limit in self.ask_tree.limit_map.items():
            price_decimal = price / 10**8  # Convert back to decimal
            if MIN_PRICE <= price_decimal <= MAX_PRICE: 
                ask_prices.append(price_decimal)
                ask_volumes.append(sum(order.vol for order in limit.iter_orders()))

        plt.clf()  # Clear the previous frame
        plt.bar(bid_prices, bid_volumes, width=TICK_SIZE, color='green', label='Bids', alpha=0.6)
        plt.bar(ask_prices, ask_volumes, width=TICK_SIZE, color='red', label='Asks', alpha=0.6)
        plt.xlim(MIN_PRICE, MAX_PRICE)  
        plt.xlabel("Price")
        plt.ylabel("Volume")
        plt.title("Live Order Book")
        plt.legend()
        plt.pause(0.1)  # Update rate

    def live_order_book(self):
        plt.ion()  # Turn on interactive mode

        while True:
            self.plot_order_book() 

            # Simulate adding random orders within the fixed range
            side = random.choice(["buy", "sell"])
            price = round(random.uniform(MIN_PRICE, MAX_PRICE), 4) 
            volume = random.randint(1, 10)

            is_buy = side == "buy"
            order = Order(
                id=int(time.time()),  # Unique ID
                is_buy=is_buy,
                price=price,
                vol=volume,
                timestamp=time.time(),
            )

            self.limit_order_match(order)
            time.sleep(1)  # Update every second