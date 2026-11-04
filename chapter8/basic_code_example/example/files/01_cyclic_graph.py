import operator
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END

# --- 1. Define the Graph State Schema ---
# LangGraph relies on a defined state object to pass data between nodes.
class GraphState(TypedDict):
    """
    Represents the state of our graph.

    generation: The current generated output (e.g., the title).
    iterations: Counter to simulate the difficulty of the task and control the mock LLM.
    """
    generation: str
    iterations: Annotated[int, operator.add]
    decision: str
    
# --- 2. Define the Graph Nodes (Functions) ---

def generate_title(state: GraphState) -> GraphState:
    """
    Node A: Simulates the LLM generating a title.
    Increments the iteration count and updates the generation string.
    """
    print(f"--- Running Node A: Generation (Iteration {state['iterations'] + 1}) ---")
    
    # Retrieve the current iteration count
    current_iterations = state['iterations']
    
    # Mock LLM behavior: Fail first time, succeed second time
    if current_iterations == 0:
        # Fails the 5-word constraint intentionally
        new_title = "This is a very long and verbose title."
    else:
        # Succeeds on the second attempt
        new_title = "Python LangGraph Cyclic Agents Power" 
        
    print(f"Generated Title: '{new_title}'")
    
    # LangGraph requires the node to return a dictionary defining how to update the state.
    return {"generation": new_title, "iterations": 1} 

def check_constraints(state: GraphState) -> GraphState:
    """
    Node B: Checks if the generated title meets the constraint (exactly 5 words).
    A node returns a state update, never a bare string; the decision it reaches is
    written into the state for the conditional edge to read.
    """
    print("--- Running Node B: Constraint Check ---")
    
    title = state['generation']
    word_count = len(title.split())
    
    print(f"Title: '{title}' | Word Count: {word_count}")
    
    # Define the constraint logic
    if word_count == 5:
        print("Constraint Met: Word count is 5. Exiting graph.")
        return {"decision": "end"}
    else:
        print(f"Constraint Failed: Expected 5 words, got {word_count}. Looping back.")
        return {"decision": "refine"}


def decide_next(state: GraphState) -> str:
    """The conditional edge: a pure function of the state, no side effects."""
    return state["decision"]

# --- 3. Construct the Graph ---

# Initialize the StateGraph with the defined state schema
workflow = StateGraph(GraphState)

# Add the nodes to the graph
workflow.add_node("generate", generate_title)
workflow.add_node("check", check_constraints)

# Set the initial entry point
workflow.set_entry_point("generate")

# Add the standard edge from generation to checking
workflow.add_edge("generate", "check")

# Add the CRITICAL conditional edge from the checker node
# The router reads state['decision'], written by 'check_constraints'.
workflow.add_conditional_edges(
    source="check",
    # The router reads the decision the node stored; LangGraph calls it after the
    # node returns, and its return value selects the next node.
    path=decide_next,
    # The dictionary mapping the function output to the next node name
    # 'refine' maps back to the 'generate' node, creating the loop.
    # 'end' maps to the special LangGraph constant END, stopping execution.
    # This dictionary defines the routing logic.
    path_map={
        "refine": "generate",  # Loop back
        "end": END             # Exit graph
    }
)

# Compile the graph into a runnable object
app = workflow.compile()

# --- 4. Execute the Graph ---

print("\n--- Starting Graph Execution ---")
initial_state = {"generation": "", "iterations": 0}

# The graph will run until it hits the END node.
final_state = app.invoke(initial_state)

print("\n--- Final State Achieved ---")
print(f"Final Title: {final_state['generation']}")
print(f"Total Iterations: {final_state['iterations']}")

# Optional: Display the graph structure using DOT language
# We use the built-in LangGraph method to visualize the flow.
try:
    from IPython.display import Image
    # Note: Requires 'pygraphviz' or 'pydot' installed for actual rendering
    # We will output the DOT structure for documentation purposes
    print("\n...")
except ImportError:
    pass # Skip visualization if dependencies are missing
