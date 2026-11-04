from pydantic import BaseModel, Field
from typing import List, Dict, Any
import random
import json # Used to conceptually represent structured LLM output

# --- 1. DEFINITIONS AND STRUCTURED OUTPUT SCHEMA ---

class Critique(BaseModel):
    """
    Pydantic schema defining the mandatory structure for agent feedback.
    This ensures all critique agents return standardized, parseable data.
    """
    criterion_name: str = Field(description="The specific dimension being evaluated (e.g., Clarity, Impact).")
    score_out_of_10: int = Field(description="The numerical score given to the input, constrained between 1 and 10.")
    refinement_suggestion: str = Field(description="Specific, actionable advice for improving the input based on this criterion.")

# Define the specialized criteria and their associated weights for consensus
CRITERIA_WEIGHTS = {
    # Impact is the most critical factor for a marketing headline, hence the highest weight.
    "Impact": 5,   
    "Clarity": 3,  
    "SEO_Potential": 2 
}
TOTAL_WEIGHT = sum(CRITERIA_WEIGHTS.values())

# --- 2. AGENT SIMULATION FUNCTIONS ---

def generate_mock_critique(headline: str, criterion: str, weight: int) -> Critique:
    """
    Simulates a specialized Critique Agent using an LLM configured for structured output.
    The function generates a Pydantic object based on the input headline and criterion.
    """
    # In a real system, the prompt would instruct the LLM: 
    # "Evaluate the headline against the '{criterion}' metric and output the result 
    # strictly in the provided JSON schema."
    
    # Simulate score generation and slight score adjustment based on input complexity
    base_score = random.randint(5, 10)
    score = max(1, min(10, base_score - (len(headline) // 20))) 

    # Generate mock advice specific to the criterion
    if criterion == "Clarity":
        advice = "The structure is too verbose. Focus on a single, compelling action verb."
    elif criterion == "Impact":
        advice = f"The headline lacks emotional punch. Highlight the pain point solved by '{headline.split()[0]}'."
    else: # SEO_Potential
        advice = "Ensure that high-value, long-tail search terms are integrated naturally without sounding robotic."
        
    # Return the validated Pydantic object
    return Critique(
        criterion_name=criterion,
        score_out_of_10=score,
        refinement_suggestion=advice
    )

# --- 3. CONSENSUS AND SYNTHESIS MECHANISM ---

def calculate_weighted_consensus(critiques: List[Critique]) -> Dict[str, Any]:
    """
    Applies the weighted voting algorithm (Majority Rule variant) to aggregate scores 
    and synthesize refinement advice from the parallel critique agents.
    """
    total_weighted_score = 0
    all_suggestions = []
    
    # Calculate the weighted score
    for critique in critiques:
        criterion = critique.criterion_name
        # Retrieve the predefined weight for the current criterion
        weight = CRITERIA_WEIGHTS.get(criterion, 0) 
        
        # Core Consensus Calculation: Score * Weight
        total_weighted_score += (critique.score_out_of_10 * weight)
        
        # Collect structured feedback for later synthesis
        all_suggestions.append(f"[{criterion} Agent]: Score {critique.score_out_of_10}/10. Suggestion: {critique.refinement_suggestion}")
        
    # Calculate the final normalized score (Total Weighted Score / Total Possible Weight)
    final_normalized_score = total_weighted_score / TOTAL_WEIGHT
    
    # Synthesize the final advice into a single block for the Refinement Agent
    synthesized_advice = "\n".join(all_suggestions)
    
    return {
        "final_score": round(final_normalized_score, 2),
        "raw_weighted_score": total_weighted_score,
        "synthesized_advice": synthesized_advice
    }

# --- 4. MAIN EXECUTION FLOW (ITERATIVE REFINEMENT SIMULATION) ---

def run_critique_cycle(headline: str, cycle_num: int) -> Dict[str, Any]:
    """
    Orchestrates the parallel critique, consensus calculation, and reporting for one cycle.
    """
    print(f"\n{'='*50}\n--- Starting Critique Cycle {cycle_num} ---")
    print(f"INPUT HEADLINE: '{headline}'")
    
    # 4.1. Parallel Critique Generation (Agent Pool Execution)
    critiques = []
    for criterion, weight in CRITERIA_WEIGHTS.items():
        # Each criterion triggers an independent, specialized agent evaluation
        critique_obj = generate_mock_critique(headline, criterion, weight)
        critiques.append(critique_obj)
        print(f"  [Critique Generated] {criterion} Agent rated: {critique_obj.score_out_of_10}/10")

    # 4.2. Consensus Calculation
    consensus_result = calculate_weighted_consensus(critiques)
    
    print(f"\n  >> Consensus Score (Weighted): {consensus_result['final_score']}/10.0")
    
    return consensus_result

# --- 5. INITIALIZATION AND RUNTIME ---

if __name__ == "__main__":
    # Initial Draft (Simulated output from a Generation Agent)
    initial_headline = "A novel system utilizing large language models for automated code review and quality assurance."
    
    # --- Iteration 1 ---
    result_1 = run_critique_cycle(initial_headline, 1)
    
    # --- Iterative Refinement Loop Check ---
    # The refinement loop is triggered if the consensus score is below the acceptance threshold (e.g., 7.5)
    ACCEPTANCE_THRESHOLD = 7.5
    
    if result_1['final_score'] < ACCEPTANCE_THRESHOLD:
        print(f"\n[Refinement Triggered] Score {result_1['final_score']} is below {ACCEPTANCE_THRESHOLD}. Generating new draft...")
        
        # In a real system, a dedicated Synthesis Agent would use the 'synthesized_advice' 
        # and the original headline as input to an LLM prompt to generate the next draft.
        
        # Simulate LLM refinement based on the consolidated advice:
        new_headline = "Stop wasting time debugging. Our AI Agent reviews your code 10x faster and finds critical errors automatically."
        print(f"\n--- Synthesis Agent Output ---\nNEW DRAFT: '{new_headline}'")
        
        # --- Iteration 2 (Refinement Loop) ---
        result_2 = run_critique_cycle(new_headline, 2)
        
        print(f"\n{'='*50}")
        print("--- Final Validation ---")
        if result_2['final_score'] >= ACCEPTANCE_THRESHOLD:
            print(f"SUCCESS: Final headline validated with a consensus score of {result_2['final_score']}.")
        else:
            print(f"FAILURE: Score {result_2['final_score']} is still too low. Further refinement needed.")
            
        print("\nConsolidated Refinement Advice from Cycle 2:\n" + result_2['synthesized_advice'])
        
    else:
        print(f"\nSUCCESS: Initial draft validated with a score of {result_1['final_score']}.")
