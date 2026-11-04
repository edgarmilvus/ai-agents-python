import json
from typing import Dict, Any

# --- Simulated LLM/Agent Interaction Functions (as provided in framework) ---
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

    return "" # Placeholder for other calls

def run_data_extraction_agent(fail_type: str) -> str:
    """Simulates the primary agent output, sometimes failing format."""
    if fail_type == "key_error":
        # Logical failure: incorrect key name ('name' instead of 'user_name')
        return '{"name": "Alice", "user_id": 101, "status_code": "ACTIVE"}'
    elif fail_type == "value_error":
        # Logical failure: incorrect status code value ('DISABLED' instead of allowed values)
        return '{"user_name": "Bob", "user_id": 102, "status_code": "DISABLED"}'
    else:
        # Success
        return '{"user_name": "Charlie", "user_id": 103, "status_code": "PENDING"}'

def format_validator_agent(raw_output: str) -> Dict[str, Any]:
    """Uses LLM to validate output against a strict schema (The Reflector)."""
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
    print("--- exercise 1: Format Validator Reflection Loop ---")
    
    for failure_case in ["success", "key_error", "value_error"]:
        print(f"\nAttempting case: {failure_case}")
        primary_output = run_data_extraction_agent(failure_case)
        validation_report = format_validator_agent(primary_output)
        
        if validation_report.get('is_valid'):
            print(f"  [VALIDATION SUCCESS] Final Output: {primary_output}")
        else:
            # Log the specific reason identified by the validator
            print(f"  [VALIDATION FAILURE] Reflection Reason: {validation_report.get('reason')}")
            print("  Output discarded due to structural violation.")

# Execution
exercise_12_4_1()
