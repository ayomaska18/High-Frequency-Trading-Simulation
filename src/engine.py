from src.orderbook import orderbook
from src.order import order
import time

class engine:
    def __init__(self):
        self.order_book = orderbook()
        self.trade_history = [] 

    def add_order(self, order: order):
        print(f"Adding order: {order}")
        self.order_book.add_order(order)
        # self.match_orders()

    def match_orders(self):
        while True:
            best_buy = self.order_book.get_best_buy()
            best_sell = self.order_book.get_best_sell()

            if not best_buy or not best_sell:
                self.order_book.add_order(best_buy)
                self.order_book.add_order(best_sell)
                break

            if best_buy.price < best_sell.price:
                self.order_book.add_order(best_buy)
                self.order_book.add_order(best_sell)
                break

            trade_quantity = min(best_buy.quantity, best_sell.quantity)

            trade_price = best_sell.price

            print(f"Trade executed: {trade_quantity} units @ {trade_price}")

            self.trade_history.append({
                "buy_order_id": best_buy.id,
                "sell_order_id": best_sell.id,
                "quantity": trade_quantity,
                "price": trade_price,
                "timestamp": time.time(),
            })

            best_buy.quantity -= trade_quantity
            best_sell.quantity -= trade_quantity

            if best_buy.quantity != 0:
                self.order_book.add_order(best_buy)

            if best_sell.quantity != 0:
                self.order_book.add_order(best_sell)

    def get_trade_history(self):
        return self.trade_history
