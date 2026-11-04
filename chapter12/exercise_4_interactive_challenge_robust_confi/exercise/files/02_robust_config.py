import sys
import json
from typing import Dict, Any

# --- Custom Exceptions ---
class AgentError(Exception): pass
class ConfigurationError(AgentError): pass

# --- Simulated LLM/Agent Interaction Functions (updated for this exercise) ---
def mock_llm_call(prompt: str, temperature: float = 0.1) -> str:
    # ... (omitting previous mock logic for brevity, focusing on new logic) ...
    if "usage guide" in prompt.lower():
        # 3. LLM-Powered Usage Generation
        return json.dumps({
            "guide": "Usage: python agent_runner.py --task-id <ID> [options]\n\nExample 1 (Basic):\n$ python agent_runner.py --task-id PRJ-401\n\nExample 2 (Verbose Mode):\n$ python agent_runner.py --task-id PRJ-401 --debug",
            "message": "The agent cannot start without the required task ID argument."
        })
    return ""

def usage_guide_agent() -> Dict[str, str]:
    """LLM agent to generate user-friendly usage instructions."""
    prompt = "Generate a helpful usage guide for a command-line agent requiring a --task-id argument."
    response = mock_llm_call(prompt)
    return json.loads(response)

def simulate_flashing_error(error_type: str, message: str, guide: str = None):
    """4. Simulated Flashing Output."""
    print(f"\n[FLASH: {error_type.upper()}] Configuration Required: {message}")
    if guide:
        print("\n--- Generated Usage Guide ---")
        print(guide)
    print("-----------------------------\n")

def agent_entry_point(argv_list: list):
    """1. Entry Point Modification to check sys.argv."""
    print("--- exercise 4: Robust Configuration Check ---")
    
    has_task_id = any(arg.startswith("--task-id") for arg in argv_list)
            
    if not has_task_id:
        # 2. Raise Custom Exception
        raise ConfigurationError("Missing required command-line argument: --task-id.")
        
    print(f"[STARTUP SUCCESS] Agent initialized with required arguments.")

# Execution (Simulating command line calls)
try:
    # Case 1: Failure (Simulate missing argument)
    agent_entry_point(["agent_runner.py", "--config-path", "/tmp/cfg.json"])
except ConfigurationError as e:
    # The main error handler catches the configuration error
    guide_data = usage_guide_agent()
    simulate_flashing_error("error", guide_data['message'], guide_data['guide'])

# Case 2: Success (Simulate correct argument)
try:
    agent_entry_point(["agent_runner.py", "--task-id", "PRJ-401"])
except ConfigurationError:
    pass # Should not happen here
