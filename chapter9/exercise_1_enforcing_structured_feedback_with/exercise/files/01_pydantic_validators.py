import json
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime

# --- Pydantic Setup Mock (Required for Exercises 1, 2, 3, 4) ---

class PydanticValidationError(Exception):
    """Custom exception for simulated Pydantic errors."""
    pass

class MockPydanticModel:
    """Simulates basic Pydantic validation and type coercion."""
    
    def __init__(self, **data):
        self._data = data
        self._validate()

    def _validate(self):
        # Validation logic specific to AgentCritique (defined below)
        pass 

    @classmethod
    def parse_raw(cls, json_data: str) -> 'AgentCritique':
        try:
            data = json.loads(json_data)
            return cls(**data)
        except json.JSONDecodeError as e:
            raise PydanticValidationError(f"JSON decoding failed: {e}")
        except TypeError as e:
            # Handle cases where __init__ receives wrong types
            raise PydanticValidationError(f"Initialization failed due to type error: {e}")

    def dict(self):
        return self._data

class AgentCritique(MockPydanticModel):
    """
    Defines the structured schema for agent feedback, enforcing strict types and ranges.
    """
    def __init__(self, 
                 score_out_of_10: int = None, 
                 rationale_summary: str = None, 
                 suggested_refinement_steps: List[str] = None, 
                 critical_error_flag: bool = None,
                 **kwargs):
        
        # Store only what was provided, as Pydantic does: a missing key has to
        # reach the validator, which reports it, instead of raising a TypeError
        # from the constructor before validation can run.
        self._data = {
            key: value
            for key, value in (
                ('score_out_of_10', score_out_of_10),
                ('rationale_summary', rationale_summary),
                ('suggested_refinement_steps', suggested_refinement_steps),
                ('critical_error_flag', critical_error_flag),
            )
            if value is not None
        }
        self._validate()

    def _validate(self):
        # 1. Score Validation (Type and Range)
        score = self._data.get('score_out_of_10')
        if not isinstance(score, int):
            raise PydanticValidationError("Field 'score_out_of_10' must be an integer.")
        if not 1 <= score <= 10:
            raise PydanticValidationError(f"Score {score} is out of range (1-10).")

        # 2. Rationale Validation
        rationale = self._data.get('rationale_summary')
        if not isinstance(rationale, str):
             raise PydanticValidationError("Missing or invalid 'rationale_summary' (must be str).")

        # 3. Refinement Steps Validation
        refinements = self._data.get('suggested_refinement_steps')
        if refinements is None:
            # Check for missing field (Case B)
            raise PydanticValidationError("Missing mandatory field 'suggested_refinement_steps'.")
        if not isinstance(refinements, list):
            raise PydanticValidationError("'suggested_refinement_steps' must be a list.")
        
        # 4. Critical Flag Validation
        flag = self._data.get('critical_error_flag')
        if not isinstance(flag, bool):
            raise PydanticValidationError("Missing or invalid 'critical_error_flag' (must be bool).")

def parse_raw_critique(raw_text: str) -> AgentCritique:
    """Simulates parsing raw LLM JSON output and validating it against AgentCritique."""
    print(f"\nAttempting to parse raw text...")
    try:
        critique = AgentCritique.parse_raw(raw_text)
        print("-> SUCCESS: Critique validated successfully.")
        return critique
    except PydanticValidationError as e:
        print(f"-> VALIDATION FAILED: {e}")
        raise

# --- Demonstration ---

# 4. Demonstrate Success
raw_success = json.dumps({
    "score_out_of_10": 9,
    "rationale_summary": "The logic is sound and highly optimized, but documentation needs minor cleanup.",
    "suggested_refinement_steps": ["Add docstrings to helper functions.", "Verify license header."],
    "critical_error_flag": False
})

# 3. Error Handling Simulation: Case A (Range Error)
raw_fail_a = json.dumps({
    "score_out_of_10": 15,  # Out of range (1-10)
    "rationale_summary": "The code is amazing, but the score is too high.",
    "suggested_refinement_steps": [],
    "critical_error_flag": False
})

# 3. Error Handling Simulation: Case B (Missing Field Error)
raw_fail_b = json.dumps({
    "score_out_of_10": 5,
    "rationale_summary": "The code is incomplete.",
    "critical_error_flag": True
    # 'suggested_refinement_steps' is missing
})

print("--- Exercise 1 Demonstration ---")
try:
    critique_success = parse_raw_critique(raw_success)
except PydanticValidationError:
    pass

try:
    parse_raw_critique(raw_fail_a)
except PydanticValidationError:
    pass

try:
    parse_raw_critique(raw_fail_b)
except PydanticValidationError:
    pass
