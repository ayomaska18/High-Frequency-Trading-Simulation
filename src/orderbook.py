from src.limit_tree import LimitTree
from src.ask import Ask
from src.bid import Bid
from src.order import Order
from src.setting import *


class OrderBook:
    def __init__(self):
        self.bid_tree = Bid()
        self.ask_tree = Ask()
        self.order_map = {} 

    def add_order(self, order: Order):
        """ Adds an order to the correct BST (bids or asks). """
        limit_tree = self.bid_tree if order.is_buy == True else self.ask_tree
        limit = limit_tree.insert_limit(order.price)
        limit.add(order)
        self.order_map[order.id] = order

    def cancel_order(self, order_id):
        """ Cancels an order by removing it from the DLL & BST. """
        if order_id not in self.order_map:
            return

        order = self.order_map[order_id]

        price = int(order.price * PRICE_MULTIPLIER)
        price = round(price / TICK_MULTIPLIER) * TICK_MULTIPLIER

        limit_tree = self.bid_tree if order.is_buy == True else self.ask_tree

        limit = limit_tree.limit_map[price]
        limit.remove(order)

        del self.order_map[order_id]

        if not limit.order_head:  # Remove price level if no orders left
            print('here')
            limit_tree.remove_limit(order.price)
        

    def get_best_bid(self):
        """ Returns best bid price directly from BidTree. """
        return self.bid_tree.best_limit

    def get_best_ask(self):
        """ Returns best ask price directly from AskTree. """
        return self.ask_tree.best_limit
    
    def display_order_book(self):
        """ Displays all orders in the order book with correct decimal precision. """
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
        """ Helper function to get orders from a BST in sorted order. """
        result = {}
        self._inorder_traverse(tree.root, result)
        return dict(sorted(result.items(), reverse=not ascending))

    def _inorder_traverse(self, node, result):
        """ Helper function for in-order traversal of BST. """
        if node is None:
            return
        self._inorder_traverse(node.left, result)
        result[node.price] = node.get_total_vol()
        self._inorder_traverse(node.right, result)

