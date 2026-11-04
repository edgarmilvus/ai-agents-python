# Reusing AgentCritique from Exercise 1

# 1. Define Agent Weights
AGENT_WEIGHTS: Dict[str, float] = {
    'Agent_A': 3.0,  # Senior
    'Agent_B': 1.5,  # Junior
    'Agent_C': 2.5   # Mid-Level
}

def calculate_weighted_consensus(
    critiques_with_ids: List[Tuple[str, AgentCritique]], 
    use_semantic_scoring: bool = False,
    # Placeholder for Ex 4 integration
    TARGET_TASK_VECTOR: Optional[List[float]] = None
) -> Tuple[float, str, bool]:
    """
    Calculates the final consensus score and synthesizes rationale using weights.
    Returns: (Consensus Score, Consolidated Rationale, Critical Veto Status)
    """
    total_weighted_score = 0.0
    total_weight = 0.0
    critical_veto = False
    
    weighted_critiques = []

    # 1. Calculate Adjusted Weights (Handles Ex 4 logic if enabled) and Check Veto
    for agent_id, critique in critiques_with_ids:
        base_weight = AGENT_WEIGHTS.get(agent_id, 1.0)
        current_weight = base_weight
        
        critique_data = critique.dict()
        
        # 5. Critical Flag Resolution (Veto)
        if critique_data.get('critical_error_flag', False):
            critical_veto = True
            
        # Semantic Scoring (Integrated for completeness, Ex 4 logic)
        if use_semantic_scoring and TARGET_TASK_VECTOR:
            rationale_text = critique_data.get('rationale_summary', '')
            rationale_vector = get_embedding(rationale_text)
            similarity = calculate_semantic_similarity(rationale_vector, TARGET_TASK_VECTOR)
            current_weight = base_weight * (1 + similarity)
            # print(f"  [Weighted Consensus] {agent_id}: Adjusted Weight={current_weight:.2f}") # Suppressed for Ex 2 demo

        weighted_critiques.append({
            'agent_id': agent_id,
            'score': critique_data['score_out_of_10'],
            'weight': current_weight,
            'rationale': critique_data['rationale_summary'],
            'refinements': critique_data['suggested_refinement_steps']
        })
        
        total_weighted_score += critique_data['score_out_of_10'] * current_weight
        total_weight += current_weight

    # Handle Veto
    if critical_veto:
        return 0.0, "CRITICAL VETO: One or more agents flagged a blocking error.", True

    # 3. Weighted Score Calculation
    if total_weight == 0:
        return 0.0, "No critiques provided.", False
        
    consensus_score = total_weighted_score / total_weight

    # 4. Rationale Synthesis
    consolidated_rationales = [f"Consensus Score: {consensus_score:.2f}/10.0\n--- Consolidated Feedback ---"]
    
    # Determine the average weight for filtering high-priority rationales
    avg_weight = total_weight / len(weighted_critiques) if weighted_critiques else 0

    # Prioritize rationales from agents whose weight is above average
    prioritized_rationales = sorted(weighted_critiques, key=lambda x: x['weight'], reverse=True)
    
    for item in prioritized_rationales:
        if item['weight'] >= avg_weight:
            consolidated_rationales.append(
                f"[{item['agent_id']} (Weight: {item['weight']:.2f})]: {item['rationale']}"
            )
            for step in item['refinements']:
                consolidated_rationales.append(f"  - Refinement: {step}")

    return consensus_score, "\n".join(consolidated_rationales), False

# --- Demonstration ---

# 2. Input Data Structure (Simulated Critiques)
critique_a = AgentCritique(
    score_out_of_10=9, rationale_summary="Code is highly efficient.", 
    suggested_refinement_steps=["Check license."], critical_error_flag=False
)
critique_b = AgentCritique(
    score_out_of_10=7, rationale_summary="Documentation is confusing.", 
    suggested_refinement_steps=["Rewrite README."], critical_error_flag=False
)
critique_c = AgentCritique(
    score_out_of_10=2, rationale_summary="Major security flaw detected.", 
    suggested_refinement_steps=["Patch immediately."], critical_error_flag=True # Veto
)

critiques_ex2_veto = [
    ('Agent_A', critique_a),
    ('Agent_B', critique_b),
    ('Agent_C', critique_c),
]

# Case 1: Veto Scenario
print("\n--- Exercise 2 Demonstration: Veto ---")
score_veto, rationale_veto, veto_status = calculate_weighted_consensus(critiques_ex2_veto)
print(f"Consensus Score: {score_veto:.2f}. Veto Status: {veto_status}")
print(f"Rationale: {rationale_veto}")

# Case 2: Standard Weighted Consensus (No Veto)
critiques_ex2_standard = [
    ('Agent_A', critique_a), # Score 9, Weight 3.0
    ('Agent_B', critique_b), # Score 7, Weight 1.5
    ('Agent_C', AgentCritique(score_out_of_10=8, rationale_summary="Good structure.", suggested_refinement_steps=["Test coverage."], critical_error_flag=False)), # Score 8, Weight 2.5
]
# Weighted Average: ((9*3.0) + (7*1.5) + (8*2.5)) / (3.0 + 1.5 + 2.5) = (27 + 10.5 + 20) / 7.0 = 57.5 / 7.0 = 8.21
print("\n--- Exercise 2 Demonstration: Standard Consensus ---")
score_standard, rationale_standard, _ = calculate_weighted_consensus(critiques_ex2_standard)
print(f"Consensus Score: {score_standard:.2f}")
print(f"Rationale Synthesis (Prioritizing Agents A & C): \n{rationale_standard}")
