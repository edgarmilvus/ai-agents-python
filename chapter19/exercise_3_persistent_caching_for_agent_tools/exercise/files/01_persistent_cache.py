import asyncio
import json
import time
from typing import Any, Dict, List

# =============================================================
# Exercise 3 Solution
# =============================================================

async def expensive_tool_core(ticker: str, period: int) -> float:
    """Simulates an expensive, non-cached API call or calculation."""
    print(f"  [Tool EXECUTION] Executing expensive calculation for {ticker} over {period} years...")
    await asyncio.sleep(1.0) # Simulate latency
    # A deterministic result: `hash()` on strings is salted per process, so it
    # would print different numbers on every run, in the book and in a test.
    seed = sum(ord(char) for char in ticker) % 100
    return round(seed + (period * 0.5), 2)

class CachedToolWrapper:
    """Wraps an asynchronous tool function to cache results based on arguments."""
    def __init__(self, tool_func):
        self.tool_func = tool_func
        self.cache: Dict[str, Any] = {}
        
    def _generate_key(self, *args, **kwargs) -> str:
        """Generates a unique, hashable key from function arguments."""
        # Use JSON serialization with sorted keys for reliable key generation
        key_data = {"args": args, "kwargs": kwargs}
        return json.dumps(key_data, sort_keys=True)

    async def __call__(self, *args, **kwargs) -> Any:
        cache_key = self._generate_key(*args, **kwargs)
        
        if cache_key in self.cache:
            # Cache Hit: Immediate return
            print(f"  [Cache HIT] Returning cached result for key: {cache_key[:30]}...")
            return self.cache[cache_key]
        else:
            # Cache Miss: Execute expensive tool
            print(f"  [Cache MISS] Key not found. Executing tool...")
            result = await self.tool_func(*args, **kwargs)
            self.cache[cache_key] = result
            print(f"  [Cache STORE] Stored result: {result}")
            return result

async def run_exercise_3():
    # Wrap the expensive tool
    cached_tool = CachedToolWrapper(expensive_tool_core)
    
    print("--- Running Exercise 3: Persistent Caching for Tools ---")
    
    start_time = time.time()
    
    # Call 1: Cache Miss (Execution required, ~1.0s)
    result_a = await cached_tool(ticker="TSLA", period=5)
    
    # Call 2: Cache Hit (Identical inputs, near instant)
    result_b = await cached_tool(ticker="TSLA", period=5)
    
    # Call 3: Cache Miss (Different inputs, ~1.0s)
    result_c = await cached_tool(ticker="AAPL", period=10)

    # Call 4: Cache Hit (Identical inputs to Call 3, near instant)
    result_d = await cached_tool(ticker="AAPL", period=10)
    
    end_time = time.time()
    
    print(f"\nResults: A={result_a}, B={result_b}, C={result_c}, D={result_d}")
    print(f"Total execution time: {end_time - start_time:.2f} seconds.")
    # Expected time should be close to 2.0 seconds (for 2 misses)

asyncio.run(run_exercise_3())
