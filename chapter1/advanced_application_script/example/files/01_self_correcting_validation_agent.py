import time
from typing import Any, Dict, List

from langchain_core.tools import tool
from pydantic import BaseModel, Field

# --- 1. Pydantic Schemas for Structured Agent Communication ---

class ProjectProposal(BaseModel):
    """Defines the expected output structure for a valid project proposal."""
    title: str = Field(description="The concise and descriptive title of the project.")
    description: str = Field(description="The detailed description, adhering to length requirements.")

class AgentDecision(BaseModel):
    """The structured output the simulated LLM uses to decide the next action."""
    action: str = Field(description="The next tool to use: 'validate' or 'correct'.")
    context: str = Field(description="Summary of the current state and why this action was chosen.")
    
# --- 2. Tool Definitions (External Capabilities) ---

@tool
def validate_project_rules(proposal: ProjectProposal) -> Dict[str, Any]:
    """
    Tool 1: Checks if the proposal adheres to strict length and content rules.
    Returns a status dictionary indicating success or failure and the reason.
    """
    title_len = len(proposal.title)
    desc_len = len(proposal.description)
    
    # Define rules
    MIN_TITLE = 10
    MAX_TITLE = 50
    MIN_DESC = 100
    
    errors = []
    
    if not (MIN_TITLE <= title_len <= MAX_TITLE):
        errors.append(f"Title length ({title_len}) is outside the required range ({MIN_TITLE}-{MAX_TITLE}).")
    
    if desc_len < MIN_DESC:
        errors.append(f"Description length ({desc_len}) is too short. Minimum required is {MIN_DESC}.")
        
    if errors:
        return {"status": "FAILURE", "report": errors}
    else:
        return {"status": "SUCCESS", "report": "Proposal meets all validation criteria."}

@tool
def generate_correction_plan(current_proposal: Dict[str, str], error_report: List[str]) -> ProjectProposal:
    """
    Tool 2: Simulates the LLM generating a new, corrected proposal based on the errors.
    In a real system, this would be an LLM call instructed to fix the input.
    """
    print(f"\n[Tool 2: Planning Correction] Attempting to fix input...")
    time.sleep(0.5) # Simulate processing time

    # Mock correction logic based on observed errors
    original_title = current_proposal['title']
    original_desc = current_proposal['description']

    # Simple correction strategy: truncate/pad
    new_title = original_title[:50] if len(original_title) > 50 else original_title + " (Revised)"
    new_desc = original_desc + " " + "This section was added to meet the minimum length requirement for the project description, demonstrating the agent's ability to self-correct based on observed failures."
    
    return ProjectProposal(title=new_title, description=new_desc)

# --- 3. The Agentic Loop (OODA Implementation) ---

def mock_llm_decision_maker(current_state: Dict[str, Any]) -> AgentDecision:
    """
    Simulates the LLM's 'Orient' and 'Decide' phases, choosing the next tool.
    This replaces a complex prompt engineering step.
    """
    if current_state['status'] == 'GOAL_MET':
        return AgentDecision(action='terminate', context="Goal reached: Proposal is validated.")
    
    if current_state['status'] == 'INITIAL' or current_state['status'] == 'CORRECTED':
        return AgentDecision(action='validate', context="New input received or correction applied. Must check rules.")
        
    if current_state['status'] == 'FAILED_VALIDATION':
        return AgentDecision(action='correct', context="Validation failed. Need to use the planning tool to generate a conforming input.")
        
    # Default fallback
    return AgentDecision(action='terminate', context="Unknown state, terminating execution.")


def run_validation_agent(initial_proposal: Dict[str, str], max_iterations: int = 3) -> Dict[str, Any]:
    """
    The main agentic loop, implementing Observe, Orient, Decide, Act (OODA).
    """
    # Initialize the state (Memory/Observation)
    state = {
        "status": "INITIAL",
        "current_proposal": initial_proposal,
        "history": [],
        "last_errors": [],
        "iteration": 0
    }
    
    print(f"--- Agent Initialized. Goal: Validate Proposal. ---")

    while state["iteration"] < max_iterations:
        state["iteration"] += 1
        print(f"\n[Iteration {state['iteration']}] Current Status: {state['status']}")

        # 1. ORIENT & DECIDE: Determine the next step using the simulated LLM
        decision = mock_llm_decision_maker(state)
        print(f"   -> Decision: {decision.action.upper()} | Context: {decision.context}")

        # 2. ACT: Execute the chosen tool
        
        if decision.action == 'validate':
            # OBSERVE: Structure the current input for the tool
            try:
                proposal_obj = ProjectProposal(**state["current_proposal"])
            except Exception as e:
                print(f"Error parsing proposal: {e}")
                state["status"] = "ERROR"
                break

            # ACT: Call the validation tool. A @tool object is a StructuredTool,
            # not a function: invoke() takes the arguments as a dictionary keyed
            # by the tool's own parameter names.
            validation_result = validate_project_rules.invoke(
                {"proposal": proposal_obj.model_dump()}
            )
            
            # OBSERVE: Update state based on tool output
            if validation_result["status"] == "SUCCESS":
                state["status"] = "GOAL_MET"
                print("   -> Validation SUCCESS. Goal achieved.")
            else:
                state["status"] = "FAILED_VALIDATION"
                state["last_errors"] = validation_result["report"]
                print(f"   -> Validation FAILED. Errors: {validation_result['report']}")
                
        elif decision.action == 'correct':
            # ACT: Call the correction/planning tool
            current_input = state["current_proposal"]
            errors = state["last_errors"]
            
            corrected_proposal = generate_correction_plan.invoke(
                {"current_proposal": current_input, "error_report": errors}
            )
            
            # OBSERVE: Update state with the new input
            state["current_proposal"] = corrected_proposal.model_dump()
            state["status"] = "CORRECTED"
            print(f"   -> Correction Applied. New Title: '{state['current_proposal']['title'][:40]}...'")
            
        elif decision.action == 'terminate':
            break
            
        # Record history for transparency and debugging
        state["history"].append({
            "iteration": state["iteration"],
            "action": decision.action,
            "status_after": state["status"],
            "proposal_snapshot": state["current_proposal"]
        })

    print(f"\n--- Agent Execution Complete. Final Status: {state['status']} ---")
    return state


if __name__ == "__main__":
    # --- 4. Execution Examples ---

    # Example 1: Input designed to fail validation (Title too long, Description too short)
    initial_bad_proposal = {
        "title": "A Very Long Project Title That Exceeds The Maximum Character Count Allowed By The Strict Formatting Rules For The Proposal Submission System",
        "description": "Short description."
    }

    final_state = run_validation_agent(initial_bad_proposal)

    if final_state['status'] == 'GOAL_MET':
        print("\n[Final Output]")
        print(ProjectProposal(**final_state['current_proposal']).model_dump_json(indent=2))
