class AsyncFinancialAPI:
    async def __aenter__(self):
        # Setup logic
        return self
    
    async def fetch_quote(self, symbol):
        # Mock API call
        return {"symbol": symbol, "price": 1500.00}

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Cleanup logic
        pass
