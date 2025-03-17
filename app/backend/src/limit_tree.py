from .limit import Limit
from .setting import *

class LimitTree:
    def __init__(self, is_bid_tree):
        self.root = None
        self.best_limit = None
        self.worst_limit = None
        self.limit_map = {} 
        self.is_bid_tree = is_bid_tree

    def insert_limit(self, price):
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
        if price not in self.limit_map:
            return
        
        limit = self.limit_map[price]

        del self.limit_map[price]

        if limit.left and limit.right:
            successor = limit.right 
            while successor.left:
                successor = successor.left
            limit.price = successor.price 
            limit.order_head = successor.order_head
            limit.order_tail = successor.order_tail
            self.remove_limit(successor.price) 
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

        if not self.is_bid_tree:
            if price == self.best_limit:
                while curr.left:
                    curr = curr.left
                self.best_limit = curr.price
            else:
                while curr.right:
                    curr = curr.right
                self.worst_limit = curr.price
        else: 
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

def print_tree_info(title, tree: LimitTree):
    print(f"--- {title} ---")
    if tree.root is None:
        print("Tree is empty.")
    else:
        best = tree.get_best_limit()
        worst = tree.get_worst_limit()
        print(f"Best limit: {best}")
        print(f"Worst limit: {worst}")

    print(f"Tree limit_map keys: {list(tree.limit_map.keys())}\n")


def test_bid_tree_operations():
    bid_tree = LimitTree(is_bid_tree=True)
    prices_to_insert = [100, 105, 95, 99, 107, 93, 101]
    
    for price in prices_to_insert:
        bid_tree.insert_limit(price)
        print_tree_info(f"After inserting {price}", bid_tree)
    
    node_to_remove = 93
    bid_tree.remove_limit(node_to_remove)
    print_tree_info(f"After removing leaf node {node_to_remove}", bid_tree)

    node_to_remove = 99
    bid_tree.remove_limit(node_to_remove)
    print_tree_info(f"After removing node {node_to_remove} (one child)", bid_tree)


    node_to_remove = 100
    bid_tree.remove_limit(node_to_remove)
    print_tree_info(f"After removing node {node_to_remove} (two children)", bid_tree)

    
    node_to_remove = 107
    bid_tree.remove_limit(node_to_remove)
    print_tree_info(f"After removing node {node_to_remove} (two children)", bid_tree)


def test_ask_tree_operations():
    ask_tree = LimitTree(is_bid_tree=False)
    prices_to_insert = [100, 95, 105, 99, 93, 107, 101]
    
    for price in prices_to_insert:
        ask_tree.insert_limit(price)
        print_tree_info(f"After inserting {price}", ask_tree)
    
    node_to_remove = 107
    ask_tree.remove_limit(node_to_remove)
    print_tree_info(f"After removing leaf node {node_to_remove}", ask_tree)

    node_to_remove = 99
    ask_tree.remove_limit(node_to_remove)
    print_tree_info(f"After removing node {node_to_remove} (one child)", ask_tree)

    node_to_remove = 100
    ask_tree.remove_limit(node_to_remove)
    print_tree_info(f"After removing node {node_to_remove} (two children)", ask_tree)

if __name__ == "__main__":
    test_bid_tree_operations()




