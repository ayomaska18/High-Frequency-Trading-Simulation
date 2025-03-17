import React, { useEffect, useRef, useState, useContext } from "react";
import { AreaSeries, createChart } from 'lightweight-charts';
import { WebSocketContext } from "./WebSocketContext";

const TradingChart = () => {
    const chartContainerRef = useRef(null);
    const [chart, setChart] = useState(null);
    const [series, setSeries] = useState(null);
    const [socket, setSocket] = useState(null);
    const { midPrice } = useContext(WebSocketContext);

    useEffect(() => {
        if (!chartContainerRef.current) return;

        const chartOptions = {
            width: 1190,
            height: 522,
            layout: { backgroundColor: "#000", textColor: "#black" },
            grid: { vertLines: { color: "#333" }, horzLines: { color: "#333" } },
        }
        const newChart = createChart(chartContainerRef.current, chartOptions);

        const newSeries = newChart.addSeries(AreaSeries, { color: "#007bff" });

        setChart(newChart);
        setSeries(newSeries);

        return () => newChart.remove();
    }, []);

    useEffect(() => {
        if (series && midPrice) {
            series.update({
                time: Math.floor(Date.now() / 1000),
                value: midPrice,
            });
        }
    }, [midPrice]);

    return (
        <div className="chart-container" ref={chartContainerRef} />
    );
    
};

export default TradingChart;
