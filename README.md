# High-Frequency-Trading-Simulation

This project implements a high-performance, asynchronous trading engine designed to simulate market trading with various automated trader types. The engine features an order book with market and limit order matching, a range of trader strategies, real-time data streaming via websockets, and persistent storage with PostgreSQL and InfluxDB.

## Features

- **Order Book & Matching Engine:**  
  Implements an order book that supports both market and limit order matching. Orders are organized in a binary tree structure for efficient best bid/ask retrieval and matching 
- **Automated Traders:**  
  Multiple trader types such as BullTrader, BearTrader, MarketMaker, and NoiseTrader simulate different trading strategies. Traders place market and limit orders based on market conditions

- **Real-Time Data & Websockets:**  
  Provides real-time order book snapshots and order fill notifications through websockets. Market data is also streamed and stored in InfluxDB for analysis

- **Database Integration:**  
  Uses SQLAlchemy with asynchronous PostgreSQL support to manage persistent data storage for traders and orders
  
- **Configuration & Environment Management:**  
  Configuration is handled via Pydantic settings with support for environment variables, allowing flexible deployment setups

## Architecture Overview

- **Core Components:**  
  - **Order Book:** Maintains the current state of buy and sell orders using a limit tree structure for efficient matching 
  - **Trader Manager:** Manages a collection of trader instances, orchestrates trading tasks, and handles dynamic trader addition/removal 
  - **API & Websocket Endpoints:** Exposes RESTful APIs and websockets for interacting with the trading engine, including endpoints for order management, trader registration, and real-time order book updates 

- **Data Storage:**  
  - **PostgreSQL:** Used for persisting traders and orders through SQLAlchemy’s asynchronous engine.
  - **InfluxDB:** Stores market data snapshots for time-series analysis.

## Setup & Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/trading-engine.git
   cd trading-engine
   ```

2. **Create & Activate a Virtual Environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**

   Create a `.env` file in the project root with the following (adjust values as needed):

   ```env
   # PostgreSQL configuration
   POSTGRES_USER=your_pg_user
   POSTGRES_PASSWORD=your_pg_password
   POSTGRES_DB=your_database_name
   DATABASE_HOSTNAME=localhost
   DATABASE_PORT=5432

   # InfluxDB configuration
   INFLUXDB_MODE=setup
   INFLUXDB_URL=http://localhost:8086
   INFLUXDB_USERNAME=your_influx_username
   INFLUXDB_PASSWORD=your_influx_password
   INFLUXDB_ORG=your_influx_org
   INFLUXDB_BUCKET=your_influx_bucket
   INFLUXDB_ADMIN_TOKEN=your_influx_token

   # API Keys
   COINAPI_API_KEY=your_coinapi_key

   # PG Admin
   PGADMIN_DEFAULT_EMAIL=your_pgadmin_email
   PGADMIN_DEFAULT_PASSWORD=your_pg_default_password
   
   ```

5. **Database Initialization:**

   The database is automatically initialized during application startup. Ensure that your PostgreSQL server is running and accessible.

## Running the Application

Start the application with an ASGI server such as Uvicorn:

```bash
docker-compose up --build
```

The application will:
- Initialize the database and populate initial traders.
- Start background tasks to simulate trader activity.
- Expose REST API endpoints and websockets for real-time updates.

## Project Structure

Project Structure
The following is the desired directory layout for the project:

bash
fyp/
├── app/
│   ├── backend/          # Backend API (FastAPI)
│   │   ├── src/
│   │   │   ├── routers/  # API routes
│   │   │   ├── models/   # Database models
│   │   │   ├── trader_manager.py
│   │   │   ├── orderbook.py
│   │   │   └── main.py
│   ├── frontend/         # Frontend application (React)
├── docker-compose.yaml   # Docker Compose configuration
├── Dockerfile            # Backend Dockerfile
├── .env.example          # Environment variable template
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
