import React, { useEffect, useState } from "react";

const WEBSOCKET_URL = "ws://127.0.0.1:8000/orderbook/ws"; // ✅ Your WebSocket URL

const OrderBook = () => {
    const [bids, setBids] = useState([]);
    const [asks, setAsks] = useState([]);
    const [lastPrice, setLastPrice] = useState(0);
    const [markPrice, setMarkPrice] = useState(0);

    useEffect(() => {
        const socket = new WebSocket(WEBSOCKET_URL);

        socket.onopen = () => {
            console.log("✅ WebSocket connected");
        };

        socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                setBids(Array.isArray(data.bids) ? data.bids : []);
                setAsks(Array.isArray(data.asks) ? data.asks : []);
                setMarkPrice(typeof data.markPrice === "number" ? data.markPrice : 0);
                setLastPrice(typeof data.lastPrice === "number" ? data.lastPrice : data.markPrice);
            } catch (error) {
                console.error("❌ WebSocket Error Parsing Data:", error);
            }
        };

        socket.onerror = (error) => console.error("❌ WebSocket Error:", error);

        socket.onclose = () => {
            console.log("🔄 WebSocket closed, reconnecting...");
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        };

        return () => socket.close();
    }, []);

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
                <span className="last-price">{(lastPrice || 0).toFixed(2)}</span>
                <span className="mark-price">Mark: {(markPrice || 0).toFixed(2)}</span>
            </div>

            {/* Bids (Buy Orders) */}
            <div className="orderbook-bids">
                {bids.slice(0, 10).map((bid, index) => (
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
