from src.orderbook import OrderBook
from src.order import Order
import time
import random
import threading
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from src.setting import *
from src.trader import Trader

# Initialize the order book
order_book = OrderBook()

def generate_random_orders():
    """ Continuously adds multiple random bid and ask orders per second. """
    while True:
        for _ in range(ORDERS_PER_SECOND):  
            side = random.choice(["buy", "sell"])
            price = round(random.uniform(MIN_PRICE, MAX_PRICE), 4)  
            volume = random.randint(1, 10)  

            is_buy = side == "buy"
            order = Order(
                id=int(time.time() * 1000),  
                is_buy=is_buy,
                price=price,
                vol=volume,
                timestamp=time.time(),
            )

            # Add the order to the order book
            order_book.limit_order_match(order)
            print(f"Added Order: {side.upper()} {volume} @ {price}")

        time.sleep(0.2)  

def main():
    """ Starts the Dash server and high-frequency order generation thread. """

    order_book.initialize_order_book()

    # Create multiple traders with different strategies
    traders = [
        Trader(trader_id=1, order_book=order_book, strategy="random"),
        Trader(trader_id=2, order_book=order_book, strategy="market_maker"),
        Trader(trader_id=3, order_book=order_book, strategy="market_maker"),
        Trader(trader_id=4, order_book=order_book, strategy="market_maker"),
        Trader(trader_id=5, order_book=order_book, strategy="market_maker"),
        Trader(trader_id=6, order_book=order_book, strategy="market_maker"),
        Trader(trader_id=7, order_book=order_book, strategy="market_maker"),
        Trader(trader_id=8, order_book=order_book, strategy="market_maker"),
        Trader(trader_id=9, order_book=order_book, strategy="market_maker"),
        Trader(trader_id=10, order_book=order_book, strategy="market_maker"),
        Trader(trader_id=11, order_book=order_book, strategy="random"),
        Trader(trader_id=12, order_book=order_book, strategy="random"),
        Trader(trader_id=13, order_book=order_book, strategy="random"),
        Trader(trader_id=14, order_book=order_book, strategy="random"),
        Trader(trader_id=15, order_book=order_book, strategy="random"),
        Trader(trader_id=16, order_book=order_book, strategy="random"),
        Trader(trader_id=17, order_book=order_book, strategy="random")
        
    ]

    # Start each trader in a separate thread
    for trader in traders:
        trader_thread = threading.Thread(target=trader.trade, daemon=True)
        trader_thread.start()

    # Dash App Setup
    app = dash.Dash(__name__)
    app.layout = html.Div([
        html.H1("Live Order Book"),
        dcc.Graph(id='order-book-graph'),
        dcc.Interval(id='interval-component', interval=500, n_intervals=0)  # Updates every 0.5s
    ])

    @app.callback(Output('order-book-graph', 'figure'), Input('interval-component', 'n_intervals'))
    def update_graph(n):
        """ Updates the graph with the latest order book data. """

        bid_prices = []
        bid_volumes = []
        ask_prices = []
        ask_volumes = []

        # Extract bids
        for price, limit in order_book.bid_tree.limit_map.items():
            price_decimal = price / 10**8 
            price_decimal = round(price_decimal, 4)
            bid_prices.append(price_decimal)
            bid_volumes.append(sum(order.vol for order in limit.iter_orders()))

        # Extract asks
        for price, limit in order_book.ask_tree.limit_map.items():
            price_decimal = price / 10**8 
            price_decimal = round(price_decimal, 4)
            ask_prices.append(price_decimal)
            ask_volumes.append(sum(order.vol for order in limit.iter_orders()))

        # Create new figure
        fig = go.Figure()
        fig.add_trace(go.Bar(x=bid_prices, y=bid_volumes, name='Bids', marker_color='green'))
        fig.add_trace(go.Bar(x=ask_prices, y=ask_volumes, name='Asks', marker_color='red'))

        fig.update_layout(
            title="Live Order Book",
            xaxis_title="Price",
            yaxis_title="Volume",
            xaxis=dict(tickformat=".4f")
        )

        return fig

    app.run_server(debug=True)

if __name__ == "__main__":
    main()
