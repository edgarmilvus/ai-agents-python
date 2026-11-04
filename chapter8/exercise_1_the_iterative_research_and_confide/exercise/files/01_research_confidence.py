from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
import random

# 1. State Definition
class ResearchState(TypedDict):
    """Defines the state for the iterative research agent."""
    query: str
    results: List[str]
    confidence_score: int
    search_attempts: int

# 2. Node Implementations

def researcher_node(state: ResearchState) -> Dict[str, Any]:
    """Generates the initial query or refines an existing query."""
    attempts = state.get("search_attempts", 0) + 1
    
    if attempts == 1:
        new_query = state["query"]
        print(f"--- Attempt {attempts}: Starting research on: {new_query}")
    else:
        # Simulate LLM refining the query based on previous low confidence results
        prev_query = state["query"]
        new_query = f"{prev_query} (Refined focus: Need more economic data)"
        print(f"--- Attempt {attempts}: Refining query based on low confidence ({state['confidence_score']}): {new_query}")
    
    return {
        "query": new_query,
        "search_attempts": attempts
    }

def tool_call_node(state: ResearchState) -> Dict[str, Any]:
    """Simulates executing a search tool."""
    current_query = state["query"]
    attempt = state["search_attempts"]
    
    # Mock results: results improve with attempts
    mock_results = [
        f"Doc A (Attempt {attempt}): Basic definition.",
        f"Doc B (Attempt {attempt}): Initial market projections.",
    ]
    if attempt >= 2:
        mock_results.append(f"Doc C (Attempt {attempt}): Detailed economic model data.")
    
    print(f"--- Tool Call: Fetched {len(mock_results)} documents.")
    
    # Append new results to existing ones
    current_results = state.get("results", [])
    return {
        "results": current_results + mock_results
    }

def evaluator_node(state: ResearchState) -> Dict[str, Any]:
    """Evaluates results, assigns confidence, and updates the state."""
    
    attempts = state["search_attempts"]
    
    # Confidence increases linearly with attempts (to force termination)
    simulated_confidence = min(20 + attempts * 30, 100)
    
    print(f"--- Evaluation: Current confidence score: {simulated_confidence}/100.")
    
    return {
        "confidence_score": simulated_confidence
    }

def route_research(state: ResearchState) -> str:
    """Conditional edge logic for the loop."""
    confidence = state["confidence_score"]
    attempts = state["search_attempts"]
    
    MAX_ATTEMPTS = 3
    CONFIDENCE_THRESHOLD = 80
    
    if confidence < CONFIDENCE_THRESHOLD and attempts < MAX_ATTEMPTS:
        return "researcher_node"
    else:
        return END

# 3. Build the Graph
workflow = StateGraph(ResearchState)

workflow.add_node("researcher_node", researcher_node)
workflow.add_node("tool_call_node", tool_call_node)
workflow.add_node("evaluator_node", evaluator_node)

# Define edges
workflow.add_edge("researcher_node", "tool_call_node")
workflow.add_edge("tool_call_node", "evaluator_node")

# Conditional edge from evaluator_node drives the cycle
workflow.add_conditional_edges(
    "evaluator_node",
    route_research,
    {
        "researcher_node": "researcher_node",
        END: END
    }
)

# Set entry point
workflow.set_entry_point("researcher_node")

app_841 = workflow.compile()

# Example Execution
initial_state = {
    "query": "The economic impact of quantum computing on cryptography",
    "results": [],
    "confidence_score": 0,
    "search_attempts": 0
}

print("--- Starting Iterative Research Agent ---")
final_state = app_841.invoke(initial_state)
print("\n--- Final State Summary ---")
print(f"Final Confidence: {final_state['confidence_score']}")
print(f"Total Attempts: {final_state['search_attempts']}")
print(f"Total Documents: {len(final_state['results'])}")
