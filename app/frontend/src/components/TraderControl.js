import React, { useState, useEffect } from "react";
import axios from "axios";

const API_URL = "http://127.0.0.1:8000/trader";

const TraderControls = () => {
    const [traders, setTraders] = useState([]);
    const [bullCount, setBullCount] = useState(0);
    const [bearCount, setBearCount] = useState(0);
    const [marketMakerCount, setMarketMakerCount] = useState(0);
    const [noiseTraderCount, setNoiseTraderCount] = useState(0);

    const fetchTraders = async () => {
        try {
            const response = await axios.get(API_URL);
            setTraders(response.data);
        } catch (error) {
            console.error("Error fetching traders:", error);
        }
    };

    const addTrader = async (type) => {
        try {
            await axios.post(API_URL, { name: type });
            fetchTraders();
        } catch (error) {
            console.error("Error adding trader:", error);
        }
    };

    const removeTrader = async (type) => {
        try {
            await axios.delete(API_URL, { data: { name: type } });
            fetchTraders();
        } catch (error) {
            console.error("Error removing trader:", error);
        }
    };

    useEffect(() => {
        fetchTraders();
    }, []);

    useEffect(() => {
        const bullCount = traders.filter(t => t.type === "BullTrader").length;
        const bearCount = traders.filter(t => t.type === "BearTrader").length;
        const marketMakerCount = traders.filter(t => t.type === "MarketMaker").length;
        const noiseTraderCount = traders.filter(t => t.type === "NoiseTrader").length;

        setBullCount(bullCount);
        setBearCount(bearCount);
        setMarketMakerCount(marketMakerCount);
        setNoiseTraderCount(noiseTraderCount);
    }, [traders]);

    return (
        <div className="trader-controls">
            <h2>Trader Controls</h2>
            <div className="control-group">
                <button onClick={() => addTrader("BullTrader")}>Add BullTrader</button>
                <button onClick={() => removeTrader("BullTrader")}>Remove BullTrader</button>
                <span>BullTraders: {bullCount}</span>
            </div>
            <div className="control-group">
                <button onClick={() => addTrader("BearTrader")}>Add BearTrader</button>
                <button onClick={() => removeTrader("BearTrader")}>Remove BearTrader</button>
                <span>BearTraders: {bearCount}</span>
            </div>
            <div className="control-group">
                <button onClick={() => addTrader("MarketMaker")}>Add MarketMaker</button>
                <button onClick={() => removeTrader("MarketMaker")}>Remove MarketMaker</button>
                <span>MarketMakers: {marketMakerCount}</span>
            </div>
            <div className="control-group">
                <button onClick={() => addTrader("NoiseTrader")}>Add NoiseTrader</button>
                <button onClick={() => removeTrader("NoiseTrader")}>Remove NoiseTrader</button>
                <span>NoiseTraders: {noiseTraderCount}</span>
            </div>
        </div>
    );
};

export default TraderControls;