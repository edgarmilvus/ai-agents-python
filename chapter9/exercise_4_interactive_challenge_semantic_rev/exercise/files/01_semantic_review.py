# Reusing AGENT_WEIGHTS and AgentCritique

# 1. Define Target Vector
TARGET_TASK_VECTOR = [0.8, 0.1, 0.7, 0.2] 

def get_embedding(text: str) -> List[float]:
    """
    Mock function simulating an embedding model call. 
    Generates vectors based on keywords to simulate relevance.
    """
    # High relevance to TARGET_TASK_VECTOR (focus on optimization/performance)
    if "optimization" in text or "latency" in text:
        return [0.75, 0.15, 0.8, 0.1]
    # Low relevance (focus on superficial aspects like UI/design)
    if "color scheme" in text or "font" in text:
        return [0.05, 0.9, 0.1, 0.9]
    # Moderate relevance 
    if "structure" in text or "error handling" in text:
        return [0.5, 0.3, 0.6, 0.4]
    return [0.4, 0.4, 0.4, 0.4] # Default

# 2. Similarity Function (Cosine Similarity)
def calculate_semantic_similarity(vector_a: List[float], vector_b: List[float]) -> float:
    """
    Calculates cosine similarity between two vectors.
    """
    if len(vector_a) != len(vector_b):
        return 0.0

    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    magnitude_a = sum(a**2 for a in vector_a)**0.5
    magnitude_b = sum(b**2 for b in vector_b)**0.5

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
    
    similarity = dot_product / (magnitude_a * magnitude_b)
    
    # Clamp similarity between 0 and 1
    return max(0.0, min(1.0, similarity))

# The core logic for weight adjustment (Requirement 3) is integrated into 
# calculate_weighted_consensus (defined in Exercise 2, used here with TARGET_TASK_VECTOR).

# --- 4. Demonstration ---
print("\n--- Exercise 4 Demonstration: Semantic Scoring ---")

# Agent A: High Base Weight (3.0), High relevance (Optimization) -> Amplified influence
critique_a_sem = AgentCritique(
    score_out_of_10=9, rationale_summary="Excellent optimization strategy, minimal latency found.", 
    suggested_refinement_steps=["Check memory allocation."], critical_error_flag=False
)
# Agent B: Low Base Weight (1.5), Low relevance (Color scheme) -> Reduced influence
critique_b_sem = AgentCritique(
    score_out_of_10=7, rationale_summary="The documentation uses a poor color scheme and font choices.", 
    suggested_refinement_steps=["Change font to serif."], critical_error_flag=False
)
# Agent C: Medium Base Weight (2.5), Moderate relevance (Structure)
critique_c_sem = AgentCritique(
    score_out_of_10=8, rationale_summary="General structure is good, but error handling needs hardening.", 
    suggested_refinement_steps=["Add try/except blocks."], critical_error_flag=False
)

critiques_ex4 = [
    ('Agent_A', critique_a_sem),
    ('Agent_B', critique_b_sem),
    ('Agent_C', critique_c_sem),
]

# Calculate consensus without semantic scoring (Base Weights)
# Result should be 8.21 (from Ex 2 calculation)
base_score, _, _ = calculate_weighted_consensus(critiques_ex4, use_semantic_scoring=False)
print(f"Base Consensus Score (No Semantic Adjustment): {base_score:.2f}")

# Calculate consensus WITH semantic scoring (Adjusted Weights)
adjusted_score, rationale, veto = calculate_weighted_consensus(
    critiques_ex4, 
    use_semantic_scoring=True, 
    task_vector=TARGET_TASK_VECTOR
)
print(f"Adjusted Consensus Score (Semantic Boosted): {adjusted_score:.2f}")
# Expected: Adjusted score should be higher than 8.21 because Agent A (score 9) received a high boost.
