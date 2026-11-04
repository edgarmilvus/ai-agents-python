import json
import re

# --- Exercise 4: Interactive Challenge - Planning Layer for RAG ---

# 1. Planning Prompt Template (Simulated LLM Input)
PLANNING_PROMPT_TEMPLATE = """
As the Agent Planner, analyze the user query. Determine if the query requires external knowledge retrieval (RAG) or if it is a simple, direct question.
Output must be a JSON object with two keys:

1. "search_required": boolean (True if RAG is needed, False otherwise).
2. "refined_query": string (The optimized search query, or the original query if search is not needed).

User Query: {query}
"""

def simulate_llm_planning(user_query):
    """
    Simulates the LLM's Orient phase by parsing keywords and outputting structured JSON.
    """
    # Simple rule-based simulation of LLM intelligence
    query_lower = user_query.lower()
    
    if 'what is the capital' in query_lower or 'who is the ceo' in query_lower:
        # Simple factual query, no complex RAG needed
        search_required = False
        refined_query = user_query
    elif 'history of' in query_lower or 'technical specifications' in query_lower or 'compare and contrast' in query_lower:
        # Complex query likely requiring external knowledge
        search_required = True
        # Simple refinement: strip the introductory phrase that carries no
        # signal for the vector store, whatever its capitalisation.
        refined_query = re.sub(
            r"^what is the history of\s+", "", user_query, flags=re.IGNORECASE
        ).strip()
    else:
        # Default to search if uncertain
        search_required = True
        refined_query = user_query
        
    # Format output as if it came from the LLM based on the template
    planner_output = {
        "search_required": search_required,
        "refined_query": refined_query
    }
    
    print(f"[Planner Output Simulation]: {json.dumps(planner_output)}")
    return planner_output

def execute_rag(query):
    """
    Simulates the Act phase of the RAG system.
    """
    print(f"\n[RAG System Act] Performing semantic search using refined query: '{query}'...")
    print("...Retrieving relevant documents from vector store...")
    print("...Generating grounded response based on retrieved context...")
    return "RAG Result: Response successfully generated using external context."

def execute_direct_answer(query):
    """
    Simulates a direct, non-RAG response.
    """
    return f"Direct Answer Result: Answering simple query '{query}' using internal parametric knowledge."

def run_planning_agent(user_query):
    """
    Main agent loop incorporating the Planning/Orient step.
    """
    print(f"--- Agent Processing User Query: '{user_query}' ---")
    
    # 1. Orient/Decide Phase (Planning)
    planning_result = simulate_llm_planning(user_query)
    
    search_needed = planning_result['search_required']
    refined_query = planning_result['refined_query']
    
    # 2. Act Phase (Conditional Execution)
    if search_needed:
        print("\n[Decide] RAG is REQUIRED. Proceeding to execution.")
        final_response = execute_rag(refined_query)
    else:
        print("\n[Decide] RAG NOT required. Executing direct answer.")
        final_response = execute_direct_answer(user_query)
        
    print(f"\n--- Final Agent Action ---\n{final_response}")
    return final_response


if __name__ == "__main__":
    # Case A: Simple query (no RAG needed)
    run_planning_agent("What is the capital of France?")
    
    # Case B: Complex query (RAG needed)
    run_planning_agent("What is the history of the early development of Python's GIL?")
