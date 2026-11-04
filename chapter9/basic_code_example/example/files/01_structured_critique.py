from pydantic import BaseModel, Field, ValidationError
from typing import List, Dict, Any

# --- 1. Pydantic Schema Definition ---

class CritiqueFeedback(BaseModel):
    """
    Standardized structure for agent critique feedback. 
    Enforces required fields and data types for reliable consensus calculation.
    """
    reviewer_id: str = Field(..., description="Unique identifier for the reviewing agent.")
    score: int = Field(..., ge=1, le=5, description="Quality score from 1 (poor) to 5 (excellent).")
    pass_fail: bool = Field(..., description="The definitive verdict: True for Pass, False for Fail.")
    justification: str = Field(..., description="Detailed explanation for the score and verdict.")

# --- 2. Simulated Agent Outputs ---

def generate_slogan() -> str:
    """Simulates the output of a Generator Agent."""
    return "Python Agents: Automating the Future, One Loop at a Time."

def get_raw_critiques(work_product: str) -> List[Dict[str, Any]]:
    """
    Simulates raw, unstructured (but intended) dictionary outputs from three Reviewer Agents.
    Note: Agent Beta intentionally generates a 'Fail' verdict.
    """
    print(f"--- Critiquing Work: '{work_product[:30]}...' ---")
    return [
        # Agent Alpha: Positive Review (Pass)
        {"reviewer_id": "Alpha", "score": 4, "pass_fail": True,
         "justification": "Clear, concise, and hits the key theme of automation."},
        # Agent Beta: Negative Review (Fail)
        {"reviewer_id": "Beta", "score": 2, "pass_fail": False,
         "justification": "The phrasing 'One Loop at a Time' is slightly clunky and redundant."},
        # Agent Gamma: Strong Positive Review (Pass)
        {"reviewer_id": "Gamma", "score": 5, "pass_fail": True,
         "justification": "Excellent synthesis of technical focus and future vision. Highly effective."},
        # Agent Delta: Invalid Data (Simulating a generation error or hallucination)
        {"reviewer_id": "Delta", "score": 10, "pass_fail": True,
         "justification": "This critique will fail validation due to the score being out of range (1-5)."}
    ]

# --- 3. Core Consensus Logic and Validation ---

def determine_consensus(raw_critiques: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validates critiques using Pydantic, filters invalid data, and calculates the majority consensus.
    """
    validated_critiques: List[CritiqueFeedback] = []
    validation_errors: List[Dict[str, Any]] = []

    # 3a. Iterative Validation
    for raw_data in raw_critiques:
        try:
            # Pydantic attempts to parse and validate the raw dictionary
            critique = CritiqueFeedback(**raw_data)
            validated_critiques.append(critique)
        except ValidationError as e:
            # If validation fails (e.g., missing field, wrong type, score out of bounds)
            validation_errors.append({"data": raw_data, "error": str(e)})

    # 3b. Consensus Calculation (Majority Rule)
    total_reviewers = len(validated_critiques)
    if total_reviewers == 0:
        return {"status": "Failure", "message": "No valid critiques received."}

    # Use a generator expression within sum() for efficient counting of 'True' verdicts
    pass_votes = sum(1 for c in validated_critiques if c.pass_fail)
    fail_votes = total_reviewers - pass_votes

    # Majority check: If Pass votes strictly exceed Fail votes
    final_verdict = pass_votes > fail_votes
    
    return {
        "status": "Success",
        "final_verdict_pass": final_verdict,
        "pass_count": pass_votes,
        "fail_count": fail_votes,
        "total_valid_reviews": total_reviewers,
        "validation_failures": validation_errors,
        "validated_data": validated_critiques
    }

# --- 4. Execution Block ---

if __name__ == "__main__":
    # 4a. Execute the pipeline
    product = generate_slogan()
    raw_feedback = get_raw_critiques(product)
    consensus_result = determine_consensus(raw_feedback)

    # 4b. Display Results
    print("\n" + "="*70)
    print("AGENT CONSENSUS REPORT: Structured Critique and Majority Rule")
    print("="*70)
    
    if consensus_result["status"] == "Success":
        verdict_str = "PASSED" if consensus_result["final_verdict_pass"] else "FAILED"
        print(f"Work Product: {product}")
        print(f"\nFINAL VERDICT: {verdict_str}")
        print(f"Consensus Result: {consensus_result['pass_count']} Pass votes vs. {consensus_result['fail_count']} Fail votes.")
        
        print("\n--- Individual Valid Critiques ---")
        # Iterate over the validated Pydantic models
        for critique in consensus_result["validated_data"]:
            verdict = "PASS" if critique.pass_fail else "FAIL"
            print(f"  [{critique.reviewer_id}]: Score {critique.score}/5, Verdict: {verdict}")
            print(f"    Justification: {critique.justification}")
        
        if consensus_result["validation_failures"]:
            print("\n--- WARNING: Validation Failures Encountered ---")
            # Iterate over the raw data that failed validation
            for failure in consensus_result["validation_failures"]:
                print(f"  Invalid Agent Data: {failure['data']}")
                # Display only the first line of the complex Pydantic error trace for clarity
                print(f"  Error Detail: {failure['error'].splitlines()[0]}...")
    else:
        print(f"Error: {consensus_result['message']}")
