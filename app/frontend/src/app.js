import React, { useState } from "react";
import MyOrderBook from "./components/OrderBook";
import TradingView from "./components/TradingView";
import TraderControls from "./components/TraderControl";
import { WebSocketProvider } from "./components/WebSocketContext";
import TraderPanel from "./components/TraderPanel";
import MarketTrades from "./components/MarketTrades";
import "./static/styles.css";
import "./static/orderbook.css";
import "./static/trader_panel.css";

const App = () => {
    const [realTraderId, setRealTraderId] = useState(null);

    return (
        <WebSocketProvider>
            <div className="app-container">
                <h1 className="title">High-Frequency Trading Simulation</h1>
                
                <div className="main-content">
                        <MyOrderBook />
                    <div className="chart-and-trades">
                        <TradingView />
                        <MarketTrades traderId={realTraderId}/>
                    </div>
                </div>

                <div className="trader-orders-container">
                        <TraderPanel setRealTraderId={setRealTraderId}/>
                </div>
                
                <div className="controls-container">
                    <TraderControls />
                </div>
            </div>
        </WebSocketProvider>
    );
};

export default App;
