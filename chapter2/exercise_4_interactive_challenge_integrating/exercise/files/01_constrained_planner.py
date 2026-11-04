import json
from typing import List, Dict, Any, Optional

# --- Boilerplate Components Used ---
# PlanStepCounter, BaseTool

# Define the system constraint
MAX_PLAN_STEPS = 4

# --- Agent Simulation ---
def constrained_planning_agent(query: str, step_counter_tool: PlanStepCounter, llm: 'MockLLM'):
    """Simulates the ReAct loop with a planning constraint check."""
    
    # 0. System Prompt (The guiding constraint)
    system_constraint = (
        f"CRITICAL RULE: You must never execute a plan that requires more than {MAX_PLAN_STEPS} steps. "
        "If your initial thought process suggests 5 or more distinct actions (including tool calls and synthesis), "
        "you MUST call the PlanStepCounter tool to verify, and if the count is > 4, you MUST enter a reflection step (Thought 2) to simplify the plan before proceeding."
    )
    
    print(f"System Constraint: {system_constraint}")
    print(f"\nUser Query: {query}")
    print("--------------------------------------------------")

    # --- Iteration 1: Initial Planning ---
    
    # Thought 1: Agent attempts to decompose the complex task
    initial_plan_text = """
    Thought 1: This is a complex query requiring multiple distinct steps.

    1. Research Strategy A and gather historical data (Tool: ResearchDB).
    2. Research Strategy B and gather historical data (Tool: ResearchDB).
    3. Research Strategy C and gather historical data (Tool: ResearchDB).
    4. Compare the historical returns for A, B, and C (Tool: ComparisonEngine).
    5. Draft the summary email to the manager (Tool: EmailComposer).
    """
    print(initial_plan_text)

    # Action 1: Check the constraint
    action_1 = f"Action: PlanStepCounter(plan_text='{initial_plan_text}')"
    print(action_1)
    
    # Observation 1: Tool execution
    step_count = step_counter_tool.run(initial_plan_text)
    print(f"Observation 1: Plan complexity count is {step_count}.")
    
    # --- Iteration 2: Constraint Check and Correction ---
    
    if step_count > MAX_PLAN_STEPS:
        print(f"\n[CONSTRAINT VIOLATION]: Count ({step_count}) > Max Steps ({MAX_PLAN_STEPS}). Triggering Self-Correction.")
        
        # Thought 2: Agent reflects and simplifies the plan
        simplified_plan_text = """
        Thought 2 (Reflection and Simplification): The initial plan had 5 steps, violating the critical rule (Max 4 steps). I must combine the research phase to meet the constraint.
        
        Revised Final Plan:

        1. Consolidated Research: Research all three strategies (A, B, C) and gather comparison data in one unified step (Tool: ResearchDB).
        2. Comparison and Analysis: Calculate and compare historical returns (Tool: ComparisonEngine).
        3. Draft Summary: Synthesize findings and draft the summary email (Tool: EmailComposer).
        """
        
        print(simplified_plan_text)
        
        # Final Action: Proceed with the simplified plan (or call the counter again to confirm)
        print("Final Action: Proceeding with the 3-step Revised Final Plan.")
        return simplified_plan_text
    else:
        print("\nAction: Proceeding with execution of the initial plan.")
        return initial_plan_text


# --- Execution Demonstration ---

# 1. Initialize Components
step_counter = PlanStepCounter()
mock_llm = MockLLM()

# 2. Complex Query designed to fail the constraint
complex_query = "Research three different investment strategies, compare their historical returns over the last decade, and draft a summary email to my manager."

# 3. Run the constrained agent
final_plan = constrained_planning_agent(complex_query, step_counter, mock_llm)

print("\n=============================================")
print("Agent successfully generated the following plan after correction:")
print(final_plan)
