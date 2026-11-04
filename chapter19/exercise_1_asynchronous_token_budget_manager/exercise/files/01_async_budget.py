import asyncio
import time
from typing import Dict, Any, List
from pydantic import BaseModel, ValidationError
import json
import tiktoken

# --- Setup for Token Counting (Used in Exercises 2 and 4) ---
TOKEN_ENCODER = tiktoken.get_encoding("cl100k_base")

def calculate_tokens(text: str) -> int:
    """Calculates the token count for a given string."""
    return len(TOKEN_ENCODER.encode(text))

# =============================================================
# Exercise 1 Solution
# =============================================================

class TokenBudgetExceededError(Exception):
    """Raised when the cumulative token usage exceeds the budget."""
    pass

class AsyncTokenBudgetManager:
    """
    An asynchronous context manager that enforces a maximum token budget 
    across multiple sequential LLM calls.
    """
    def __init__(self, max_tokens: int):
        self.max_tokens = max_tokens
        self.current_usage = 0
        print(f"Manager initialized with budget: {max_tokens} tokens.")

    async def __aenter__(self):
        """Initializes the context, resetting usage."""
        self.current_usage = 0
        return self

    async def mock_llm_call(self, prompt: str, tokens_used: int):
        """Simulates an LLM API call, tracks usage, and enforces the budget."""
        # 1. Simulate network latency
        await asyncio.sleep(0.1)
        
        new_usage = self.current_usage + tokens_used
        
        # 2. Budget Enforcement: Check BEFORE committing the usage
        if new_usage > self.max_tokens:
            raise TokenBudgetExceededError(
                f"Call for '{prompt[:20]}...' used {tokens_used} tokens. "
                f"Total usage ({new_usage}) exceeds budget ({self.max_tokens})."
            )
        
        # Commit usage if safe
        self.current_usage = new_usage
        print(f"  [LLM Call] Prompt: '{prompt[:20]}...', Tokens used: {tokens_used}. Current Total: {self.current_usage}")
        
        return f"Response to {prompt[:10]}"

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Handles context exit and cleans up resources."""
        if exc_type is TokenBudgetExceededError:
            print(f"\n[ERROR] Budget breach detected! Final usage: {self.current_usage}. Cleaning up resources.")
            # Returning False ensures the exception is propagated outside the context block
            return False 
        
        print(f"\n[SUCCESS] Context finished. Final token usage: {self.current_usage} (Budget: {self.max_tokens}).")
        return True # Suppress other exceptions, allow normal exit

async def run_exercise_1():
    print("--- Running Exercise 1: Token Budget Manager (Success Case) ---")
    try:
        async with AsyncTokenBudgetManager(max_tokens=100) as manager:
            # Call 1: Safe (30 tokens)
            await manager.mock_llm_call("Analyze market trends for Q3.", 30)
            # Call 2: Safe (45 tokens)
            await manager.mock_llm_call("Draft executive summary.", 45)
            # Total usage: 75/100
            
    except TokenBudgetExceededError as e:
        print(f"Caught unexpected error: {e}")

    print("\n--- Running Exercise 1: Token Budget Manager (Failure Case) ---")
    try:
        async with AsyncTokenBudgetManager(max_tokens=100) as manager:
            # Call 1: Safe (50 tokens)
            await manager.mock_llm_call("Analyze market trends for Q3.", 50)
            # Call 2: This call pushes the total to 105 (50 + 55), triggering the exception
            await manager.mock_llm_call("Draft detailed financial model.", 55)
            # This line should not be reached
            
    except TokenBudgetExceededError as e:
        print(f"Caught expected error: {e}")

asyncio.run(run_exercise_1())
