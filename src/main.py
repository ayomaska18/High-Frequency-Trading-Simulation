from src.orderbook import OrderBook
from src.order import Order
import time

def main():

    order_book = OrderBook()

    # # Add buy and sell orders
    order_book.add_order(Order(id=1, is_buy=False, price=100, vol=10, timestamp=time.time()))
    order_book.add_order(Order(id=2, is_buy=False, price=102, vol=5, timestamp=time.time()))
    order_book.add_order(Order(id=3, is_buy=False, price=101, vol=7, timestamp=time.time()))
    order_book.add_order(Order(id=4, is_buy=True, price=99, vol=4, timestamp=time.time()))
    order_book.add_order(Order(id=5, is_buy=True, price=98, vol=5, timestamp=time.time()))
    order_book.add_order(Order(id=6, is_buy=True, price=97, vol=7, timestamp=time.time()))

    order_book.display_order_book()

    # order_book.cancel_order(1)

    # order_book.display_order_book()
    # order_book.live_order_book()
    order_book.market_order_match(Order(id=7, is_buy=True, price=0, vol=12, timestamp=time.time()))
    order_book.market_order_match(Order(id=7, is_buy=False, price=0, vol=5, timestamp=time.time()))

    order_book.display_order_book()

if __name__ == "__main__":
    main()