import json
from typing import Callable, Dict, Any

# --- 1. THE TOOL FUNCTION (The Logic) ---

def celsius_to_fahrenheit(celsius: float) -> float:
    """
    Converts a temperature from Celsius to Fahrenheit using the standard formula.
    This function represents the actual, deterministic task the LLM delegates.
    """
    # Standard conversion formula: (C * 9/5) + 32
    return (celsius * 9/5) + 32

# --- 2. THE TOOL SCHEMA (The LLM's Instruction Manual) ---

# This dictionary defines the function's interface in a JSON format 
# that the LLM understands (following the standard OpenAI function calling specification).
tool_schema = {
    "name": "celsius_to_fahrenheit",
    "description": "Converts temperature from Celsius (C) to Fahrenheit (F). Essential for providing temperature conversions to users.",
    "parameters": {
        "type": "object",
        "properties": {
            "celsius": {
                "type": "number",
                "description": "The temperature value in Celsius (e.g., 25.0) to be converted."
            }
        },
        # The 'required' list tells the LLM which parameters MUST be provided.
        "required": ["celsius"]
    }
}

# --- 3. THE TOOL REGISTRY (The Agent's Lookup Table) ---

# This maps the string name (used by the LLM in its response) to the 
# actual executable Python function object.
TOOL_REGISTRY: Dict[str, Callable] = {
    "celsius_to_fahrenheit": celsius_to_fahrenheit
}

# --- 4. THE AGENT EXECUTION SIMULATION ---

def execute_tool_call(tool_name: str, arguments: Dict[str, Any]) -> Any:
    """
    Simulates the Agent receiving a function call request from the LLM, 
    looking up the function, and executing it.
    """
    print(f"\n[AGENT ACTION]: LLM requested tool '{tool_name}' with arguments: {arguments}")
    
    if tool_name in TOOL_REGISTRY:
        tool_function = TOOL_REGISTRY[tool_name]
        
        # CRITICAL STEP: The arguments dictionary provided by the LLM is unpacked 
        # directly into the Python function's parameters.
        try:
            result = tool_function(**arguments)
            
            print(f"[TOOL OUTPUT]: Conversion successful.")
            return result
            
        except TypeError as e:
            # Catches issues if the LLM provides arguments the function doesn't accept
            print(f"[ERROR]: Type mismatch during execution. Details: {e}")
            return f"Error executing tool: {e}"
            
    else:
        raise ValueError(f"Tool '{tool_name}' not found in registry. Cannot execute.")

# --- SIMULATION START ---
print("--- Tool Definition Phase Complete ---")
print(f"The Agent presents this schema to the LLM:\n{json.dumps(tool_schema, indent=2)}")

# SCENARIO: The user asks the LLM to convert 25 degrees Celsius.

# STEP 1: Hypothetical LLM response suggesting a tool call
# The LLM reasons: "I need to call 'celsius_to_fahrenheit' with 'celsius=25.0'."
hypothetical_llm_call = {
    "tool_name": "celsius_to_fahrenheit",
    "arguments": {
        "celsius": 25.0
    }
}

print("\n--- Simulation of LLM Suggestion Received by Agent ---")
print(f"LLM Suggestion Payload: {hypothetical_llm_call}")

# STEP 2: The Python Agent executes the suggestion
final_result = execute_tool_call(
    tool_name=hypothetical_llm_call["tool_name"],
    arguments=hypothetical_llm_call["arguments"]
)

# STEP 3: The result is packaged and sent back to the LLM for final response generation
print("\n--- Simulation Complete ---")
print(f"[FINAL RESULT]: The agent obtained the result: {final_result:.2f} F")
