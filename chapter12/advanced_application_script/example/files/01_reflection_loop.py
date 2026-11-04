import json
import time
from typing import Optional, Dict, Any

# --- 1. Mock External Tool Definition ---

def fetch_stock_data(ticker: str) -> str:
    """
    Simulates an external API call. 
    It intentionally validates input and returns structured error JSON 
    to simulate a 'logical failure' (tool works, but input is bad).
    """
    time.sleep(0.5) # Simulate latency
    
    ticker = ticker.upper().strip()
    
    if not ticker:
        # This simulates a critical input validation failure
        return json.dumps({"status": "error", "message": "Ticker cannot be empty. Missing required security identifier."})
        
    if ticker not in ["AAPL", "GOOGL"]:
        # Simulating an unsupported ticker error
        return json.dumps({"status": "error", "message": f"Invalid or unsupported ticker: {ticker}. Only AAPL/GOOGL allowed."})
        
    # Success cases
    if ticker == "AAPL":
        return json.dumps({"ticker": "AAPL", "price": 175.50, "volume": 1200000, "currency": "USD"})
    if ticker == "GOOGL":
        return json.dumps({"ticker": "GOOGL", "price": 2500.25, "volume": 850000, "currency": "USD"})
    
    # Fallback for unexpected internal issues
    raise ValueError("Unexpected internal tool execution error.")


# --- 2. Mock LLM Interaction (Simulating Planning and Reflection) ---

def call_llm(prompt: str, is_reflection: bool = False) -> str:
    """
    Mock function for LLM interaction, designed to simulate specific outputs 
    based on the phase (initial plan vs. reflection).
    """
    
    if is_reflection:
        # --- Reflection Phase Mock ---
        if "Missing Ticker" in prompt or "Ticker cannot be empty" in prompt:
            print(">>> LLM (Reflection): Diagnosed missing required input. Suggesting GOOGL.")
            # The LLM generates a new plan/input based on the trace
            return json.dumps({
                "action": "retry", 
                "new_ticker": "GOOGL", 
                "reason": "Initial plan failed due to missing security identifier (empty ticker). Attempting GOOGL."
            })
        elif "Invalid or unsupported ticker: MSFT" in prompt:
            print(">>> LLM (Reflection): Diagnosed unsupported ticker MSFT. Suggesting AAPL.")
            return json.dumps({
                "action": "retry", 
                "new_ticker": "AAPL", 
                "reason": "MSFT is not supported by the current tool. Switching to supported ticker AAPL."
            })
        
        # Fallback for unexpected reflection failure
        return json.dumps({"action": "abort", "reason": "Reflection inconclusive or unexpected error."})

    else:
        # --- Initial Planning Phase Mock ---
        # Simulate the agent making a mistake on the first attempt (e.g., providing empty input)
        if "Analyze the market data" in prompt:
            print(">>> LLM (Initial Plan): Generated plan with empty ticker (simulated mistake).")
            # The agent's initial output structure (Tool usage JSON)
            return '{"tool": "fetch_stock_data", "ticker": ""}'
        
        # Optional: Simulate a second attempt where the agent uses a known bad ticker
        if "MSFT" in prompt:
             print(">>> LLM (Initial Plan): Generated plan with unsupported ticker MSFT.")
             return '{"tool": "fetch_stock_data", "ticker": "MSFT"}'
             
        return "Task completed successfully." # Should only be hit if the agent generates a successful plan immediately


# --- 3. Reflection Prompt Generation ---

def generate_reflection_prompt(trace: Dict[str, Any], error: str) -> str:
    """Generates the detailed, structured prompt for the reflection agent."""
    return f"""
    [CRITICAL_REFLECTION_REQUEST]
    Analyze the following failed execution trace to diagnose the error and propose a corrective action.
    The goal was to fetch financial data using the 'fetch_stock_data' tool.
    
    --- EXECUTION TRACE ---
    Attempted Input Ticker: '{trace['input_ticker']}'
    Observed System/Tool Error: {error}
    
    Based on the error, determine the necessary modification to the input parameters or plan.
    Respond ONLY with a JSON object containing:

    1. 'action' (must be 'retry' or 'abort')
    2. 'new_ticker' (the corrected input parameter for the next attempt)
    3. 'reason' (a brief explanation of the diagnosis and correction).
    """

# --- 4. Core Execution Loop with Self-Correction ---

def execute_task_with_reflection(initial_task_prompt: str, max_retries: int = 3) -> Dict[str, Any]:
    """
    Manages the execution flow, integrating error catching and the recursive reflection loop.
    """
    current_attempt = 0
    current_ticker = "" # State variable modified by the reflection step
    
    while current_attempt < max_retries:
        print(f"\n{'='*20} [Attempt {current_attempt + 1}/{max_retries}] Starting Execution {'='*20}")
        current_attempt += 1
        
        # Initialize trace for the current run
        execution_trace = {"input_ticker": current_ticker, "output": None, "error": None}

        try:
            # 4a. Planning/Action Generation Phase (Only on the first attempt, or if state is reset)
            if current_attempt == 1:
                llm_response_json = call_llm(initial_task_prompt)
                action_data = json.loads(llm_response_json)
                current_ticker = action_data.get("ticker", "")
                
            execution_trace["input_ticker"] = current_ticker
            
            # 4b. Execute the Tool using the current state
            print(f"Executing tool with ticker: '{current_ticker}'")
            tool_output = fetch_stock_data(current_ticker)
            
            # 4c. Custom Error Handler: Check for logical failures in tool response
            tool_result = json.loads(tool_output)
            if tool_result.get("status") == "error":
                # Raise a runtime error based on the tool's structured failure message
                raise RuntimeError(f"Tool reported logical error: {tool_result['message']}")

            # Success Path
            execution_trace["output"] = tool_result
            print(f"\n[SUCCESS] Task completed. Data retrieved for {current_ticker}.")
            return {"status": "success", "result": tool_result}

        except (RuntimeError, ValueError) as e:
            # 4d. Failure Catch and Trace Recording
            error_message = str(e)
            execution_trace["error"] = error_message
            print(f"\n[FAILURE DETECTED] Error: {error_message}")
            
            if current_attempt >= max_retries:
                print("Max retries reached. Aborting task.")
                return {"status": "failed", "reason": error_message}
            
            # 4e. Reflection Phase: Generate prompt based on the failed trace
            reflection_prompt = generate_reflection_prompt(execution_trace, error_message)
            
            # 4f. Get Corrective Action
            correction_response = call_llm(reflection_prompt, is_reflection=True)
            correction_data = json.loads(correction_response)
            
            # 4g. Apply Dynamic Plan Modification (State Update)
            if correction_data.get("action") == "retry" and correction_data.get("new_ticker"):
                current_ticker = correction_data["new_ticker"]
                print(f"--- Correction Applied: New input parameter set to '{current_ticker}'. Retrying... ---")
            else:
                print("Reflection failed to provide a clear retry plan or suggested 'abort'. Aborting.")
                return {"status": "failed", "reason": "Reflection inconclusive."}

    return {"status": "failed", "reason": "Exited loop unexpectedly."}


# --- 5. Execution ---
if __name__ == "__main__":
    INITIAL_TASK = "Analyze the market data for a major tech company by fetching its stock price."
    
    final_result = execute_task_with_reflection(INITIAL_TASK, max_retries=3)
    
    print("\n" + "="*50)
    print("FINAL EXECUTION SUMMARY")
    print("="*50)
    print(json.dumps(final_result, indent=2))
