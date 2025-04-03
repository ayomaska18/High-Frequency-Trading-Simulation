from influxdb_client import Point
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from influxdb_client.client.write_api import ASYNCHRONOUS
import os
from dotenv import load_dotenv
import asyncio
import aiohttp

load_dotenv()

INFLUXDB_URL = os.getenv("INFLUXDB_URL")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_ADMIN_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")                  
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")  

async def write_to_influxdb(timestamp: str, ohlc: dict, currency: str):
    async with InfluxDBClientAsync(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG) as client:
        
        write_api = client.write_api()
        
        point = (
            Point("ohlc")
            .tag("currency", currency)
            .field("open", ohlc.get("open"))
            .field("high", ohlc.get("high"))
            .field("low", ohlc.get("low"))
            .field("close", ohlc.get("close"))
            .time(timestamp)
        )
        
        await write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
