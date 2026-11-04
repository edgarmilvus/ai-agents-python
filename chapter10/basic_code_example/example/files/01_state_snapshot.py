import pickle
import os
import sys
from datetime import datetime

# --- Configuration ---
STATE_FILE = "agent_state.pkl"
INITIAL_STATE = {
    "session_count": 0,
    "total_actions": 0,
    "last_run": None,
    "history_log": []
}

class SimpleAgentState:
    """
    A simple class to encapsulate the agent's internal memory and state.
    This object is what we will serialize and deserialize using pickle.
    """
    def __init__(self, initial_data: dict):
        # Initialize attributes based on the provided dictionary
        self.session_count = initial_data["session_count"]
        self.total_actions = initial_data["total_actions"]
        self.last_run = initial_data["last_run"]
        self.history_log = initial_data["history_log"]

    def record_action(self, action_type: str):
        """Simulates the agent performing an action and updating its state."""
        self.total_actions += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] Action recorded: {action_type}"
        self.history_log.append(log_entry)
        print(f"  -> Agent executed action: {action_type}")

    def start_new_session(self):
        """Increments the session counter and updates the last run time."""
        self.session_count += 1
        self.last_run = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n--- Session {self.session_count} Started ({self.last_run}) ---")

    def __str__(self):
        """Provides a readable summary of the current state for display."""
        return (
            f"\n--- Persistent Agent State Summary ---\n"
            f"Total Sessions Run: {self.session_count}\n"
            f"Total Actions Ever Performed: {self.total_actions}\n"
            f"Last Run Timestamp: {self.last_run if self.last_run else 'N/A'}\n"
            f"History Log Length: {len(self.history_log)} entries\n"
            f"--------------------------------------\n"
        )


def load_agent_state(filename: str) -> SimpleAgentState:
    """
    Attempts to load the agent state from a pickled file.
    If the file does not exist or is corrupted, it initializes a new state.
    """
    if os.path.exists(filename):
        try:
            # Open the file in binary read mode ('rb')
            with open(filename, 'rb') as f:
                # Deserialize the object using pickle.load()
                loaded_state = pickle.load(f)
                print(f"[LOAD] State successfully loaded from {filename}.")
                
                # Critical check: Ensure the loaded object is the expected type
                if not isinstance(loaded_state, SimpleAgentState):
                    print("[ERROR] Loaded object type mismatch. Initializing new state.")
                    return SimpleAgentState(INITIAL_STATE)
                return loaded_state
                
        except (pickle.UnpicklingError, EOFError, FileNotFoundError, AttributeError) as e:
            # Handle corrupted, empty, or incompatible files gracefully
            print(f"[WARNING] Error loading state ({type(e).__name__}: {e}). Initializing new state.")
            return SimpleAgentState(INITIAL_STATE)
    else:
        # If the file does not exist, start fresh
        print(f"[INIT] State file {filename} not found. Initializing new agent state.")
        return SimpleAgentState(INITIAL_STATE)


def save_agent_state(state: SimpleAgentState, filename: str):
    """
    Serializes and saves the current agent state to a pickled file.
    """
    try:
        # Open the file in binary write mode ('wb')
        with open(filename, 'wb') as f:
            # Serialize the object using pickle.dump()
            pickle.dump(state, f)
            print(f"[SAVE] State successfully saved to {filename}.")
    except IOError as e:
        print(f"[FATAL ERROR] Could not save state to {filename}: {e}")
        # Terminate the program if persistence fails critically
        sys.exit(1)


# --- Main Execution Logic ---
def run_agent_session():
    """
    Simulates a single, discrete run of the autonomous agent.
    """
    print("--- Agent Persistence Demonstration ---")
    
    # 1. Load the previous state or initialize a new one
    agent_state = load_agent_state(STATE_FILE)

    # 2. Print the state before modification (showing the state from the *last* run)
    print(agent_state)

    # 3. Simulate agent activity and update state for the *current* run
    agent_state.start_new_session()
    agent_state.record_action("Data Retrieval Phase")
    agent_state.record_action("LLM Inference Step")
    agent_state.record_action("Output Generation")

    # 4. Print the state after modification
    print(agent_state)

    # 5. Persist the updated state for the next run
    save_agent_state(agent_state, STATE_FILE)
    
    print("-------------------------------------")
    print("Rerun this script immediately to observe the state incrementing.")


if __name__ == "__main__":
    run_agent_session()
