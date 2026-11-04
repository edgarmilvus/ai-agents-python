from typing import TypedDict, Optional, Dict, Any
from langgraph.graph import StateGraph, END
import random

# 1. State Definition
class CodeState(TypedDict):
    prompt: str
    code_draft: Optional[str]
    test_results: str
    attempt_count: int

# 2. Node Implementations

def code_generator(state: CodeState) -> Dict[str, Any]:
    """Generates initial code or fixes existing code."""
    
    attempt = state.get("attempt_count", 0)
    
    if attempt == 0:
        draft = "def sort_list(data):\n    return data.reverse()" # Intentionally wrong
        print(f"--- Generator: Initial code draft created (Attempt 1).")
    else:
        # Simulate LLM applying the fix based on feedback
        feedback = state["test_results"]
        draft = f"def sort_list(data, attempt={attempt+1}):\n    # Fixed based on feedback: {feedback}\n    return sorted(data)"
        print(f"--- Generator: Debugging attempt {attempt+1}. Applying fix.")
        
    return {
        "code_draft": draft,
        "test_results": "PENDING"
    }

def test_runner(state: CodeState) -> Dict[str, Any]:
    """Simulates running tests and returns PASS or FAIL."""
    
    attempt = state.get("attempt_count", 0) + 1
    
    # Simulation logic
    if attempt == 1:
        result = "FAIL: List reverse() returns None."
    elif attempt == 2:
        result = "FAIL: Still using reverse() incorrectly."
    else:
        # Guaranteed pass after 2 failures, simulating successful fix
        result = "PASS"
    
    print(f"--- Test Runner: Attempt {attempt}. Result: {result.split(':')[0]}")
    
    return {
        "test_results": result,
        "attempt_count": attempt
    }

def debugger_node(state: CodeState) -> Dict[str, Any]:
    """Analyzes test failures and prepares context for the generator."""
    
    error = state["test_results"]
    print(f"--- Debugger: Analyzing error: '{error}'. Preparing instructions.")
    
    # In a real scenario, this node's output would be used by the generator.
    return {}

def failure_report_node(state: CodeState) -> Dict[str, Any]:
    """Reports final failure after max attempts."""
    print(f"--- FINAL REPORT: Failed to fix code after {state['attempt_count']} attempts.")
    return {"test_results": "PERMANENT_FAIL"}

# Conditional Routing Function
def route_tests(state: CodeState) -> str:
    results = state["test_results"]
    attempts = state["attempt_count"]
    MAX_ATTEMPTS = 5
    
    if results == "PASS":
        return END
    
    if attempts >= MAX_ATTEMPTS:
        return "failure_report_node"
    
    # If FAIL and attempts < MAX_ATTEMPTS
    return "debugger_node"

# 3. Build the Graph
workflow = StateGraph(CodeState)

workflow.add_node("code_generator", code_generator)
workflow.add_node("test_runner", test_runner)
workflow.add_node("debugger_node", debugger_node)
workflow.add_node("failure_report_node", failure_report_node)

# Define Edges
workflow.set_entry_point("code_generator")
workflow.add_edge("code_generator", "test_runner")

# Conditional edge from test_runner drives the cycle
workflow.add_conditional_edges(
    "test_runner",
    route_tests,
    {
        END: END,
        "debugger_node": "debugger_node",
        "failure_report_node": "failure_report_node"
    }
)

# Cycle back to generator
workflow.add_edge("debugger_node", "code_generator")

# Final edge from failure report
workflow.add_edge("failure_report_node", END)

app_843 = workflow.compile()

# Example Execution
initial_state = {
    "prompt": "Write a Python function to sort a list.",
    "code_draft": None,
    "test_results": "INITIAL",
    "attempt_count": 0
}

print("--- Starting Code Refinement Agent ---")
app_843.invoke(initial_state)
