import React, { useState, useEffect } from "react";
import axios from "axios";

const API_URL = "http://127.0.0.1:8000/trader";

const TraderControls = () => {
    const [traders, setTraders] = useState([]);
    const [bullCount, setBullCount] = useState(0);
    const [bearCount, setBearCount] = useState(0);
    const [marketMakerCount, setMarketMakerCount] = useState(0);
    const [noiseTraderCount, setNoiseTraderCount] = useState(0);
    const [realTrader, setReadTrader] = useState(null);
    const [traderCounters, setTraderCounters] = useState({
        bull: 0,
        bear: 0,
        mm: 0,
        noise: 0,
    });

    const fetchTraders = async () => {
        try {
            const response = await axios.get(API_URL);
            setTraders(response.data);
        } catch (error) {
            console.error("Error fetching traders:", error);
        }
    };

    const addTrader = async (type, is_bot) => {
        try {
            const newCounter = traderCounters[type] + 1;
            const traderName = `trader_${type}_${newCounter}`;

            // Send the POST request to add the trader
            await axios.post(API_URL, {
                name: traderName,
                trader_type: type,
                balance: 1000.0,
                is_bot: is_bot,
            });

            // Update the counter in the state
            setTraderCounters((prevCounters) => ({
                ...prevCounters,
                [type]: newCounter,
            }));

            // Fetch the updated list of traders
            fetchTraders();
        } catch (error) {
            console.error("Error adding trader:", error);
        }
    };

    const removeTrader = async (type) => {
        try {
            await axios.delete(`${API_URL}/${type}`);
            fetchTraders();
        } catch (error) {
            console.error("Error removing trader:", error);
        }
    };

    // const createRealTrader = async () => {
    //     try {
    //         const response = await axios.post(`${API_URL}/real`, {
    //             name: "client",
    //             trader_type: "client",
    //             balance: 1000.0,
    //             is_bot: false,
    //         });
    //         console.log("Real trader created:", response.data);
    //     } catch (error) {
    //         console.error("Error creating real trader:", error);
    //     }
    // };

    useEffect(() => {
        fetchTraders();
        // createRealTrader();
    }, []);

    useEffect(() => {
        const bullCount = traders.filter(t => t.trader_type === "bull").length;
        const bearCount = traders.filter(t => t.trader_type === "bear").length;
        const marketMakerCount = traders.filter(t => t.trader_type === "mm").length;
        const noiseTraderCount = traders.filter(t => t.trader_type === "noise").length;
        // const realTrader = traders.find(t => t.trader_type === "client");

        setBullCount(bullCount);
        setBearCount(bearCount);
        setMarketMakerCount(marketMakerCount);
        setNoiseTraderCount(noiseTraderCount);
    }, [traders]);

    return (
        <div className="trader-controls">
            <h2>Trader Controls</h2>
            <div className="control-group">
                <button onClick={() => addTrader("bull", true)}>Add BullTrader</button>
                <button onClick={() => removeTrader("bull")}>Remove BullTrader</button>
                <span>BullTraders: {bullCount}</span>
            </div>
            <div className="control-group">
                <button onClick={() => addTrader("bear", true)}>Add BearTrader</button>
                <button onClick={() => removeTrader("bear")}>Remove BearTrader</button>
                <span>BearTraders: {bearCount}</span>
            </div>
            <div className="control-group">
                <button onClick={() => addTrader("mm", true)}>Add MarketMaker</button>
                <button onClick={() => removeTrader("mm")}>Remove MarketMaker</button>
                <span>MarketMakers: {marketMakerCount}</span>
            </div>
            <div className="control-group">
                <button onClick={() => addTrader("noise", true)}>Add NoiseTrader</button>
                <button onClick={() => removeTrader("noise")}>Remove NoiseTrader</button>
                <span>NoiseTraders: {noiseTraderCount}</span>
            </div>
        </div>
    );
};

export default TraderControls;