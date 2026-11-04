import os
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from operator import itemgetter
from langchain_openai import ChatOpenAI

# --- 1. Define the Custom Graph State Schema ---

class ResearchState(TypedDict):
    """
    Represents the state of the research process.
    """
    query: str
    result: str
    iteration_count: int
    needs_refinement: bool
    max_iterations: int

# --- 2. Initialize LLM and Mock Tools ---

# Initialize the LLM; endpoint, model and key come from the environment.
BASE_URL = os.environ.get("OPENAI_COMPATIBLE_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("OPENAI_COMPATIBLE_MODEL", "~deepseek/deepseek-flash-latest")
llm = ChatOpenAI(
    temperature=0.1,
    model=MODEL,
    base_url=BASE_URL,
    api_key=os.environ.get("OPENAI_COMPATIBLE_API_KEY"),
)

def mock_search_engine(query: str) -> str:
    """Simulates an external search tool with varying detail."""
    print(f"--- TOOL: Searching for: '{query[:40]}...'")
    if "Apollo 11 mission goals" in query:
        return "The primary goal of Apollo 11 was to land humans on the Moon and return them safely to Earth. This achieved President Kennedy's 1961 national goal. Secondary goals included scientific exploration."
    elif "specific scientific instruments used on Apollo 11" in query:
        return "Apollo 11 carried several scientific instruments, including the Passive Seismic Experiment Package (PSEP) and the Laser Ranging Retroreflector (LRRR). These were deployed by the astronauts."
    else:
        return "Apollo 11 was a NASA mission that launched in 1969."

# --- 3. Define the Graph Nodes (Functions) ---

def researcher_node(state: ResearchState) -> ResearchState:
    """Node 1: Executes the search query using the tool."""
    current_query = state["query"]
    search_result = mock_search_engine(current_query)
    
    # Update state with the new result and increment iteration count
    return {
        "result": search_result,
        "iteration_count": state["iteration_count"] + 1
    }

def verifier_node(state: ResearchState) -> ResearchState:
    """Node 2: Verifies if the current result is satisfactory."""
    
    # Check for maximum iteration limit before verification
    if state["iteration_count"] >= state["max_iterations"]:
        print(f"\n--- VERIFIER: Max iterations reached ({state['max_iterations']}). Ending loop.")
        return {"needs_refinement": False} # Force exit
        
    prompt = f"""
    CRITICAL VERIFICATION TASK:
    Original Query: {state['query']}
    Current Research Result: {state['result']}
    
    Based ONLY on the Current Research Result, is the answer detailed and complete enough 
    to fully satisfy the Original Query? 
    
    If the answer is too brief, generic, or misses key details implied by the query, 
    respond with 'YES_REFINE'. Otherwise, if the answer is complete and satisfactory, 
    respond with 'NO_COMPLETE'.
    """
    
    response = llm.invoke([HumanMessage(content=prompt)]).content.strip().upper()
    
    if "YES_REFINE" in response:
        print("--- VERIFIER: Result is too generic. Needs refinement.")
        return {"needs_refinement": True}
    else:
        print("--- VERIFIER: Result is satisfactory. Exiting.")
        return {"needs_refinement": False}

def refiner_node(state: ResearchState) -> ResearchState:
    """Node 3: Generates a new, more specific query if refinement is needed."""
    
    prompt = f"""
    REFINEMENT TASK:
    Original Query: {state['query']}
    Previous Result (Insufficient): {state['result']}
    
    The previous result was too generic. Based on the original query and the insufficient result, 
    generate a NEW, highly specific follow-up query that will likely yield a more detailed answer. 
    
    Example: If the query was 'What is Python?' and the result was 'A programming language,' 
    a new query might be: 'Specific differences between Python 2 and 3 syntax.'
    
    Output ONLY the new, refined search query (max 10 words).
    """
    
    new_query = llm.invoke([HumanMessage(content=prompt)]).content.strip().replace('"', '')
    print(f"--- REFINER: New refined query generated: '{new_query}'")
    
    # Update state with the new query. The result is cleared for the next search.
    return {"query": new_query, "result": ""}

# --- 4. Define the Conditional Edge Logic ---

def check_refinement(state: ResearchState) -> str:
    """Determines the next step based on the needs_refinement flag."""
    if state["needs_refinement"]:
        return "refine"
    else:
        return "complete"

# --- 5. Build and Run the Graph ---

# Define the graph structure
workflow = StateGraph(ResearchState)

# Add nodes
workflow.add_node("researcher", researcher_node)
workflow.add_node("verifier", verifier_node)
workflow.add_node("refiner", refiner_node)

# Set the entry point
workflow.set_entry_point("researcher")

# Define edges
workflow.add_edge("researcher", "verifier")

# Define the conditional edge (The Cycle)
workflow.add_conditional_edges(
    "verifier",
    check_refinement,
    {
        "refine": "refiner",   # Loop back to refiner
        "complete": END        # Exit the graph
    }
)

# Define the cyclic edge
workflow.add_edge("refiner", "researcher") # Refined query goes back to researcher

# Compile the graph
app = workflow.compile()

# --- 6. Execute the Agent ---

initial_state = {
    "query": "What were the Apollo 11 mission goals and the scientific instruments used?",
    "result": "",
    "iteration_count": 0,
    "needs_refinement": True, # Initial assumption is that we need to start
    "max_iterations": 3
}

print("--- STARTING AGENT EXECUTION ---")
print(f"Initial Query: {initial_state['query']}")

# Run the graph
final_state = app.invoke(initial_state)

print("\n--- FINAL RESULT ---")
print(f"Total Iterations: {final_state['iteration_count']}")
print(f"Final Research Result:\n{final_state['result']}")
