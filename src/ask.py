from src.limit_tree import LimitTree

class Ask(LimitTree):
    def __init__(self):
        super().__init__(is_bid_tree=False)
