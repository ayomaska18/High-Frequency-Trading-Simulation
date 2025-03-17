import React, { useEffect, useState, useContext } from "react";
import { WebSocketContext } from "./WebSocketContext";

const OrderBook = () => {
    const context = useContext(WebSocketContext);
    const { bids, asks, midPrice } = useContext(WebSocketContext);

    if (!context) {
        console.error("WebSocketContext is not available!");
        return <div>Loading WebSocket data...</div>;
    }

    return (
        <div className="orderbook-container">
            <div className="orderbook-header">
                <span>Price (USDT)</span>
                <span>Amount (BTC)</span>
                <span>Total</span>
            </div>

            {/* Asks (Sell Orders) */}
            <div className="orderbook-asks">
                {asks.slice(0, 10).map((ask, index) => (
                    <div key={index} className="order ask">
                        <span className="price red">{(ask[0] || 0).toFixed(2)}</span>
                        <span className="size">{(ask[1] || 0).toFixed(6)}</span>
                        <span className="total">{((ask[0] || 0) * (ask[1] || 0)).toFixed(2)}</span>
                    </div>
                ))}
            </div>

            {/* Last Price (Middle) */}
            <div className="orderbook-last-price">
                <span className="mark-price">Mark: {(midPrice || 0).toFixed(2)}</span>
            </div>

            {/* Bids (Buy Orders) */}
            <div className="orderbook-bids">
                {bids.slice(0, 10).reverse().map((bid, index) => (
                    <div key={index} className="order bid">
                        <span className="price green">{(bid[0] || 0).toFixed(2)}</span>
                        <span className="size">{(bid[1] || 0).toFixed(6)}</span>
                        <span className="total">{((bid[0] || 0) * (bid[1] || 0)).toFixed(2)}</span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default OrderBook;