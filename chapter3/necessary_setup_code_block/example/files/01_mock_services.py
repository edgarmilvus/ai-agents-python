import json
import os
import time
from typing import List, Dict, Any, Optional

# Mocking SQLAlchemy and ORM setup
# Note: In a real application, this would connect to PostgreSQL or MySQL.
# We use in-memory SQLite for simplicity.
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base

# --- 1. Database Setup (For Exercise 3) ---
Base = declarative_base()

class InventoryItem(Base):
    """SQLAlchemy Model representing an item in inventory."""
    __tablename__ = 'inventory'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "quantity": self.quantity
        }

# Initialize engine and session
engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def seed_database(session):
    """Populates the database with initial data."""
    items = [
        InventoryItem(name="Laptop Pro X", category="Electronics", price=1899.99, quantity=15),
        InventoryItem(name="Mechanical Keyboard", category="Peripherals", price=129.50, quantity=45),
        InventoryItem(name="4K Monitor 32'", category="Electronics", price=750.00, quantity=8),
        InventoryItem(name="Ergonomic Mouse", category="Peripherals", price=45.99, quantity=120),
        InventoryItem(name="USB-C Hub", category="Accessories", price=35.00, quantity=200),
    ]
    session.add_all(items)
    session.commit()

# --- 2. Mock API Client (For Exercise 2 and 4) ---
class MockFinancialAPI:
    """Simulates an external API for fetching stock prices and service health."""
    
    STOCK_DATA = {
        "GOOGL": {"price": 155.20, "last_updated": int(time.time())},
        "TSLA": {"price": 185.55, "last_updated": int(time.time())},
        "MSFT": {"price": 420.00, "last_updated": int(time.time())},
    }
    
    SERVICE_HEALTH = {
        "deployment_api": "OK",
        "log_aggregator": "DEGRADED",
        "auth_service": "OK"
    }

    @staticmethod
    def fetch_stock_price(ticker: str) -> Dict[str, Any]:
        """Fetches the current price for a given stock ticker."""
        ticker = ticker.upper()
        if ticker in MockFinancialAPI.STOCK_DATA:
            return {
                "status": "success",
                "ticker": ticker,
                "data": MockFinancialAPI.STOCK_DATA[ticker]
            }
        else:
            return {
                "status": "error",
                "message": f"Ticker '{ticker}' not found or unsupported."
            }

    @staticmethod
    def get_service_status(service_name: str) -> str:
        """Checks the health status of a specific internal service."""
        service_name = service_name.lower()
        return MockFinancialAPI.SERVICE_HEALTH.get(service_name, "UNKNOWN")

# --- 3. Mock File System (For Exercise 1 and 4) ---
CONFIG_FILE_PATH = "agent_config.json"
LOG_FILE_PATH = "deployment_logs.txt"

def initialize_mock_files():
    """Creates initial mock files for the agent to interact with."""
    if not os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, 'w') as f:
            json.dump({"agent_name": "ToolMaster", "version": 1.0, "max_retries": 5}, f, indent=4)
    
    if not os.path.exists(LOG_FILE_PATH):
        log_content = (
            "INFO: 2024-08-01 10:00:00 - Deployment started.\n"
            "INFO: 2024-08-01 10:01:15 - Service A initialized.\n"
            "ERROR: 2024-08-01 10:02:40 - Database connection failure on node 3.\n"
            "INFO: 2024-08-01 10:05:00 - Service B deployed successfully.\n"
            "WARNING: 2024-08-01 10:06:10 - High latency detected in auth service.\n"
            "ERROR: 2024-08-01 10:07:05 - Critical exception in worker process 7: Memory limit exceeded.\n"
        )
        with open(LOG_FILE_PATH, 'w') as f:
            f.write(log_content)

# Setup initialization
initialize_mock_files()
db_session = Session()
seed_database(db_session)
db_session.close()

# Note: In a full agent implementation, these functions would be wrapped 
# and registered with the LLM framework (e.g., using Pydantic for schema definition).
