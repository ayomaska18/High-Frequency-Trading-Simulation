class Order:
    def __init__(self, id, trader_id, asset, is_buy, price, vol, order_type, timestamp):
        self.id = id
        self.trader_id = trader_id
        self.asset = asset
        self.is_buy = is_buy
        self.price = price  
        self.vol = vol
        self.timestamp = timestamp
        self.order_type = order_type
        self.prev = None
        self.next = None


    