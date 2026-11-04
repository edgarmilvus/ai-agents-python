import sys
import json
from typing import Dict, Any, Type, Callable

# --- Custom Exceptions for exercise 2 and 12-4.5 ---
class AgentError(Exception):
    """Base exception for all agent system errors."""
    pass

class ConfigurationError(AgentError):
    """Raised when required startup configuration (e.g., sys.argv) is missing."""
    pass

class NetworkToolError(AgentError):
    """Raised for transient network issues during tool execution."""
    pass

class DatabaseToolError(AgentError):
    """Raised for persistent database connection or credential issues."""
    pass

# --- Simulated LLM/Agent Interaction Functions ---
# In a real scenario, these would call a large language model API.
def mock_llm_call(prompt: str, temperature: float = 0.1) -> str:
    """Simulates an LLM response based on prompt keywords."""
    prompt_lower = prompt.lower()
    
    if "validate json" in prompt_lower or "schema validator" in prompt_lower:
        # Only the raw output can be judged: the prompt also carries the schema,
        # which names every required key and every legal status.
        raw = prompt_lower.split("raw output:", 1)[-1]
        has_keys = all(key in raw for key in ("user_name", "user_id", "status_code"))
        valid_status = any(f'"{status}"' in raw for status in ("active", "inactive", "pending"))
        if has_keys and valid_status:
            return '{"is_valid": true, "reason": "Schema adhered to."}'
        if not has_keys:
            return '{"is_valid": false, "reason": "Missing required key: user_name or user_id."}'
        return '{"is_valid": false, "reason": "Status code violation: Must be ACTIVE, INACTIVE, or PENDING."}'

    if "code review" in prompt_lower:
        if "list comprehension" in prompt_lower:
            return "FAILURE: Code uses prohibited list comprehension syntax."
        else:
            return "SUCCESS: Code adheres to all constraints."

    if "usage guide" in prompt_lower:
        # Response for ConfigurationError (exercise 4)
        return json.dumps({
            "guide": "Usage: python agent_runner.py --task-id <ID> [options]\n\nExample 1 (Basic):\n$ python agent_runner.py --task-id PRJ-401\n\nExample 2 (Verbose Mode):\n$ python agent_runner.py --task-id PRJ-401 --debug",
            "message": "The agent cannot start without a task ID."
        })

    if "generate recovery strategy" in prompt_lower:
        if "runtime failure" in prompt_lower:
            return "RETRY_STRATEGY: Wait 5 seconds and attempt the API call again."
        if "logical failure" in prompt_lower:
            return "REPLAN_STRATEGY: The ID was not found. Modify the input parameter to search for a related resource using a wildcard."
    
    # Default response for code generation (exercise 3)
    if "previous attempt failed" in prompt_lower:
        # Success on second attempt (no list comprehension)
        return "def process_data(data):\n    result = []\n    for item in data:\n        if item > 10:\n            result.append(item)\n    return result"
    
    # Failure on first attempt (uses list comprehension)
    return "def process_data(data):\n    return [item for item in data if item > 10]"


# --- exercise 1: Format Validator Reflection Loop ---

def run_data_extraction_agent(fail_type: str) -> str:
    """Simulates the primary agent output, sometimes failing format."""
    if fail_type == "key_error":
        # Logical failure: incorrect key name
        return '{"name": "Alice", "user_id": 101, "status_code": "ACTIVE"}'
    elif fail_type == "value_error":
        # Logical failure: incorrect status code value
        return '{"user_name": "Bob", "user_id": 102, "status_code": "DISABLED"}'
    else:
        # Success
        return '{"user_name": "Charlie", "user_id": 103, "status_code": "PENDING"}'

def format_validator_agent(raw_output: str) -> Dict[str, Any]:
    """Uses LLM to validate output against a strict schema."""
    target_schema = "JSON object with keys: user_name (string), user_id (integer), status_code (must be ACTIVE, INACTIVE, or PENDING)."
    
    validation_prompt = (
        f"You are a strict JSON schema validator. Analyze the following raw JSON output against the target schema.\n"
        f"TARGET SCHEMA: {target_schema}\n"
        f"RAW OUTPUT: {raw_output}\n"
        f"Output only a JSON object: {{'is_valid': true/false, 'reason': '...'}}"
    )
    
    validation_result_str = mock_llm_call(validation_prompt)
    return json.loads(validation_result_str)

