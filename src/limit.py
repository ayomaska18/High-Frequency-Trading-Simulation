from src.order import Order

class Limit:
    def __init__(self, price):
        self.price = price
        self.order_head = None 
        self.order_tail = None
        self.total_volume = 0
        self.parent = None
        self.left = None 
        self.right = None

    def add(self, order: Order):
        if self.order_tail:
            self.order_tail.next_order = order
            order.prev = self.order_tail
            self.order_tail = order
        else:
            self.order_head = self.order_tail = order

        self.total_volume += order.vol

    def remove(self, order: Order):
        if order.prev and order.next: # if order is in the middle
            order.prev.next = order.next
            order.next.prev = order.prev
        elif order.prev: # if order is the tail
            order.prev.next = None
            self.order_tail = order.prev
        elif order.next: # if order is the head
            order.next.prev = None
            self.order_head = order.next
        else:
            self.order_head = self.order_tail = None

        self.total_volume -= order.vol
    
    def get_total_vol(self):
        return self.total_volume
    
    def iter_orders(self):
        current = self.order_head
        while current:
            yield current
            current = current.next 
