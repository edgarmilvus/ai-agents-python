import asyncio
import time
from typing import Dict, Any, Tuple

# --- 1. DEFINITION OF ECONOMIC CONSTANTS ---
# Standard pricing models charge different rates for input (prompt) and output (completion).
# Rates are typically defined per 1,000,000 tokens (1 Million).
INPUT_RATE_PER_MILLION = 5.00    # Example: $5.00 per 1M input tokens (Context)
OUTPUT_RATE_PER_MILLION = 15.00   # Example: $15.00 per 1M output tokens (Generation)
TOKENS_PER_DOLLAR = 1_000_000     # Conversion factor

class AsyncLLMCostTracker:
    """
    An asynchronous wrapper designed to simulate an LLM API interaction 
    and maintain a detailed, cumulative ledger of token usage and financial cost.
    """
    def __init__(self, model_name: str = "gpt-4o_simulated"):
        # Initialize the ledger variables
        self.model_name = model_name
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost_usd = 0.0
        print(f"[{self.model_name}] Cost Tracker initialized using rates: Input=${INPUT_RATE_PER_MILLION}/M, Output=${OUTPUT_RATE_PER_MILLION}/M.")

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """
        Heuristic for token counting. In a production system, this would be replaced 
        by a proper tokenizer (e.g., tiktoken for OpenAI models) or API metadata.
        We use a conservative estimate of 1 token per 4 characters.
        """
        return max(1, len(text) // 4)

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculates the precise dollar cost for a single API transaction.
        """
        
        # Calculate Input Cost: (Token Count / 1 Million) * Rate per Million
        input_cost = (input_tokens / TOKENS_PER_DOLLAR) * INPUT_RATE_PER_MILLION
        
        # Calculate Output Cost
        output_cost = (output_tokens / TOKENS_PER_DOLLAR) * OUTPUT_RATE_PER_MILLION
        
        return input_cost + output_cost

    async def generate_response(self, prompt: str, simulation_delay: float = 0.5) -> Tuple[str, Dict[str, Any]]:
        """
        Simulates the core LLM API interaction, tracks metrics, and updates the ledger.
        """
        start_time = time.perf_counter()
        
        # 1. Pre-API Hook: Estimate Input Tokens before the call
        input_tokens = self._estimate_tokens(prompt)
        
        # Simulate network latency and processing (I/O bound operation)
        await asyncio.sleep(simulation_delay)
        
        # 2. Post-API Hook: Simulate Response and Estimate Output Tokens
        # In a real system, the API response object would contain the actual token count.
        simulated_response = (f"Summary generated successfully for the context provided. "
                              f"The analysis covered {input_tokens} input tokens and resulted in a concise summary.")
        
        output_tokens = self._estimate_tokens(simulated_response)
        
        # 3. Calculate and Log Cost
        transaction_cost = self._calculate_cost(input_tokens, output_tokens)
        
        # 4. Update the Cumulative Ledger (The core economic logging mechanism)
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost_usd += transaction_cost
        
        end_time = time.perf_counter()
        
        # Prepare detailed usage metadata for immediate logging or storage
        metadata = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "transaction_cost_usd": transaction_cost,
            "latency_seconds": round(end_time - start_time, 3)
        }
        
        return simulated_response, metadata

    def report_usage(self):
        """
        Displays the total accumulated usage and cost for the entire session.
        """
        print("\n===================================")
        print("    CUMULATIVE AGENT USAGE REPORT    ")
        print("===================================")
        print(f"Model Used: {self.model_name}")
        print(f"Total Input Tokens (Context): {self.total_input_tokens:,}")
        print(f"Total Output Tokens (Generation): {self.total_output_tokens:,}")
        print(f"TOTAL ESTIMATED COST: ${self.total_cost_usd:,.8f}") 
        print("===================================\n")

async def main():
    # Instantiate the cost tracker for the agent session
    tracker = AsyncLLMCostTracker()
    
    # --- SCENARIO 1: Short Query (Low Input, Medium Output) ---
    prompt_1 = "What are the three main components of a recursive autonomous agent loop?"
    print(f"\n[S1] Query: {prompt_1}")
    response_1, usage_1 = await tracker.generate_response(prompt_1, simulation_delay=0.1)
    
    print(f"    -> S1 Usage: Input={usage_1['input_tokens']} | Output={usage_1['output_tokens']}")
    print(f"    -> S1 Cost: ${usage_1['transaction_cost_usd']:.8f}")

    # --- SCENARIO 2: Heavy Context (High Input, Low Output) ---
    # Simulating a large document analysis required for an agent planning step
    long_context = ("The history of token economics in large language models is complex, beginning with early "
                    "transformer architectures and evolving through various pricing strategies. Key milestones include "
                    "the introduction of tiered pricing, the separation of input and output costs, and the recent trend "
                    "toward highly optimized, low-latency models like GPT-4o and Claude 3 Opus. Understanding these "
                    "historical shifts is crucial for optimizing current agent workflows...")
    
    # We repeat the context many times to simulate a 40,000 character input.
    prompt_2 = "Summarize the key economic trends in LLM pricing from 2020 to present." * 10 
    prompt_2 = long_context + prompt_2 # Ensure high token count
    
    print(f"\n[S2] Query (Heavy Context): {len(prompt_2):,} characters...")
    response_2, usage_2 = await tracker.generate_response(prompt_2, simulation_delay=1.5)
    
    print(f"    -> S2 Usage: Input={usage_2['input_tokens']:,} | Output={usage_2['output_tokens']}")
    print(f"    -> S2 Cost: ${usage_2['transaction_cost_usd']:.8f}") # Noticeably higher input cost

    # --- SCENARIO 3: Cumulative Check (Another short query) ---
    prompt_3 = "Define 'Asynchronous Context Manager' (ACF)."
    print(f"\n[S3] Query: {prompt_3}")
    response_3, usage_3 = await tracker.generate_response(prompt_3, simulation_delay=0.2)
    
    print(f"    -> S3 Cost: ${usage_3['transaction_cost_usd']:.8f}")

    # Final report displays the sum of S1, S2, and S3
    tracker.report_usage()

if __name__ == "__main__":
    # Execute the asynchronous workflow
    asyncio.run(main())
