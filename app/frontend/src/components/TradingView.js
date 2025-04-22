import React, { useEffect, useRef, useState, useContext } from "react";
import { AreaSeries, createChart, CandlestickSeries } from 'lightweight-charts';
import { WebSocketContext } from "./WebSocketContext";

const TradingChart = () => {
    const chartContainerRef = useRef(null);
    const [chart, setChart] = useState(null);
    const [series, setSeries] = useState(null);
    const [socket, setSocket] = useState(null);
    const {ohlc} = useContext(WebSocketContext);

    useEffect(() => {
        if (!chartContainerRef.current) return;

        const chartOptions = {
            width: 800,
            height: 522,
            layout: { background: {type:'solid', color:'black'}, textColor: 'white' },
            grid: { vertLines: { color: "#333" }, horzLines: { color: "#333" } },
        };
        const newChart = createChart(chartContainerRef.current, chartOptions);
        const newSeries = newChart.addSeries(CandlestickSeries, {
            upColor: "#26a69a",
            downColor: "#ef5350",
            borderVisible: false,
            wickUpColor: "#26a69a",
            wickDownColor: "#ef5350",
          });
        setChart(newChart);
        setSeries(newSeries);

        return () => newChart.remove();
    }, []);

    useEffect(() => {
        if (series && ohlc && Array.isArray(ohlc)) {
            const formattedData = ohlc.map(candle => ({
                open: candle.open,
                high: candle.high,
                low: candle.low,
                close: candle.close,
                time: Math.floor(candle.time / 60) * 60
            }));
            const sortedData = formattedData.sort((a, b) => a.time - b.time);
            series.setData(sortedData);
        }
    }, [ohlc, series]);

    return (
        <div className="chart-container" ref={chartContainerRef} />
    );
    
};

export default TradingChart;
