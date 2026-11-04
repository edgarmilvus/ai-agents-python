import asyncio
import random
from typing import Dict, Any, List

# 1. Asynchronous Context Manager
class AsyncFinancialAPI:
    """Simulates a safe, asynchronous connection to a financial data API."""
    def __init__(self, name="Financial_Tool"):
        self.name = name

    async def __aenter__(self):
        print(f"[{self.name}] Establishing secure connection...")
        await asyncio.sleep(0.1)
        print(f"[{self.name}] Connection established.")
        # Return the object itself, which contains the fetch_quote method
        return self

    async def fetch_quote(self, symbol: str) -> Dict[str, Any]:
        """Mock method to fetch data."""
        await asyncio.sleep(random.uniform(0.5, 1.5))
        price = round(random.uniform(100.0, 2000.0), 2)
        return {"symbol": symbol, "price": price, "source": self.name}

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print(f"[{self.name}] Connection closed due to exception: {exc_val}")
        else:
            print(f"[{self.name}] Connection safely closed.")
        await asyncio.sleep(0.1)

# 2. Worker Specialization
class DataFetcherAgent:
    """Requires the AsyncFinancialAPI tool and uses async with."""
    def __init__(self, agent_id: int):
        self.id = agent_id
        self.specialization = "DataFetcherAgent"

    async def execute_task(self, task_data: Dict[str, Any], api_tool: AsyncFinancialAPI) -> Dict[str, Any]:
        task_name = task_data.get('task_name', 'Fetch Data')
        symbol = task_data.get('symbol', 'MSFT')
        
        print(f"Worker {self.id} ({self.specialization}) starting: {task_name} for {symbol}")
        
        # Execution Flow: Use Asynchronous Context Manager
        async with api_tool as api:
            # api is the object returned by __aenter__
            result = await api.fetch_quote(symbol)
            details = f"Fetched data for {symbol}: ${result['price']}"
        
        print(f"Worker {self.id} finished: {task_name}")
        return {
            'worker_id': self.id,
            'task': task_name,
            'status': 'Completed',
            'details': details
        }

class CalculationAgent:
    """Performs calculations, does not require the API."""
    def __init__(self, agent_id: int):
        self.id = agent_id
        self.specialization = "CalculationAgent"

    async def execute_task(self, task_data: Dict[str, Any], api_tool=None) -> Dict[str, Any]:
        task_name = task_data.get('task_name', 'Calculate')
        duration = task_data.get('duration', 3)
        symbol = task_data.get('symbol', 'GOOG')

        print(f"Worker {self.id} ({self.specialization}) starting: {task_name} on {symbol} (Duration: {duration}s)")
        
        await asyncio.sleep(duration)
        
        details = f"Complex calculation (RSI) completed successfully for {symbol}."
        print(f"Worker {self.id} finished: {task_name}")
        
        return {
            'worker_id': self.id,
            'task': task_name,
            'status': 'Completed',
            'details': details
        }

# 3. Manager Allocation
class ResourceAllocationManager:
    def __init__(self):
        self.data_fetcher = DataFetcherAgent(agent_id=101)
        self.calculator = CalculationAgent(agent_id=102)
        self.financial_api = AsyncFinancialAPI()

    async def run_allocation(self, tasks: List[Dict[str, Any]]):
        
        coros = []
        for task in tasks:
            task_type = task["type"]
            
            # 4. Allocation Logic
            if task_type == "fetch_data":
                print(f"[MANAGER] Allocating FETCH task ({task['symbol']}) to DataFetcherAgent.")
                coros.append(self.data_fetcher.execute_task(
                    task_data=task,
                    api_tool=self.financial_api # Pass the context manager instance
                ))
            
            elif task_type == "calculate_RSI":
                print(f"[MANAGER] Allocating CALCULATION task ({task['symbol']}) to CalculationAgent.")
                coros.append(self.calculator.execute_task(
                    task_data=task,
                    api_tool=None 
                ))
            else:
                print(f"[MANAGER] Unknown task type: {task_type}")

        results = await asyncio.gather(*coros)
        return results

async def main_exercise_2():
    manager = ResourceAllocationManager()
    
    tasks = [
        {"type": "fetch_data", "task_name": "Real-Time Quote", "symbol": "GOOG"},
        {"type": "calculate_RSI", "task_name": "RSI Calculation", "symbol": "GOOG", "duration": 2.5},
        {"type": "fetch_data", "task_name": "Real-Time Quote", "symbol": "TSLA"},
    ]
    
    print("--- Starting Exercise 2: Specialized Allocation and Context Management ---")
    results = await manager.run_allocation(tasks)
    
    print("\n[FINAL RESULTS SUMMARY]")
    for result in results:
        print(f"- {result['task']} by W{result['worker_id']}: {result['details']}")

if __name__ == "__main__":
    asyncio.run(main_exercise_2())
