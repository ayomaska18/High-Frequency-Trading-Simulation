from src.limit import Limit
from src.setting import *

class LimitTree:
    def __init__(self, is_bid_tree):
        self.root = None
        self.best_limit = None
        self.worst_limit = None
        self.limit_map = {} 
        self.is_bid_tree = is_bid_tree

    def insert_limit(self, price):
        price = int(price * PRICE_MULTIPLIER)
        price = round(price / TICK_MULTIPLIER) * TICK_MULTIPLIER

        if price in self.limit_map:
            return self.limit_map[price]

        limit = Limit(price)
        self.limit_map[price] = limit

        if not self.root:
            self.root = limit
            self.best_limit = price
            self.worst_limit = price
            return limit

        current = self.root

        while True:
            if price < current.price:
                if current.left:
                    current = current.left
                else:
                    current.left = limit
                    limit.parent = current
                    break
            else:
                if current.right:
                    current = current.right
                else:
                    current.right = limit
                    limit.parent = current
                    break

        if not self.is_bid_tree:
            self.best_limit = min(self.best_limit, price)
            self.worst_limit = max(self.worst_limit, price)
        else:
            self.best_limit = max(self.best_limit, price)
            self.worst_limit = min(self.worst_limit, price)

        return limit

    def remove_limit(self, price):
        price = int(price * PRICE_MULTIPLIER)
        price = round(price / TICK_MULTIPLIER) * TICK_MULTIPLIER
        
        if price not in self.limit_map:
            return
        
        limit = self.limit_map[price]

        del self.limit_map[price]

        if limit.left and limit.right: # if both left and right children exist
            successor = limit.right # find the inorder successor
            while successor.left:
                successor = successor.left
            limit.price = successor.price # copy the successor's data to this node
            limit.order_head = successor.order_head
            limit.order_tail = successor.order_tail
            self.remove_limit(successor.price) # delete the successor
        elif limit.left or limit.right:
            child = limit.left if limit.left else limit.right
            if limit == self.root:
                self.root = child
            elif limit.parent.left == limit:
                limit.parent.left = child
            else:
                limit.parent.right = child
            child.parent = limit.parent
        else:
            if limit == self.root:
                self.root = None
            elif limit.parent.left == limit:
                limit.parent.left = None
            else:
                limit.parent.right = None
        
        if price == self.best_limit or price == self.worst_limit:
            self.update_best_worst_price(price)
    
    def update_best_worst_price(self, price):
        curr = self.root

        if not self.is_bid_tree: # ask tree
            if price == self.best_limit: # previous best price was removed
                while curr.left:
                    curr = curr.left
                self.best_limit = curr.price
            else:  # previous worst price was removed
                while curr.right:
                    curr = curr.right
                self.worst_limit = curr.price
        else: # bid tree
            if price == self.best_limit:
                while curr.right:
                    curr = curr.right
                self.best_limit = curr.price
            else:
                while curr.left:
                    curr = curr.left
                self.worst_limit = curr.price
    
    def get_best_limit(self):
        return self.best_limit
    
    def get_worst_limit(self):
        return self.worst_limit
