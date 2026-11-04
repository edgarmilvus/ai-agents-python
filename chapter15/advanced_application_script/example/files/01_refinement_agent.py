import subprocess
import json
import os
import sys
import textwrap
from typing import Dict, Any

# --- 1. Agent Inputs and Simulated LLM Outputs ---

# The specific requirement for the agent to solve.
AGENT_TASK = "Write a Python function 'calculate_median(data_list)' that finds the median of a list of numbers. It must raise a ValueError if the input is not a list of numbers."

# A comprehensive test suite designed to expose common errors (e.g., even/odd length, validation).
TEST_SUITE = textwrap.dedent("""
    import json
    import unittest
    from solution import calculate_median

    class TestMedian(unittest.TestCase):
        def test_odd_length(self):
            self.assertEqual(calculate_median([1, 2, 3, 4, 5]), 3)

        def test_even_length(self):
            # Median of [1, 2, 3, 4] is (2+3)/2 = 2.5
            self.assertEqual(calculate_median([1, 2, 3, 4]), 2.5)

        def test_validation_error(self):
            # Test case to ensure non-numeric input raises ValueError
            with self.assertRaises(ValueError):
                calculate_median(["a", "b", "c"])

    if __name__ == '__main__':
        # Run tests and capture results
        import sys
        import io
        
        # Redirect stdout/stderr to capture test results cleanly
        # unittest reports to stderr, so both streams have to be captured.
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = captured_output = io.StringIO()
        
        try:
            unittest.main(exit=False, verbosity=2)
        except SystemExit:
            pass # Prevent unittest.main from exiting the script
        
        sys.stdout, sys.stderr = old_stdout, old_stderr # Restore the streams
        
        # Output results in a structured format for the Refiner Agent
        test_output = captured_output.getvalue()
        
        # Simple check for success/failure based on standard unittest output patterns
        if "Ran 3 tests" in test_output and "OK" in test_output:
            status = "SUCCESS"
        elif "FAILED" in test_output or "ERROR" in test_output:
            status = "FAILURE"
        else:
            status = "UNKNOWN_ERROR"

        feedback = {
            "status": status,
            "raw_output": test_output
        }
        print(json.dumps(feedback))
""")

# --- 2. Simulated Agent Code Generation (Attempt 1 - Intentional Bug) ---

# This initial code is flawed: it fails to implement the required input validation (ValueError).
INITIAL_AGENT_CODE = textwrap.dedent("""
def calculate_median(data_list):
    # Sort the list first
    data_list.sort() 
    n = len(data_list)
    
    # Check if the length is odd
    if n % 2 == 1:
        # Return the middle element index
        return data_list[n // 2]
    else:
        # Handle even length (simple integer division bug for demonstration)
        mid1 = data_list[n // 2 - 1]
        mid2 = data_list[n // 2]
        return (mid1 + mid2) / 2
""")

# --- 3. Sandboxing and Execution Core ---

SANDBOX_DIR = "./agent_sandbox"
SOLUTION_FILE = os.path.join(SANDBOX_DIR, "solution.py")
TEST_FILE = os.path.join(SANDBOX_DIR, "run_tests.py")

def setup_sandbox(code_content: str):
    """Creates the necessary files (solution and test suite) in the sandbox directory."""
    os.makedirs(SANDBOX_DIR, exist_ok=True)
    
    # Write the generated code to 'solution.py'
    with open(SOLUTION_FILE, "w") as f:
        f.write(code_content)
        
    # Write the test suite wrapper to 'run_tests.py'
    with open(TEST_FILE, "w") as f:
        f.write(TEST_SUITE)
        
    print(f"# Sandbox setup complete. Files written to {SANDBOX_DIR}")

def execute_in_sandbox() -> Dict[str, Any]:
    """
    Executes the test script in a separate Python process (sandboxed) 
    and captures the structured JSON feedback.
    """
    print("# Executing code and tests...")
    try:
        # Use subprocess to run the test file. This isolates the execution.
        result = subprocess.run(
            [sys.executable, TEST_FILE],
            capture_output=True,
            text=True,
            check=False, # We allow non-zero exit codes (test failures)
            timeout=5 # Prevent infinite loops
        )
        
        # The test script prints the structured JSON feedback to stdout
        raw_output = result.stdout.strip()
        
        # Attempt to parse the structured feedback
        try:
            # Look for the JSON object printed by the test script
            feedback = json.loads(raw_output[raw_output.rfind('{'):])
        except json.JSONDecodeError:
            # Fallback for unexpected execution errors (e.g., syntax error)
            feedback = {
                "status": "EXECUTION_ERROR",
                "raw_output": result.stderr if result.stderr else result.stdout
            }
            
        return feedback

    except subprocess.TimeoutExpired:
        return {"status": "TIMEOUT", "raw_output": "Execution exceeded 5 seconds limit."}
    except Exception as e:
        return {"status": "SYSTEM_ERROR", "raw_output": str(e)}

# --- 4. The Iterative Refinement Loop ---

def run_refinement_cycle(attempt_code: str, cycle_num: int):
    """Manages one cycle of code generation, testing, and feedback."""
    print(f"\n--- CYCLE {cycle_num}: Testing Generated Code ---")
    
    # 1. Setup the environment
    setup_sandbox(attempt_code)
    
    # 2. Execute the test
    feedback = execute_in_sandbox()
    
    # 3. Analyze results
    print(f"Status: {feedback['status']}")
    
    if feedback['status'] == "FAILURE":
        print("\n[FEEDBACK SUMMARY]: Test failed. Sending detailed report to Refiner Agent...")
        print("--------------------------------------------------")
        # This is the crucial input for the next LLM call (the Refiner Agent)
        refinement_input = {
            "task": AGENT_TASK,
            "current_code": attempt_code,
            "test_feedback": feedback['raw_output']
        }
        
        # In a real system, the Refiner LLM would consume refinement_input and generate corrected code.
        print(json.dumps(refinement_input, indent=2))
        print("--------------------------------------------------")
        
        # Simulate the Refiner Agent's output based on the failure (Validation Error was missed)
        # Note: We skip the actual LLM call and provide the corrected code directly for demonstration.
        CORRECTED_CODE = textwrap.dedent("""
def calculate_median(data_list):
    # CRITICAL FIX: Ensure input is a list of numbers first.
    if not all(isinstance(x, (int, float)) for x in data_list):
        raise ValueError("Input must be a list of numbers.")
        
    # Sort the list
    data_list.sort() 
    n = len(data_list)
    
    # Check if the length is odd
    if n % 2 == 1:
        return data_list[n // 2]
    else:
        # Handle even length
        mid1 = data_list[n // 2 - 1]
        mid2 = data_list[n // 2]
        return (mid1 + mid2) / 2
""")
        
        print("\n--- SIMULATION: Refiner Agent generated corrected code. ---")
        run_refinement_cycle(CORRECTED_CODE, cycle_num + 1)
        
    elif feedback['status'] == "SUCCESS":
        print("\n[SUCCESS]: All tests passed. Code is production ready.")
        print(f"Final Code:\n{attempt_code}")
        
    else:
        print(f"\n[ERROR]: Unexpected execution error or timeout.")
        print(f"Raw Output: {feedback['raw_output']}")

# --- 5. Execution Start ---
if __name__ == "__main__":
    # Start the process with the intentionally flawed code
    run_refinement_cycle(INITIAL_AGENT_CODE, 1)

    # Cleanup the sandbox directory (optional, but good practice)
    # import shutil
    # shutil.rmtree(SANDBOX_DIR)
