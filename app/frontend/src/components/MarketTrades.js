import React, { useEffect, useState } from "react";

const ORDER_WEBSOCKET_URL = "ws://127.0.0.1:8000/order/ws";

const MarketTrades = ({traderId}) => {
    const [trades, setTrades] = useState([]);

    useEffect(() => {
        if (!traderId){
            console.log('no trader id provided')
            return;
        }
            
        
        const ws = new WebSocket(`${ORDER_WEBSOCKET_URL}/${traderId}`);

        ws.onopen = () => {
            console.log("WebSocket connected to MarketTrades");
        };

        ws.onmessage = (event) => {
            try {
                const newTrade = {
                    ...JSON.parse(event.data),
                    timestamp: Date.now() 
                };

                console.log(newTrade);

                setTrades((prevTrades) => [newTrade, ...prevTrades].slice(0, 20));
            } catch (error) {
                console.error("Error parsing WebSocket message:", error);
            }
        };

        ws.onclose = () => {
            console.log("WebSocket disconnected from MarketTrades");
        };

        return () => {
            ws.close();
        };
    }, [traderId]);

    return (
        <div className="market-trades-container">
            <h3>Market Trades</h3>
            <div className="trade header">
                <span className="trade-price"><strong>Price(USDT)</strong></span>
                <span className="trade-volume"><strong>Amount(BTC)</strong></span>
                <span className="trade-time"><strong>Time</strong></span>
            </div>
            <div className="trades-list">
            {trades.map((trade, index) => (
                <div key={index} className={`trade ${trade.is_buy ? "buy" : "sell"}`}>
                    <span className="trade-price">{Number(trade.price).toFixed(2)}</span>
                    <span className="trade-volume">{Number(trade.volume).toFixed(4)}</span>
                    <span className="trade-time">
                        {new Date(trade.timestamp).toLocaleTimeString("en-GB", {
                            hour: "2-digit",
                            minute: "2-digit",
                            second: "2-digit"
                        })}
                    </span>
                </div>
            ))}
            </div>
        </div>
    );
};

export default MarketTrades;