import React, { useState, useEffect } from "react";
import axios from "axios";

const ORDER_API = "http://127.0.0.1:8000/order";
const TRADER_API = "http://127.0.0.1:8000/trader";
const HOLDING_API = "http://127.0.0.1:8000/holding";

const TraderPanel = ({ setRealTraderId }) => {
    const [realTraderIdLocal, setRealTraderIdLocal] = useState(null);
    const [orderType, setOrderType] = useState("limit");
    const [isBuy, setIsBuy] = useState(true);
    const [price, setPrice] = useState("");
    const [volume, setVolume] = useState("");
    const [cancelId, setCancelId] = useState("");
    const [activeTab, setActiveTab] = useState("history");
    const [orderHistory, setOrderHistory] = useState([]);
    const [currentHoldings, setCurrentHoldings] = useState([]);

    
    const createRealTrader = async () => {
        try {

            const response = await axios.post(TRADER_API, {
                name: "client",
                trader_type: "client",
                balance: 1000.0,
                is_bot: false,
            });
            console.log("Real trader created:", response.data);

            setRealTraderIdLocal(response.data.trader_id);
            setRealTraderId(response.data.trader_id);
            console.log("Trader ID set:", response.data.trader_id);
        } catch (error) {
            console.error("Error creating real trader:", error);
        }
    };

    const fetchOrders = async () => {
        try {
            const response = await axios.get(`${ORDER_API}/${realTraderIdLocal}`);
            setOrderHistory(response.data);
        } catch (error) {
            console.error("Error fetching orders:", error);
        }
    };

    const fetchHoldings = async () => {
        try {
            const response = await axios.get(`${HOLDING_API}/${realTraderIdLocal}`);
            setCurrentHoldings(response.data);
        } catch (error) {
            console.error("Error fetching order history:", error);
        }
    };

    const submitOrder = async () => {
        try {
            const payload = {
                trader_id: realTraderIdLocal,
                asset: "BTC",
                is_buy: isBuy,
                price: parseFloat(price),
                order_type: orderType,
                volume: parseFloat(volume),
                timestamp: Math.floor(Date.now() / 1000),
            };

            const response = await axios.post(ORDER_API, payload);
            console.log("Order response:", response.data);

            fetchOrders();
            fetchHoldings();
        } catch (error) {
            console.error("Error submitting order:", error);
        }
    };

    const cancelOrder = async () => {
        try {
            const response = await axios.delete(`${ORDER_API}/${cancelId}`);
            console.log("Cancel response:", response.data);

            fetchOrders();
            fetchHoldings();
        } catch (error) {
            console.error("Error cancelling order:", error);
        }
    };

    useEffect(() => {
        createRealTrader();
    }, []);
    
    useEffect(() => {
        if (realTraderIdLocal) {
            fetchOrders();
            fetchHoldings();
        }
    }, [realTraderIdLocal]);

    return (
        <div className="trader-panel-container">
            {/* Left Panel: Submit Order */}
            <div className="submit-order-panel">
                <h2>Submit Order</h2>

                <div className="form-group">
                    <label>Order Type:</label>
                    <select value={orderType} onChange={(e) => setOrderType(e.target.value)}>
                        <option value="limit">Limit</option>
                        <option value="market">Market</option>
                    </select>
                </div>

                <div className="form-group">
                    <label>Side:</label>
                    <select value={isBuy} onChange={(e) => setIsBuy(e.target.value === "true")}>
                        <option value="true">Buy</option>
                        <option value="false">Sell</option>
                    </select>
                </div>

                {orderType === "limit" && (
                    <div className="form-group">
                        <label>Price:</label>
                        <input type="number" value={price} onChange={(e) => setPrice(e.target.value)} />
                    </div>
                )}

                <div className="form-group">
                    <label>Volume:</label>
                    <input type="number" value={volume} onChange={(e) => setVolume(e.target.value)} />
                </div>

                <button className="submit-button" onClick={submitOrder}>Submit Order</button>
            </div>

            {/* Right Panel: Order History and Current Holdings */}
            <div className="order-info-panel">
                <div className="tabs">
                    <button
                        className={activeTab === "history" ? "active" : ""}
                        onClick={() => setActiveTab("history")}
                    >
                        Order History
                    </button>
                    <button
                        className={activeTab === "holdings" ? "active" : ""}
                        onClick={() => setActiveTab("holdings")}
                    >
                        Current Holdings
                    </button>
                </div>

                <div className="tab-content">
                    {activeTab === "history" && (
                        <div className="order-history">
                            <h3>Order History</h3>
                            <table className="order-table">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Type</th>
                                        <th>Side</th>
                                        <th>Volume</th>
                                        <th>Price</th>
                                        <th>Timestamp</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {orderHistory.map((order) => (
                                        <tr key={order.id}>
                                            <td>{order.id}</td>
                                            <td>{order.order_type.toUpperCase()}</td>
                                            <td>{order.is_buy ? "Buy" : "Sell"}</td>
                                            <td>{order.volume.toFixed(4)}</td>
                                            <td>{order.price.toFixed(2)}</td>
                                            <td>{new Date(order.timestamp).toLocaleString()}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}

                    {activeTab === "holdings" && (
                        <div className="current-holdings">
                            <h3>Current Holdings</h3>
                            <table className="holdings-table">
                                <thead>
                                    <tr>
                                        <th>Asset</th>
                                        <th>Amount</th>
                                        <th>Avg Price</th>
                                        <th>Last Updated</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {currentHoldings.map((holding, index) => (
                                        <tr key={index}>
                                            <td>{holding.asset}</td>
                                            <td>{holding.amount.toFixed(4)}</td>
                                            <td>{holding.avg_price.toFixed(2)}</td>
                                            <td>{new Date(holding.updated_at).toLocaleString()}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default TraderPanel;
