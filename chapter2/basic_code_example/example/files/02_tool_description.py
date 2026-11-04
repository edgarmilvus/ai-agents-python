from langchain_core.tools import tool

# GOOD DOCSTRING: Explicitly states the purpose and conditions for use
@tool
def get_current_stock_price(ticker: str) -> str:
    """
    Retrieves the real-time closing price for a given stock ticker (e.g., 'GOOG', 'AAPL').
    This tool MUST be used for any question involving current financial data or prices.
    Do not guess the price; delegate to this tool.
    """
    # A real implementation would call a market-data API here.
    return f"{ticker.upper()}: price lookup is not wired to a provider in this example."
