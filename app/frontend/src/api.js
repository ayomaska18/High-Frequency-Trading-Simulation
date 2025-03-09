import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

export const fetchOrderBook = async () => {
    console.log("fetching orderbook...");
    try {
        const response = await axios.get(`${API_URL}/orderbook`);
        return response.data;
    } catch (error) {
        console.error("Error fetching order book:", error);
        return { bids: [], asks: [] };
    }
};
