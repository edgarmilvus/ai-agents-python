import json
from typing import Dict, Any

# --- Custom Exceptions ---
class AgentError(Exception): pass
class NetworkToolError(AgentError): pass

# --- Simulated LLM/Agent Interaction Functions (updated for this exercise) ---
def mock_llm_call(prompt: str, temperature: float = 0.1) -> str:
    # ... (omitting previous mock logic for brevity, focusing on new logic) ...
    if "recovery strategy" in prompt.lower():
        if "runtime failure" in prompt.lower():
            return "RETRY_STRATEGY: Wait 5 seconds and attempt the API call again."
        if "logical failure" in prompt.lower():
            return "REPLAN_STRATEGY: The ID was not found. Modify the input parameter to search for a related resource using a wildcard."
    return ""

def external_api_tool(id_param: str) -> Dict[str, Any]:
    """Simulates an external tool with different failure modes."""
    if id_param == "FAIL_NETWORK":
        # 1. Simulate Runtime Error
        raise NetworkToolError("Connection timeout during request.")
    elif id_param == "INVALID_ID":
        # 2. Simulate Logical Failure
        return {"success": False, "error_code": 404, "message": "Resource ID not found in primary index."}
    else:
        return {"success": True, "data": f"Resource data for {id_param}"}

def agent_execution_handler(id_param: str):
    print(f"\n--- exercise 2: Handling ID '{id_param}' ---")
    try:
        tool_output = external_api_tool(id_param)
        
        # 3. Logical Failure Analysis
        if not tool_output.get('success', True): # Check if 'success' is explicitly False
            error_code = tool_output.get('error_code', 'UNKNOWN')
            error_msg = tool_output.get('message', 'No message provided.')
            
            # 4. Generate Recovery Strategy (LLM call based on classification)
            recovery_prompt = (
                f"A logical failure occurred with error code {error_code} and message: '{error_msg}'. "
                f"Classify this as a logical failure and generate a recovery strategy."
            )
            strategy = mock_llm_call(recovery_prompt)
            print(f"  [CLASSIFICATION] Logical Failure (404/Bad Input)")
            print(f"  [RECOVERY PLAN] {strategy}")
            return
            
        print(f"  [SUCCESS] Tool executed successfully: {tool_output['data']}")

    except NetworkToolError as e:
        # 2. Catch Runtime Exception
        recovery_prompt = (
            f"A runtime failure occurred: {e}. Classify this as a transient network failure and generate a recovery strategy."
        )
        strategy = mock_llm_call(recovery_prompt)
        print(f"  [CLASSIFICATION] Runtime Failure (Network)")
        print(f"  [RECOVERY PLAN] {strategy}")
    except Exception as e:
        print(f"  [UNHANDLED ERROR] An unexpected error occurred: {type(e).__name__}")

# Execution
agent_execution_handler("VALID_ID_123")
agent_execution_handler("FAIL_NETWORK")
agent_execution_handler("INVALID_ID")
