import time
from typing import ClassVar
from pydantic import BaseModel, Field

# --- 1. Structured Communication Protocol (Pydantic) ---

class PlanningTask(BaseModel):
    """
    Defines the initial input structure for the planning agent.
    This is the 'client request' or initial requirements document.
    """
    subject: str = Field(description="The core topic the motto must address.")

class RawMottoOutput(BaseModel):
    """
    Defines the structured output from the Idea Generator Agent (Task 1).
    This output is the input for the Formatter Agent (Task 2).
    """
    motto_text: str = Field(description="The raw, unformatted motto text.")
    confidence_score: float = Field(description="Agent's self-assessed confidence (0.0 to 1.0).")

class FinalDeliverable(BaseModel):
    """
    Defines the final, formatted output structure from the Formatter Agent.
    This represents the final deliverable handed back to the orchestrator.
    """
    client_name: str
    formatted_output: str

# --- 2. Mock LLM Interaction (Simulating API Calls) ---

def mock_llm_call(prompt: str, output_schema: BaseModel) -> dict:
    """
    Simulates an LLM API call that generates structured output.
    In a real system, this function would handle network requests, 
    API keys, and robust Pydantic parsing/retries.
    """
    print(f"--- LLM Mock: Processing prompt for schema {output_schema.__name__} ---")
    time.sleep(0.1) # Simulate network latency

    if output_schema == RawMottoOutput:
        # Mock generation logic based on input subject
        if "AI Education" in prompt:
            return {"motto_text": "Code the Future, Learn the Machine.", "confidence_score": 0.95}
        else:
            # Low confidence mock for testing feedback loops
            return {"motto_text": "A generic placeholder motto.", "confidence_score": 0.45}
    
    elif output_schema == FinalDeliverable:
        # Mock formatting logic: extracting raw text and wrapping it
        if "RAW_TEXT:" in prompt:
            raw_text = prompt.split("RAW_TEXT:")[1].strip()
        else:
            raw_text = "Error: Raw text not found."
        
        formatted = (
            f"## Final Client Deliverable\n\n"
            f"**Project:** Swarm Motto Generation\n"
            f"**Motto:** *{raw_text}*\n\n"
            f"--- End of Deliverable ---"
        )
        return {"client_name": "Acme Corp", "formatted_output": formatted}

    return {}


# --- 3. Agent Definitions (Defining Specialized Roles) ---

class BaseAgent:
    """Provides common properties and the core execution logic wrapper."""
    role: ClassVar[str] = "Generic Agent"
    
    def __init__(self, name: str):
        self.name = name
        print(f"[{self.name}]: Initialized as {self.role}.")

    def _execute_task(self, prompt: str, schema: BaseModel) -> dict:
        """Internal method to handle the LLM interaction."""
        print(f"[{self.name}]: Executing task...")
        return mock_llm_call(prompt, schema)

class IdeaGeneratorAgent(BaseAgent):
    """
    Role 1: Responsible for initial conceptualization (Planning Phase).
    Output: RawMottoOutput (Structured Data).
    """
    role: ClassVar[str] = "Idea Generator"

    def generate_motto(self, task: PlanningTask) -> RawMottoOutput:
        """Takes the structured task and produces a raw motto."""
        prompt = (
            f"Generate a concise, impactful motto for the subject: '{task.subject}'. "
            f"Ensure the output adheres strictly to the RawMottoOutput schema."
        )
        result = self._execute_task(prompt, RawMottoOutput)
        
        # Validation and structured return
        return RawMottoOutput(**result)

class FormatterAgent(BaseAgent):
    """
    Role 2: Responsible for taking raw input and formatting it for final delivery (Execution Phase).
    Input: RawMottoOutput (Structured Data).
    Output: FinalDeliverable (Structured Data).
    """
    role: ClassVar[str] = "Formatter"

    def finalize_delivery(self, raw_data: RawMottoOutput) -> FinalDeliverable:
        """Takes the raw motto and formats it into the final client structure."""
        
        # Dynamic Feedback Loop: Check confidence before proceeding
        if raw_data.confidence_score < 0.8:
            print(f"[{self.name}]: WARNING: Low confidence ({raw_data.confidence_score}). Rerouting or refusing task.")
            # This demonstrates how the receiving agent can enforce quality control
            raise ValueError("Generation quality too low. Requires re-planning.")

        prompt = (
            f"Format the following raw text into a professional client deliverable. "
            f"Use Markdown formatting. RAW_TEXT: {raw_data.motto_text}"
        )
        result = self._execute_task(prompt, FinalDeliverable)
        
        # Validation and structured return
        return FinalDeliverable(**result)

# --- 4. The Swarm Orchestration (The Agency Manager) ---

def run_development_agency(subject: str):
    """
    Orchestrates the sequential workflow, managing state and data transfer 
    between the specialized agents.
    """
    print("\n" + "="*50)
    print(f"[ORCHESTRATOR]: Starting Swarm Execution for subject: '{subject}'")
    print("="*50)
    
    # Define the initial structured task
    initial_task = PlanningTask(subject=subject)

    # 1. Initialize specialized agents
    planner = IdeaGeneratorAgent(name="Agent_P1")
    formatter = FormatterAgent(name="Agent_F1")

    try:
        # 2. Sequential Task 1: Planner executes and produces structured output
        print("\n[ORCHESTRATOR]: Task 1 (Generation) assigned to Agent_P1.")
        raw_motto = planner.generate_motto(initial_task)
        print(f"[Agent_P1]: Generation Complete. Confidence: {raw_motto.confidence_score}")
        
        # 3. Sequential Task 2: Formatter receives the structured output and executes
        print("\n[ORCHESTRATOR]: Task 2 (Formatting) assigned to Agent_F1.")
        final_delivery = formatter.finalize_delivery(raw_motto)

        # 4. Final Output
        print("\n[ORCHESTRATOR]: Swarm execution successful. Final Deliverable:")
        print("-" * 40)
        print(final_delivery.formatted_output)
        print("-" * 40)
        
    except ValueError as e:
        print(f"\n[ORCHESTRATOR]: Execution halted due to agent feedback.")
        print(f"Reason: {e}")
        print("[ORCHESTRATOR]: Aborting delivery.")


# --- 5. Execution Demonstration ---
if __name__ == "__main__":
    # Scenario A: Successful execution (High confidence)
    run_development_agency(subject="AI Education")
    
    # Separator for clarity
    print("\n" + "#" * 70 + "\n")
    
    # Scenario B: Execution failure due to low confidence (Testing the feedback loop)
    run_development_agency(subject="A very obscure topic")