def exercise_12_4_1():
    print("--- exercise 1: Format Validator ---")
    
    for failure_case in ["success", "key_error", "value_error"]:
        print(f"\nAttempting case: {failure_case}")
        primary_output = run_data_extraction_agent(failure_case)
        validation_report = format_validator_agent(primary_output)
        
        if validation_report.get('is_valid'):
            print(f"  [VALIDATION SUCCESS] Final Output: {primary_output}")
        else:
            print(f"  [VALIDATION FAILURE] Reflection Reason: {validation_report.get('reason')}")
            print("  Output discarded due to structural violation.")


# --- exercise 2: Differentiating Tool Errors ---

def external_api_tool(id_param: str) -> Dict[str, Any]:
    """Simulates an external tool with different failure modes."""
    if id_param == "FAIL_NETWORK":
        # Simulate Runtime Error
        raise NetworkToolError("Connection timeout during request.")
    elif id_param == "INVALID_ID":
        # Simulate Logical Error (successful API call, but error payload)
        return {"success": False, "error_code": 404, "message": "Resource ID not found in primary index."}
    else:
        return {"success": True, "data": f"Resource data for {id_param}"}

def agent_execution_handler(id_param: str):
    print(f"\n--- exercise 2: Handling ID '{id_param}' ---")
    try:
        tool_output = external_api_tool(id_param)
        
        # 3. Logical Failure Analysis (using dict.get())
        if not tool_output.get('success', True): # Check if 'success' is explicitly False
            error_code = tool_output.get('error_code', 'UNKNOWN')
            error_msg = tool_output.get('message', 'No message provided.')
            
            # 4. Generate Recovery Strategy (LLM call based on classification)
            recovery_prompt = (
                f"A logical failure occurred with error code {error_code} and message: '{error_msg}'. "
                f"Classify this as a logical failure and generate a recovery strategy."
            )
            strategy = mock_llm_call(recovery_prompt)
            print(f"  [CLASSIFICATION] Logical Failure (404/Bad Input)")
            print(f"  [RECOVERY PLAN] {strategy}")
            return
            
        print(f"  [SUCCESS] Tool executed successfully: {tool_output['data']}")

    except NetworkToolError as e:
        # 2. Catch Runtime Exception
        recovery_prompt = (
            f"A runtime failure occurred: {e}. Classify this as a transient network failure and generate a recovery strategy."
        )
        strategy = mock_llm_call(recovery_prompt)
        print(f"  [CLASSIFICATION] Runtime Failure (Network)")
        print(f"  [RECOVERY PLAN] {strategy}")
    except Exception as e:
        print(f"  [UNHANDLED ERROR] An unexpected error occurred: {type(e).__name__}")


# --- exercise 3: Recursive Error Recovery ---

MAX_ATTEMPTS = 3

def code_review_agent(code: str, constraints: str) -> str:
    """Reflects on code quality based on constraints."""
    prompt = f"Perform a code review based on the constraint: '{constraints}'. Code:\n{code}"
    return mock_llm_call(prompt)

def recursive_task_solver(initial_prompt: str, constraints: str, attempt: int = 1):
    if attempt > MAX_ATTEMPTS:
        raise AgentError("Maximum self-correction attempts reached without success.")
    
    print(f"\n--- Attempt {attempt}/{MAX_ATTEMPTS} ---")
    
    # 2. Execute Primary Agent
    agent_prompt = initial_prompt
    if attempt > 1:
        # 3. Dynamic Prompt Generation: Augment the prompt based on previous failure
        agent_prompt = f"ATTEMPT {attempt}: Previous attempt failed because of constraint violation. {initial_prompt}"
        print(f"  [AUGMENTED PROMPT] Using modified instructions for re-execution.")

    generated_code = mock_llm_call(agent_prompt, temperature=0.5)
    
    # 2. Reflection
    reflection_feedback = code_review_agent(generated_code, constraints)
    print(f"  [REFLECTION] Feedback: {reflection_feedback.split(':')[0]}")
    
    if reflection_feedback.startswith("SUCCESS"):
        print(f"  [SUCCESS] Task completed on attempt {attempt}.")
        print("Final Code:\n" + generated_code)
        return generated_code
    else:
        print(f"  [CORRECTION NEEDED] Modifying plan for next attempt...")
        # Recursive call with augmented prompt (simulated by the LLM response)
        recursive_task_solver(
            initial_prompt=f"Previous attempt failed: {reflection_feedback}. You MUST adhere to the constraint: {constraints}",
            constraints=constraints,
            attempt=attempt + 1
        )

