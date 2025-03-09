from .limit_tree import LimitTree

class Bid(LimitTree):
    def __init__(self):
        super().__init__(is_bid_tree=True)
