# Reusing AGENT_WEIGHTS and calculate_weighted_consensus from Exercise 2

MAX_ITERATIONS = 5
SUCCESS_THRESHOLD = 8.0

def generate_artifact(revision_feedback: str, iteration: int) -> str:
    """Mock function for the Generator Agent creating or revising work."""
    print(f"\n[Iteration {iteration}] Generator Agent creating Artifact...")
    if iteration == 1:
        content = "Initial Draft: Functionality is 60% complete, focusing on speed."
    elif iteration == 2:
        content = f"Revision 1: Implemented error handling and addressed initial feedback.\nFeedback: {revision_feedback[:100]}..."
    elif iteration == 3:
        content = f"Revision 2: Implemented optimization and addressed remaining structural feedback.\nFeedback: {revision_feedback[:100]}..."
    else:
        content = f"Revision {iteration-1}: Final polish based on minor critiques.\nFeedback: {revision_feedback[:100]}..."
    return content

def run_critique_group(artifact: str, iteration: int) -> List[Tuple[str, AgentCritique]]:
    """Mock function for the Reviewer Group providing structured critiques."""
    
    # Simulate scores improving over time
    if iteration == 1:
        scores = [6, 7, 5]
        rationales = ["Missing error handling.", "Needs optimization.", "Incomplete features."]
        critical = True
    elif iteration == 2:
        scores = [7, 8, 6]
        rationales = ["Error handling added, but optimization is weak.", "Still needs speed improvement.", "Minor bugs remain."]
        critical = False
    elif iteration == 3:
        scores = [9, 8, 8]
        rationales = ["Optimization is excellent.", "Meets all requirements.", "Ready for deployment."]
        critical = False
    else: # High score for subsequent runs
        scores = [9, 10, 9]
        rationales = ["Perfect.", "Flawless.", "No issues found."]
        critical = False

    critiques = []
    agent_ids = list(AGENT_WEIGHTS.keys())
    for i, agent_id in enumerate(agent_ids):
        # Agent A sets the veto flag in iteration 1
        is_critical = critical and (agent_id == 'Agent_A') 
        
        critique = AgentCritique(
            score_out_of_10=scores[i],
            rationale_summary=rationales[i],
            suggested_refinement_steps=[f"Refinement step {i+1}"],
            critical_error_flag=is_critical
        )
        critiques.append((agent_id, critique))
    return critiques

def refinement_loop():
    """Implements the core iterative refinement process."""
    revision_feedback = "Initial task prompt."
    iteration = 0
    final_score = 0.0

    print("\n--- Exercise 3: Iterative Refinement Loop Start ---")

    while iteration < MAX_ITERATIONS:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")
        
        # 1. Generation/Revision
        current_artifact = generate_artifact(revision_feedback, iteration)

        # 2. Critique
        critiques = run_critique_group(current_artifact, iteration)

        # 3. Consensus 
        final_score, consolidated_rationale, veto = calculate_weighted_consensus(critiques, use_semantic_scoring=False)
        
        print(f"Consensus Result: Score={final_score:.2f}, Veto={veto}")

        # 4. Validation Check and Decision
        if veto or final_score < SUCCESS_THRESHOLD:
            if veto:
                print("Status: CRITICAL VETO. Revision required.")
            else:
                print(f"Status: Score {final_score:.2f} < Threshold {SUCCESS_THRESHOLD:.1f}. Revision required.")
            
            # Feedback Integration: Pass the consolidated rationale back for revision
            revision_feedback = consolidated_rationale
            
            if iteration == MAX_ITERATIONS:
                print("LOOP TERMINATED: Max iterations reached without success.")
                break
        else:
            print("Status: SUCCESS! Artifact meets consensus threshold.")
            break
    
    print(f"\n--- Loop Finished. Final Score: {final_score:.2f} (Iterations: {iteration}) ---")

# Run the loop
refinement_loop()
