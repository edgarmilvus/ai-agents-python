import json
from typing import Tuple, Dict, Any

# --- 1. Simulation Setup: The Mock LLM ---

def mock_llm_call(prompt: str, iteration: int) -> str:
    """
    Simulates an LLM call. For educational purposes, this function is
    designed to guarantee a logical failure on the first attempt and
    a successful correction on subsequent attempts.
    """
    if iteration == 1:
        # Initial failure: The LLM forgets the 'status' requirement.
        # This is syntactically valid JSON, but logically incomplete.
        return '{"name": "Alice", "role": "Developer", "projects": ["Project X"]}'
    else:
        # Success: The LLM incorporates the correction context from the reflection.
        return '{"name": "Alice", "role": "Developer", "projects": ["Project X"], "status": "Active"}'

# --- 2. The Reflector/Validator Component ---

def validate_profile_json(raw_json_str: str) -> Tuple[bool, str]:
    """
    Analyzes the output string against system constraints.
    Returns (True, message) if valid, or (False, detailed_error) otherwise.
    This component is the core of the reflection process.
    """
    data = {}
    try:
        # Attempt 1: Catching Runtime Exceptions (e.g., malformed syntax)
        data = json.loads(raw_json_str)

    except json.JSONDecodeError as e:
        # If parsing fails, this is a clear structural/runtime error.
        return False, f"RUNTIME ERROR: JSON parsing failed. Malformed syntax. Error: {e}"

    # Attempt 2: Catching Logical Failures (e.g., missing required content)
    # Requirement: The output must contain a 'status' key.
    # We use dict.get() for safe, robust key checking.
    if data.get("status") is None:
        # This is a logical failure, as the constraint was violated.
        return False, "LOGICAL FAILURE: The required key 'status' is missing from the generated profile."

    # If all checks pass
    return True, "Validation successful. All constraints met."

# --- 3. The Autonomous Execution Loop ---

MAX_ATTEMPTS = 3
initial_prompt = (
    "Task: Generate a JSON profile for a user named Alice. "
    "The profile MUST include 'name', 'role', 'projects', and 'status'."
)
current_prompt = initial_prompt # The prompt that will be passed to the LLM
agent_output = None
success = False
error_trace = "" # Accumulates failure history for effective re-prompting

print("--- Starting Agent Execution Loop ---")

for attempt in range(1, MAX_ATTEMPTS + 1):
    print(f"\n[ATTEMPT {attempt}] Running LLM with prompt length: {len(current_prompt)} characters.")

    # 3.1. Execution Step: Call the simulated agent
    agent_output = mock_llm_call(current_prompt, attempt)
    print(f"  > Raw Output Received: {agent_output}")

    # 3.2. Reflection/Validation Step: Analyze the output
    is_valid, validation_message = validate_profile_json(agent_output)

    if is_valid:
        # 3.3. Success Path: Break the loop
        print(f"  > SUCCESS: Output validated. Message: {validation_message}")
        success = True
        break
    else:
        # 3.4. Failure Path: Trigger Self-Correction
        print(f"  > FAILURE DETECTED: {validation_message}")

        # Accumulate the error details (The Reflection Trace)
        error_trace += f"\n--- Attempt {attempt} Failure Trace ---\n"
        error_trace += f"Observed Output: {agent_output}\n"
        error_trace += f"Validation Message: {validation_message}\n"

        # Dynamic Re-Prompting: Inject the reflection into the new context
        current_prompt = (
            f"{initial_prompt}\n\n"
            f"CRITICAL REFLECTION INSTRUCTION: Your previous attempt failed validation. "
            f"You MUST review the failure trace below and correct the output for this next attempt.\n"
            f"FAILURE TRACE:\n{error_trace}"
        )

# --- 4. Final Result Handling ---
if success:
    print("\n--- Final Result ---")
    try:
        final_data = json.loads(agent_output)
        print(f"Agent successfully self-corrected on attempt {attempt}.")
        print(f"Parsed Data:\n{json.dumps(final_data, indent=4)}")
    except json.JSONDecodeError:
        # Should not happen if validation passed, but kept for robustness
        print("Error during final parsing.")
else:
    print(f"\n--- Final Result ---")
    print(f"Agent failed to self-correct after {MAX_ATTEMPTS} attempts. Last error: {validation_message}")
