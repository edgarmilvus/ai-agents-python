import time
from typing import Dict, Any

# Assume MockFinancialAPI is defined from the setup

def get_stock_price(ticker_symbol: str) -> str:
    """
    Fetches the real-time stock price for a single, specified ticker symbol 
    (e.g., "GOOGL", "MSFT") using the external financial API.
    """
    ticker = ticker_symbol.upper()
    result = MockFinancialAPI.fetch_stock_price(ticker)
    
    # 1. Error Handling based on API response structure
    if result.get("status") == "error":
        return f"API ERROR: Could not retrieve price for {ticker}. Message: {result['message']}"
    
    # 2. Success Formatting
    data = result.get("data", {})
    price = data.get("price")
    
    # Convert timestamp for better readability
    updated = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data.get("last_updated")))
    
    return f"The current price for {ticker} is ${price:.2f}, last updated at {updated}."

# --- Complex Reasoning Challenge Strategy ---
# Query: "Which stock is currently more expensive, TSLA or MSFT? Also, what happens if I ask about the price of APPL?"
#
# Agent Execution Sequence (Simulated):
# 1. Tool Call: get_stock_price(ticker_symbol="TSLA")
#    Output: "The current price for TSLA is $185.55, last updated at..."
# 2. Tool Call: get_stock_price(ticker_symbol="MSFT")
#    Output: "The current price for MSFT is $420.00, last updated at..."
# 3. Tool Call: get_stock_price(ticker_symbol="APPL")
#    Output: "API ERROR: Could not retrieve price for APPL. Message: Ticker 'APPL' not found or unsupported."
#
# LLM Synthesis:
# "Based on the data, MSFT ($420.00) is currently more expensive than TSLA ($185.55). 
# When querying the price for APPL, the financial API returned an error stating that the 
# ticker 'APPL' was not found or is unsupported."
