import React, { createContext, useEffect, useState } from "react";

const WEBSOCKET_URL = "ws://127.0.0.1:8000/orderbook/ws";

export const WebSocketContext = createContext(null);

export const WebSocketProvider = ({ children }) => {
    const [bids, setBids] = useState([]);
    const [asks, setAsks] = useState([]);
    const [midPrice, setMidPrice] = useState(0);
    const [isConnected, setIsConnected] = useState(false);
    const [socket, setSocket] = useState(null);

    useEffect(() => {
        let ws;

        const connectWebSocket = () => {
            ws = new WebSocket(WEBSOCKET_URL);
            setSocket(ws);

            ws.onopen = () => {
                console.log("WebSocket connected");
                setIsConnected(true);
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
            
                    setBids(data.bids || []);
                    setAsks(data.asks || []);
                    setMidPrice(data.midPrice || 0);
                } catch (error) {
                    console.error("WebSocket Error Parsing Data:", error);
                }
            };
            
            ws.onerror = (error) => console.error("WebSocket Error:", error);

            ws.onclose = () => {
                console.log("🔄 WebSocket closed, reconnecting in 2s...");
                setIsConnected(false);
                setTimeout(connectWebSocket, 2000);
            };
        };

        connectWebSocket();

        return () => {
            if (ws) ws.close();
        };
    }, []);

    return (
        <WebSocketContext.Provider value={{ bids, asks, midPrice }}>
            {children}
        </WebSocketContext.Provider>
    );
};

export default WebSocketProvider;
