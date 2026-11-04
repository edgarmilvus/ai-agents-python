from typing import TypedDict, List, Optional, Dict, Any
from langgraph.graph import StateGraph, END
import random

# 1. State Definition
class ChatState(TypedDict):
    chat_history: List[str]
    tool_call_attempt: int
    tool_call_error: Optional[str]
    tool_arguments: Dict[str, Any]
    user_query: str
    tool_output: Optional[str]

# Mock Tool Definition
def mock_calculator_tool(operation: str, a: int, b: int) -> float:
    """Simulates a calculator tool that fails randomly or on specific inputs."""
    
    # Simulate random failure 50% of the time on 'divide' for the first attempt
    if operation == "divide" and b == 5 and random.random() < 0.5:
        raise ValueError("Tool Error: Initial connection failed.")
    
    if operation == "add":
        return a + b
    elif operation == "divide":
        if b == 0:
             raise ZeroDivisionError("Cannot divide by zero.")
        return a / b
    else:
        raise NotImplementedError(f"Operation {operation} not supported.")

# 2. Node Implementations

def router_node(state: ChatState) -> Dict[str, Any]:
    """Initial node: identifies the need for a tool call."""
    query = state["user_query"]
    
    # Assume tool is needed and set initial, potentially faulty, arguments
    args = {"operation": "divide", "a": 100, "b": 5}
    print(f"--- Router: Tool call required. Initial args: {args}")
    return {
        "tool_arguments": args,
        "tool_call_attempt": 0,
        "tool_call_error": None,
        "tool_output": None,
        "chat_history": state["chat_history"] + [f"Agent: Attempting calculation..."]
    }

def tool_executor_node(state: ChatState) -> Dict[str, Any]:
    """Executes the tool and handles exceptions."""
    args = state["tool_arguments"]
    attempt = state["tool_call_attempt"] + 1
    
    print(f"--- Tool Executor: Attempting tool call {attempt} with args: {args}")
    
    try:
        result = mock_calculator_tool(**args)
        
        print(f"--- Tool Executor: SUCCESS.")
        return {
            "tool_output": str(result),
            "tool_call_attempt": attempt,
            "tool_call_error": None
        }
    except Exception as e:
        error_msg = str(e)
        print(f"--- Tool Executor: FAILED. Error: {error_msg}")
        return {
            "tool_call_attempt": attempt,
            "tool_call_error": error_msg
        }

def error_analyzer_node(state: ChatState) -> Dict[str, Any]:
    """Analyzes the error and generates corrected arguments."""
    
    error = state["tool_call_error"]
    current_args = state["tool_arguments"]
    
    # Simulate LLM correction: If we failed on 'divide' with b=5, try b=10
    new_args = current_args.copy()
    if new_args.get('operation') == 'divide' and new_args.get('b') == 5:
        new_args["b"] = 10 # Correct the argument
        print(f"--- Analyzer: Correcting argument 'b' to 10 based on analysis.")
    else:
        print(f"--- Analyzer: Could not determine specific fix. Retrying with same args.")
        
    return {
        "tool_arguments": new_args,
    }

def response_generator_node(state: ChatState) -> Dict[str, Any]:
    """Generates the final response based on success or failure."""
    
    output = state.get("tool_output")
    error = state.get("tool_call_error")
    
    if output:
        final_message = f"Calculation successful after {state['tool_call_attempt']} attempts. Result: {output}"
    else:
        final_message = f"Calculation failed permanently after {state['tool_call_attempt']} attempts. Last error: {error}"
        
    return {
        "chat_history": state["chat_history"] + [f"Agent: {final_message}"]
    }

# Conditional Routing Function
def route_tool_result(state: ChatState) -> str:
    error = state.get("tool_call_error")
    output = state.get("tool_output")
    attempts = state["tool_call_attempt"]
    MAX_RETRIES = 3
    
    if output is not None:
        return "response_generator_node" # Success
    
    if error is not None:
        if attempts < MAX_RETRIES:
            return "error_analyzer_node"
        else:
            return "response_generator_node" # Max attempts reached
            
    return END # Should only happen if initial state was empty

# 3. Build the Graph
workflow = StateGraph(ChatState)

workflow.add_node("router_node", router_node)
workflow.add_node("tool_executor_node", tool_executor_node)
workflow.add_node("error_analyzer_node", error_analyzer_node)
workflow.add_node("response_generator_node", response_generator_node)

workflow.set_entry_point("router_node")
workflow.add_edge("router_node", "tool_executor_node")

# Conditional edge from tool_executor_node drives the retry cycle
workflow.add_conditional_edges(
    "tool_executor_node",
    route_tool_result,
    {
        "error_analyzer_node": "error_analyzer_node",
        "response_generator_node": "response_generator_node"
    }
)

# Cycle back to executor
workflow.add_edge("error_analyzer_node", "tool_executor_node")
workflow.add_edge("response_generator_node", END)

app_845 = workflow.compile()

# Example Execution
initial_state = {
    "user_query": "Please calculate 100 divided by 5.",
    "chat_history": ["User: Please calculate 100 divided by 5."],
    "tool_call_attempt": 0,
    "tool_call_error": None,
    "tool_arguments": {},
    "tool_output": None
}

print("--- Starting Interactive Chatbot with Tool Retries ---")
final_state = app_845.invoke(initial_state)

print("\n--- Final Chat History ---")
for message in final_state['chat_history']:
    print(message)