# --- exercise 4: Interactive Challenge (sys.argv and Flashing) ---

def usage_guide_agent() -> Dict[str, str]:
    """LLM agent to generate user-friendly usage instructions."""
    prompt = "Generate a helpful usage guide for a command-line agent requiring a --task-id argument."
    response = mock_llm_call(prompt)
    return json.loads(response)

def simulate_flashing_error(error_type: str, message: str, guide: str = None):
    """Simulates the output format of a web framework 'flash' message."""
    print(f"\n[FLASH: {error_type.upper()}] Configuration Required: {message}")
    if guide:
        print("\n--- Generated Usage Guide ---")
        print(guide)
    print("-----------------------------\n")

def agent_entry_point(argv_list: list):
    print("--- exercise 4: Robust Configuration Check ---")
    
    has_task_id = False
    for arg in argv_list:
        if arg.startswith("--task-id"):
            has_task_id = True
            break
            
    if not has_task_id:
        # 2. Raise Custom Exception
        raise ConfigurationError("Missing required command-line argument: --task-id.")
        
    print(f"[STARTUP SUCCESS] Agent initialized with required arguments.")


# --- exercise 5: Tool Failure Handler Registry ---

# 3. Create a Handler Registry
ERROR_HANDLER_REGISTRY: Dict[Type[AgentError], Callable[[str], str]] = {}

def register_handler(exception_class: Type[AgentError]):
    """Decorator to register handlers."""
    def decorator(func: Callable[[str], str]):
        ERROR_HANDLER_REGISTRY[exception_class] = func
        return func
    return decorator

@register_handler(NetworkToolError)
def handle_network_error(context: str) -> str:
    """Handler for transient network issues."""
    print(f"  [HANDLER LOG] Network failure detected. Context: {context}")
    return "RECOVERY_ACTION: The network is unstable. Implement an exponential backoff retry strategy."

@register_handler(DatabaseToolError)
def handle_database_error(context: str) -> str:
    """Handler for persistent database issues."""
    print(f"  [HANDLER LOG] Database failure detected. Context: {context}")
    return "RECOVERY_ACTION: Credentials likely expired or connection misconfigured. Alert System Admin."

def simulated_tool_execution(tool_name: str):
    if tool_name == "network":
        raise NetworkToolError("Timeout accessing external API.")
    elif tool_name == "db":
        raise DatabaseToolError("Authentication failed for read operation.")
    else:
        print(f"Tool {tool_name} executed successfully.")

def agent_executor_with_registry(tool_name: str):
    print(f"\n--- exercise 5: Executing Tool '{tool_name}' ---")
    try:
        simulated_tool_execution(tool_name)
    except AgentError as e:
        exception_type = type(e)
        if exception_type in ERROR_HANDLER_REGISTRY:
            handler = ERROR_HANDLER_REGISTRY[exception_type]
            recovery_suggestion = handler(str(e))
            print(f"  [AGENT RESPONSE] Tool failure handled by custom registry.")
            print(f"  Suggested Agent Action: {recovery_suggestion}")
        else:
            print(f"  [AGENT RESPONSE] Unregistered error type: {exception_type.__name__}. Raising fatal error.")
            raise e


# --- Main Execution Block ---

if __name__ == "__main__":
    
    # 12-4.1 Execution
    exercise_12_4_1()

    # 12-4.2 Execution
    agent_execution_handler("VALID_ID_123")
    agent_execution_handler("FAIL_NETWORK")
    agent_execution_handler("INVALID_ID")
    
    # 12-4.3 Execution
    CONSTRAINTS = "The generated Python function must not use any list comprehensions."
    INITIAL_TASK = "Write a Python function called 'process_data' that filters a list of numbers, keeping only those greater than 10."
    try:
        recursive_task_solver(INITIAL_TASK, CONSTRAINTS)
    except AgentError as e:
        print(f"\n[FATAL ERROR] {e}")

    # 12-4.4 Execution (Interactive Challenge)
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

    # 12-4.5 Execution
    agent_executor_with_registry("network")
    agent_executor_with_registry("db")
    agent_executor_with_registry("success_tool")
