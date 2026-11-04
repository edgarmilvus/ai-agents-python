from pydantic import BaseModel, Field
from typing import List, Dict, Any
from langgraph.graph import StateGraph, END

# 1. State Schema Definition using Pydantic
class ProcessingState(BaseModel):
    """Robust state schema for tracking data processing."""
    raw_inputs: List[str] = Field(default_factory=list)
    processed_outputs: List[Dict[str, Any]] = Field(default_factory=list)
    error_log: List[str] = Field(default_factory=list)
    total_items: int = 0
    current_index: int = 0

# 2. Node Implementations

def input_fetcher(state: ProcessingState) -> Dict[str, Any]:
    """Initializes the raw inputs and total count."""
    initial_inputs = [
        "25 C", "100 F", "Invalid Data", "77 K", "50 C"
    ]
    
    print(f"--- Fetcher: Initializing {len(initial_inputs)} items.")
    
    return {
        "raw_inputs": initial_inputs,
        "total_items": len(initial_inputs),
        "current_index": 0
    }

def processor_node(state: ProcessingState) -> Dict[str, Any]:
    """Processes the current item based on the index."""
    
    idx = state.current_index
    item = state.raw_inputs[idx]
    
    updates = {}
    
    # Simulate validation and standardization
    if "Invalid" in item:
        error_msg = f"Validation failed for item {idx}: '{item}'. Invalid format detected."
        print(f"--- Processor: FAILED item {idx}.")
        updates["error_log"] = state.error_log + [error_msg]
        
    elif "C" in item or "F" in item or "K" in item:
        # Simulate successful processing
        value, unit = item.split()
        processed_data = {"id": idx, "original": item, "standardized_unit": unit, "value": int(value)}
        print(f"--- Processor: SUCCESS item {idx}.")
        updates["processed_outputs"] = state.processed_outputs + [processed_data]
        
    return updates

def index_incrementer_and_router(state: ProcessingState) -> Dict[str, Any]:
    """Increments the index and prepares for the next step."""
    
    current = state.current_index
    next_index = current + 1
    
    # Return the state update (incrementing the index)
    return {"current_index": next_index}

def route_on_index(state: ProcessingState) -> str:
    """Conditional routing based on index completion."""
    if state.current_index < state.total_items:
        return "processor_node"
    return END

# 3. Build the Graph
# Pass the Pydantic model to the StateGraph constructor
workflow = StateGraph[ProcessingState](ProcessingState)

workflow.add_node("input_fetcher", input_fetcher)
workflow.add_node("processor_node", processor_node)
workflow.add_node("index_router", index_incrementer_and_router)

# Define Entry
workflow.set_entry_point("input_fetcher")
workflow.add_edge("input_fetcher", "processor_node")

# Cycle: processor -> index_router -> (conditional) -> processor or END
workflow.add_edge("processor_node", "index_router")

workflow.add_conditional_edges(
    "index_router",
    route_on_index,
    {
        "processor_node": "processor_node",
        END: END
    }
)

app_842 = workflow.compile()

# Example Execution
# Note: Since the state is Pydantic, we must pass the initial data as a dictionary 
# which LangGraph validates against the schema.
initial_state = ProcessingState().model_dump() 

print("--- Starting Data Processing Agent ---")
final_state = app_842.invoke(initial_state)

print("\n--- Final State Summary ---")
print(f"Total items processed: {final_state['total_items']}")
print(f"Successful outputs: {len(final_state['processed_outputs'])}")
print(f"Errors logged: {final_state['error_log']}")
