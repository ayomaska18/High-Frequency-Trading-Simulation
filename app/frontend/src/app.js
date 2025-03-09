import React from "react";
import MyOrderBook from "./components/OrderBook";
import TradingView from "./components/TradingView";
import "./static/styles.css";
import "./static/orderbook.css";

const App = () => {
    console.log("App Component is rendering...");
    return (
        <div className="app">
            <div className="orderbook-container">
                <MyOrderBook />
            </div>
            <div className="chart-container">
                <TradingView />
            </div>
        </div>
    );
};

export default App;
