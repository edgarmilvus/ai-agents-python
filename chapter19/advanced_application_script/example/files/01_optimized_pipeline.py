import os
import json
from pydantic import BaseModel, Field
from openai import OpenAI
from typing import List

# --- 1. Configuration and Definitions ---

# The endpoint, model and key come from the environment.
BASE_URL = os.environ.get("OPENAI_COMPATIBLE_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("OPENAI_COMPATIBLE_MODEL", "~deepseek/deepseek-flash-latest")
OPENAI_COMPATIBLE_API_KEY = os.getenv("OPENAI_COMPATIBLE_API_KEY")

# Simplified cost constants: the rates your deployed model publishes, per 1M tokens.
# They are here to be multiplied, not to be trusted for a bill.
INPUT_COST_PER_MILLION = 0.50  # $0.50 per million input tokens
OUTPUT_COST_PER_MILLION = 1.50 # $1.50 per million output tokens

class MarketSummary(BaseModel):
    """Structured output schema for guaranteed extraction of key metrics."""
    key_sentiment: str = Field(description="Overall sentiment (Positive, Negative, Mixed).")
    top_pain_point: str = Field(description="The single most common complaint or issue identified.")
    actionable_recommendations: List[str] = Field(description="3-5 specific, concise actions derived from the feedback.")
    token_optimization_status: bool = Field(description="Always True if the input context was successfully compressed.")

def calculate_cost(usage):
    """Calculates the estimated dollar cost based on token usage statistics."""
    # Ensure usage object has required attributes for robust calculation
    input_tokens = getattr(usage, 'prompt_tokens', 0)
    output_tokens = getattr(usage, 'completion_tokens', 0)
    
    input_cost = (input_tokens / 1_000_000) * INPUT_COST_PER_MILLION
    output_cost = (output_tokens / 1_000_000) * OUTPUT_COST_PER_MILLION
    return input_cost + output_cost

# --- 2. Simulated Inputs ---

# Simulate a very long, verbose, and repetitive raw feedback document (often exceeding 1000 tokens)
RAW_FEEDBACK = """
The new application interface is incredibly confusing. I spent nearly 45 minutes trying to find the settings menu, and even then, the labels were not intuitive. 
Many users, including myself, have experienced significant latency issues during peak hours, specifically between 2 PM and 5 PM EST. This needs immediate attention. 
However, the customer support team was outstanding—fast response times and very helpful resolution. 
The pricing structure, while generally fair, is slightly too complex for small businesses; a simplified tier would be better. 
I also noticed that the mobile app crashes frequently when attempting to upload large files, which is a major blocker for my workflow. 
Overall, the core functionality is strong, but the user experience (UX) is severely lacking. 
We need better documentation and clearer tooltips. The search feature is completely broken, returning irrelevant results consistently. 
This document is intentionally verbose to simulate real-world, messy, long-form data requiring compression. 
The main complaints are UX, latency, and mobile stability. The positive is customer service. The overall tone is frustrated but hopeful.
"""

# --- 3. Agent Execution Function (Optimized Flow) ---

def execute_optimized_analysis(raw_text: str):
    """
    Executes a two-step analysis process: Context Compression followed by Structured Extraction.
    This minimizes the token count sent to the expensive structured output step.
    """
    client = OpenAI(base_url=BASE_URL, api_key=OPENAI_COMPATIBLE_API_KEY)
    # Initialize a dictionary to track accumulated usage across all steps
    total_usage = {"prompt_tokens": 0, "completion_tokens": 0}
    
    # --- Step A: Context Compression (Token Trimming) ---
    print("--- 1. Context Compression Phase (Input Optimization) ---")
    compression_prompt = (
        f"Condense the following verbose market feedback into a concise, professional summary "
        f"of no more than 150 words, focusing only on key sentiments, pain points, and core recommendations:\n\n{raw_text}"
    )
    
    # Execute compression call (simple, fast, unstructured output)
    compression_response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": compression_prompt}],
        temperature=0.1
    )
    
    compressed_summary = compression_response.choices[0].message.content
    usage_step_a = compression_response.usage
    
    # Log and accumulate usage statistics for Step A
    total_usage['prompt_tokens'] += usage_step_a.prompt_tokens
    total_usage['completion_tokens'] += usage_step_a.completion_tokens
    
    print(f"Initial Raw Context Tokens: {usage_step_a.prompt_tokens}")
    print(f"Compressed Summary Tokens Used: {usage_step_a.completion_tokens}")
    print("-" * 30)
    
    # --- Step B: Structured Extraction (Using Compressed Context) ---
    print("--- 2. Structured Extraction Phase (Output Optimization) ---")
    
    # The extraction prompt now uses the significantly shorter, compressed summary
    # The schema travels in the prompt, because `response_format` only promises
    # "some JSON object"; validation is what pins the fields.
    extraction_prompt = (
        "Analyze the following compressed market summary and extract the requested structured data. "
        "Ensure the 'token_optimization_status' field is set to True.\n"
        f"The object must validate against this JSON schema:\n"
        f"{json.dumps(MarketSummary.model_json_schema())}"
        f"\n\nCOMPRESSED SUMMARY:\n{compressed_summary}"
    )

    # Ask for a JSON object rather than a JSON schema: `response_format` with a
    # schema is a per-gateway feature, and not every endpoint offers it. The
    # schema is still enforced here, by validating the answer against the model.
    extraction_response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system",
             "content": "Reply with a single JSON object and nothing else."},
            {"role": "user", "content": extraction_prompt},
        ],
        response_format={"type": "json_object"}, # CRITICAL: Structured output optimization
        temperature=0.0 # Low temperature for deterministic extraction
    )

    usage_step_b = extraction_response.usage

    # Log and accumulate usage statistics for Step B
    total_usage['prompt_tokens'] += usage_step_b.prompt_tokens
    total_usage['completion_tokens'] += usage_step_b.completion_tokens

    # --- 4. Reporting and Output ---
    
    # Convert accumulated usage dictionary back to a simple object for the cost function
    FinalUsage = type('FinalUsage', (object,), total_usage)
    total_cost = calculate_cost(FinalUsage)
    
    # Validation is what makes it structured: a missing or misspelt field raises
    # here instead of travelling downstream.
    structured_output = MarketSummary.model_validate_json(
        extraction_response.choices[0].message.content
    )
    extracted_data = json.loads(structured_output.model_dump_json())
    
    print(f"Extraction Prompt Tokens (Optimized Context): {usage_step_b.prompt_tokens}")
    print(f"Structured Output Tokens: {usage_step_b.completion_tokens}")
    print("-" * 30)
    
    print("\n--- Final Structured Output ---")
    print(json.dumps(extracted_data, indent=4))
    print("\n--- Economic Report (Accumulated) ---")
    print(f"Total Prompt Tokens (Input Cost): {FinalUsage.prompt_tokens}")
    print(f"Total Completion Tokens (Output Cost): {FinalUsage.completion_tokens}")
    print(f"Estimated Total Cost: ${total_cost:.5f}")

# --- 5. Execution ---
if __name__ == "__main__":
    if not OPENAI_COMPATIBLE_API_KEY:
        print("ERROR: OPENAI_COMPATIBLE_API_KEY environment variable not set. Please configure your environment.")
    else:
        execute_optimized_analysis(RAW_FEEDBACK)
