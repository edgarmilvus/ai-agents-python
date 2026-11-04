import asyncio
import time
from fastapi import FastAPI
from typing import Dict, Any
import uvicorn

# 1. Initialize the FastAPI application
# We use a descriptive title for documentation purposes (Swagger/OpenAPI UI)
app = FastAPI(
    title="Agent Deployment Wrapper: Sync vs. Async",
    description="Demonstrates how FastAPI handles quick (sync) vs. long (async) agent tasks."
)

# --- SIMULATED AGENT CORE FUNCTIONS ---

def synchronous_quick_check(ticker: str) -> str:
    """
    Simulates a quick, synchronous agent check (e.g., input validation of a stock ticker).
    This function will block the executing thread until completion.
    """
    start_time = time.time()
    # Simulate a very fast, CPU-bound operation
    if not ticker.isalpha() or len(ticker) > 5:
        result = f"Error: Invalid ticker format for {ticker}."
    else:
        result = f"Validation successful. Ticker '{ticker}' is ready for analysis."
    
    end_time = time.time()
    print(f"[SERVER LOG] Sync Check executed in: {end_time - start_time:.4f}s")
    return result

async def asynchronous_long_task(ticker: str) -> str:
    """
    Simulates a long-running, asynchronous agent task (e.g., Monte Carlo simulation).
    The 'await' keyword allows the Event Loop to handle other requests while waiting.
    """
    start_time = time.time()
    print(f"[SERVER LOG] Starting long task for ticker: {ticker}")
    
    # Simulate a 5-second I/O bound wait (e.g., waiting for external LLM response or DB query)
    await asyncio.sleep(5)
    
    # Final processing after the wait
    result = f"Agent completed 5-year Monte Carlo simulation for '{ticker}'."
    
    end_time = time.time()
    print(f"[SERVER LOG] Async Task executed in: {end_time - start_time:.4f}s")
    return result

# --- API ENDPOINTS DEFINITION ---

@app.get("/quick_check/{ticker}")
def quick_endpoint(ticker: str) -> Dict[str, Any]:
    """
    Endpoint for fast, synchronous requests. Runs in FastAPI's internal thread pool.
    If many of these run simultaneously, they can still exhaust the pool.
    """
    # 1. Call the synchronous core function
    agent_response = synchronous_quick_check(ticker.upper())
    
    # 2. Return the structured JSON response
    return {"status": "ok", "message": agent_response, "task_type": "quick_sync"}

@app.post("/run_complex_agent/")
async def complex_endpoint(ticker: str) -> Dict[str, Any]:
    """
    Endpoint for long-running, asynchronous tasks. Defined using 'async def'.
    Crucially, this uses 'await' to yield control during I/O waits.
    """
    # Note: In a production system, this is where we would typically enqueue the task
    # using RQ or Celery, and return an immediate 'status: pending' response.
    
    # 1. Call the asynchronous core function using 'await'
    agent_response = await asynchronous_long_task(ticker.upper())
    
    # 2. Return the structured JSON response
    return {"status": "processing_complete", "result": agent_response, "task_type": "long_async"}

# --- SERVER EXECUTION BLOCK ---
if __name__ == "__main__":
    # This block allows the script to be run directly for demonstration.
    print("---------------------------------------------------------------------")
    print("FastAPI server starting on http://127.0.0.1:8000")
    print("Test URLs:")
    print("1. Sync Test (Fast): http://127.0.0.1:8000/quick_check/MSFT")
    print("2. Async Test (Slow, POST only):")
    print("   curl -X POST 'http://127.0.0.1:8000/run_complex_agent/?ticker=GOOG'")
    print("---------------------------------------------------------------------")
    
    # uvicorn is the ASGI server that runs the FastAPI application
    uvicorn.run(app, host="0.0.0.0", port=8000)
