import React, { createContext, useEffect, useState } from "react";

const ORDERBOOK_WEBSOCKET_URL = "ws://127.0.0.1:8000/orderbook/ws";
// const ORDER_WEBSOCKET_URL = "ws://127.0.0.1:8000/orderbook/ws"

export const WebSocketContext = createContext(null);

export const WebSocketProvider = ({ children }) => {
    const [bids, setBids] = useState([]);
    const [asks, setAsks] = useState([]);
    const [mid_price, setMidPrice] = useState(0);
    const [ohlc, setOhlc] = useState([]);
    const [time, setTime] = useState(0);
    const [isConnected, setIsConnected] = useState(false);
    const [socket, setSocket] = useState(null);

    useEffect(() => {
        let ws;

        const connectWebSocket = () => {
            ws = new WebSocket(ORDERBOOK_WEBSOCKET_URL);
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
                    setMidPrice(data.mid_price || 0);
                    setTime(data.time || 0);

                    if (data.OHLC) {
                        setOhlc((prev) => [
                          ...prev,
                          {
                            open: data.OHLC.open,
                            high: data.OHLC.high,
                            low: data.OHLC.low,
                            close: data.OHLC.close,
                            time: data.time
                          },
                        ]);
                      }

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
        <WebSocketContext.Provider value={{ bids, asks, mid_price, ohlc, time }}>
            {children}
        </WebSocketContext.Provider>
    );
};

export default WebSocketProvider;
