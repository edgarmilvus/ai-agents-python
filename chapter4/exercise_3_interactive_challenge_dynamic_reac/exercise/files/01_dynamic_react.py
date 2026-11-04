import textwrap
from typing import List, Callable

# 1. Define Simulated Search Tool
def search_web(query: str) -> str:
    """Simulates a web search result, intentionally poor on the first specific query."""
    
    if "initial complex query" in query.lower():
        # 3. Simulated Low-Quality Observation
        return "Observation: No direct match found for the complex query. Try simplifying or refining the scope."
    
    if "refined specific impact of 2024" in query.lower():
        # High-Quality Observation after refinement
        return textwrap.dedent("""
        Observation: The 2024 EU AI Act introduces mandatory risk assessments for SMEs 
        using high-risk AI models. This will lead to an estimated 15-25% increase in 
        compliance overhead, primarily impacting development timelines and legal costs. 
        General consensus suggests smaller firms may shift to lower-risk, pre-certified models.
        (Total characters: 350+)
        """)
        
    return "Observation: Generic search result."

# 2. Prompt Modification for Self-Correction
SELF_CORRECTION_PROMPT = textwrap.dedent("""
You are a research agent. Your goal is to find the specific economic impact of the 2024 EU AI Act on small-to-medium enterprises (SMEs).
You MUST follow the ReAct pattern (Thought, Action, Observation).

CRITICAL RULE: Observation Quality Check
After receiving an Observation, you MUST evaluate its quality. An observation is insufficient if:

1. It contains fewer than 100 characters.
2. OR it contains the phrase 'No direct match found'.

If the observation is insufficient, your next Thought MUST start with the phrase 'REFINEMENT_NEEDED:' and propose a more specific query for the next Action.
""")

# 4. Verification (Simulated Trace)
def simulate_self_correction_trace(tool: Callable):
    print("--- Starting ReAct Self-Correction Trace ---")
    
    # --- STEP 1: Initial Attempt (Leads to poor observation) ---
    print("\n--- STEP 1: Initial Search ---")
    
    thought_1 = "I need to start with a broad, complex query to gauge the available data."
    action_1 = "search_web('economic impact of the 2024 EU AI Act on small-to-medium enterprises')"
    observation_1 = tool(action_1.split("'")[1])
    
    print(f"Thought: {thought_1}")
    print(f"Action: {action_1}")
    print(f"Observation: {observation_1}")
    
    # --- STEP 2: Self-Correction Loop Triggered by Observation Quality ---
    print("\n--- STEP 2: Quality Check and Refinement ---")
    
    # Check Observation 1 against the rule
    if len(observation_1) < 100 or "No direct match found" in observation_1:
        print("-> [AGENT INTERNAL CHECK]: Observation is insufficient. Triggering refinement.")
        
        # Self-Correction Thought
        thought_2 = "REFINEMENT_NEEDED: The initial query was too broad and returned no direct match. I need to refine the query to focus specifically on the compliance and cost implications of the 2024 Act on SMEs."
        action_2 = "search_web('refined specific impact of 2024 EU AI Act compliance costs on SMEs')"
        
        print(f"Thought: {thought_2}")
        print(f"Action: {action_2}")
        
        # New, Refined Observation
        observation_2 = tool(action_2.split("'")[1])
        print(f"Observation: {observation_2}")
        
        # --- STEP 3: Final Answer based on High-Quality Data ---
        print("\n--- STEP 3: Synthesis and Answer ---")
        final_thought = "The refined observation provides high-quality data regarding compliance overhead and shifts in model usage. I can now synthesize the final answer."
        final_answer = "Answer: The primary economic impact on SMEs is an estimated 15-25% increase in compliance overhead due to mandatory risk assessments, leading smaller firms to favor lower-risk AI solutions."
        
        print(f"Thought: {final_thought}")
        print(final_answer)
        
    else:
        print("Observation was sufficient. Proceeding to answer.")

simulate_self_correction_trace(search_web)
