import asyncio
import json
from pydantic import BaseModel, ValidationError

import tiktoken

# --- Setup for Token Counting (Used in Exercises 2 and 4) ---
TOKEN_ENCODER = tiktoken.get_encoding("cl100k_base")

def calculate_tokens(text: str) -> int:
    """Calculates the token count for a given string."""
    return len(TOKEN_ENCODER.encode(text))

# =============================================================
# Exercise 4 Solution
# =============================================================

# 1. Define the Pydantic Schema
class ToolArguments(BaseModel):
    """Schema for the arguments passed to the selected tool."""
    departure: str
    arrival: str
    date: str

class AgentAction(BaseModel):
    """The structured output schema for the Agent's decision."""
    tool_name: str
    tool_arguments: ToolArguments
    justification: str

# 2. Simulate LLM Integration
async def generate_structured_action(user_query: str) -> AgentAction:
    """
    Simulates an LLM call designed to return a guaranteed JSON object 
    conforming to the AgentAction schema.
    """
    print(f"\n[Agent Reasoning] Processing query: '{user_query}'")
    
    # Simulated Raw JSON output from LLM (low token count, efficient)
    simulated_json_output = json.dumps({
        "tool_name": "FlightSearchTool",
        "tool_arguments": {
            "departure": "NYC",
            "arrival": "LAX",
            "date": "2024-12-25"
        },
        "justification": "Checked flight prices for Christmas travel to fulfill user request."
    }, indent=None) # Minimize whitespace for token efficiency
    
    # 3. Simulate Inefficient Free-Form Output (High token count, verbose)
    simulated_free_form_output = (
        "Thought: The user is asking for flight information. I must use the "
        "FlightSearchTool to find the cheapest flight from NYC to LAX on the specified date. "
        "This is the first step in the planning process, and I need to ensure the date is correct. "
        f"Action: FlightSearchTool; Action Input: {{"
        '"departure": "NYC", "arrival": "LAX", "date": "2024-12-25"}}'
    )

    # Token Cost Analysis Simulation
    json_tokens = calculate_tokens(simulated_json_output)
    free_form_tokens = calculate_tokens(simulated_free_form_output)
    
    reduction = free_form_tokens - json_tokens
    percent_reduction = (reduction / free_form_tokens) * 100
    
    print(f"  Token Cost Comparison:")
    print(f"    1. Free-Form Output Tokens: {free_form_tokens}")
    print(f"    2. Structured JSON Tokens: {json_tokens}")
    print(f"    Token Saving: {reduction} tokens ({percent_reduction:.2f}%)")
    
    # Assert the required token reduction
    if percent_reduction < 30:
        print(f"[Warning] Token reduction ({percent_reduction:.2f}%) is less than the target 30%.")
    
    # 4. Parsing and Validation
    try:
        # Pydantic validates and parses the raw JSON string
        action = AgentAction.model_validate_json(simulated_json_output)
        print("  [Validation SUCCESS] Structured output successfully parsed into AgentAction model.")
        return action
    except ValidationError as e:
        print(f"  [Validation FAILURE] Error parsing structured output: {e}")
        raise

async def run_exercise_4():
    print("--- Running Exercise 4: Structured Output Optimization ---")
    
    user_query = "Find the cheapest direct flight from New York to Los Angeles for Christmas Day."
    
    structured_action = await generate_structured_action(user_query)
    
    print("\n--- Final Validated Action Object ---")
    print(f"Tool: {structured_action.tool_name}")
    print(f"Args: {structured_action.tool_arguments.model_dump_json(indent=2)}")
    print(f"Justification: {structured_action.justification}")

asyncio.run(run_exercise_4())
