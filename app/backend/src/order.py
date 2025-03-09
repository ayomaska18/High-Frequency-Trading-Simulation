class Order:
    def __init__(self, id, asset, is_buy, price, vol, timestamp):
        self.id = id
        self.asset = asset
        self.is_buy = is_buy
        self.price = price  
        self.vol = vol
        self.timestamp = timestamp
        self.prev = None
        self.next = None


    