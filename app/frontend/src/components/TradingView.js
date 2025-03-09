import React, { useEffect, useRef } from "react";

const TradingView = () => {
    const chartContainer = useRef(null);

    useEffect(() => {
        const script = document.createElement("script");
        script.src = "https://s3.tradingview.com/tv.js";
        script.async = true;
        script.onload = () => {
            new window.TradingView.widget({
                container_id: "tradingview_chart",
                symbol: "BINANCE:BTCUSDT",
                interval: "1",
                theme: "dark",
                style: "1",
                locale: "en",
                autosize: true,
            });
        };

        if (chartContainer.current) {
            chartContainer.current.appendChild(script);
        }
    }, []);

    return <div id="tradingview_chart" ref={chartContainer} style={{ height: "500px", width: "100%" }} />;
};

export default TradingView;
