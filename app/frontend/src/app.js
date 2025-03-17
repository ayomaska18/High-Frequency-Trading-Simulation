import React from "react";
import MyOrderBook from "./components/OrderBook";
import TradingView from "./components/TradingView";
import TraderControls from "./components/TraderControl";
import { WebSocketProvider } from "./components/WebSocketContext";
import "./static/styles.css";
import "./static/orderbook.css";

const App = () => {
    return (
        <WebSocketProvider>
            <div className="app-container">
                <h1 className="title">High-Frequency Trading Simulation</h1>
                
                <div className="main-content">
                        <MyOrderBook />
                    <div className="chart-container large-chart">
                        <TradingView />
                    </div>
                </div>
                
                <div className="controls-container">
                    <TraderControls />
                </div>
            </div>
        </WebSocketProvider>
    );
};

export default App;
