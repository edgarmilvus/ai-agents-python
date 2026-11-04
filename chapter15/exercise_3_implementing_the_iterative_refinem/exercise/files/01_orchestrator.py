from typing import Dict, Any, Optional, Tuple

# Re-defining necessary classes for standalone execution (if not imported)
# If running sequentially, these can be commented out.
from pydantic import BaseModel, Field
class CodeBlock(BaseModel):
    code_string: str = Field(description="The actual code content.")
    language: str = Field(default="python", description="The programming language of the code.")
class SolutionPackage(BaseModel):
    rationale: str = Field(description="A brief explanation of the code design and strategy.")
    function_code: CodeBlock = Field(description="The implementation of the required function(s).")
    test_code: CodeBlock = Field(description="The unit tests designed to validate the function_code.")


class MockExecutor:
    """Simulates the sandboxed execution of the generated tests."""
    def __init__(self):
        self.attempt_count = 0

    def run_tests(self, solution_path: str, test_path: str) -> Dict[str, Any]:
        """
        Simulates execution. Fails on even attempts, succeeds on odd attempts.
        """
        if self.attempt_count % 2 != 0 and self.attempt_count < 4:
            # Simulated Failure (e.g., Assertion Error)
            return {
                'success': False,
                'stdout': 'Ran 3 tests in 0.001s\nFAILED (failures=1)',
                'stderr': 'AssertionError: Expected 6, got 5 in calculate_sum(3, 3).',
                'exit_code': 1,
                'reason': 'Test Failure: Assertion Error'
            }
        else:
            # Simulated Success (or forced success after a couple of failures)
            return {
                'success': True,
                'stdout': 'Ran 3 tests in 0.001s\nOK',
                'stderr': '',
                'exit_code': 0,
                'reason': 'Success'
            }

class MockGenerator:
    """Simulates the LLM generating code based on the prompt/feedback."""
    def __init__(self, initial_prompt: str):
        self.initial_prompt = initial_prompt
        self.current_code = ""

    def generate_solution(self, feedback_payload: Optional[Dict[str, Any]] = None) -> SolutionPackage:
        """
        Simulates generating a new SolutionPackage, incorporating feedback if provided.
        """
        if feedback_payload and feedback_payload.get('failure_type') != 'STYLE_ERROR':
            attempt_num = feedback_payload.get('attempt_number', 0)
            
            # Simulate a fix based on the previous error (e.g., adding a debugging offset)
            new_code = (
                f"# Attempt {attempt_num}: Fixed logic after receiving error report.\n"
                f"def calculate_sum(a, b):\n    # Previous error was assertion failure, adding correction.\n    return a + b + (attempt_num // 2)"
            )
            rationale = f"Attempt {attempt_num}: Correcting previous execution error based on trace: {feedback_payload['failure_reason']}."
        else:
            # Initial generation or style correction (which doesn't change execution logic)
            new_code = "def calculate_sum(a, b):\n    return a + b"
            rationale = "Initial implementation of the required summation function."

        self.current_code = new_code

        # Return a structured package
        return SolutionPackage(
            rationale=rationale,
            function_code=CodeBlock(code_string=new_code),
            test_code=CodeBlock(code_string="import unittest\nclass TestSum(unittest.TestCase):\n    def test_basic(self):\n        self.assertEqual(calculate_sum(1, 2), 3)\n    def test_six(self):\n        self.assertEqual(calculate_sum(3, 3), 6)")
        )

class RefinementOrchestrator:
    """Manages the iterative code generation and testing loop."""
    def __init__(self, initial_prompt: str, max_attempts: int = 3):
        self.initial_prompt = initial_prompt
        self.max_attempts = max_attempts
        self.generator = MockGenerator(initial_prompt)
        self.executor = MockExecutor()
        self.current_attempt = 0

    def _construct_feedback(self, prev_code: str, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """Creates the structured payload used to guide the next generation step."""
        feedback = {
            'prompt': self.initial_prompt,
            'previous_code': prev_code,
            'attempt_number': self.current_attempt,
            'failure_type': 'EXECUTION_ERROR', # Default failure type
            'failure_reason': execution_result['reason'],
            'test_output': {
                'stdout': execution_result['stdout'],
                'stderr': execution_result['stderr']
            }
        }
        return feedback

    def run_loop(self) -> Optional[SolutionPackage]:
        """Executes the iterative refinement loop."""
        feedback_payload: Optional[Dict[str, Any]] = None

        print(f"Starting Refinement Loop for: '{self.initial_prompt}'")
        print(f"Max Attempts: {self.max_attempts}\n")

        while self.current_attempt < self.max_attempts:
            self.current_attempt += 1
            print(f"--- Attempt {self.current_attempt} ---")

            # 1. GENERATE Code
            solution_package = self.generator.generate_solution(feedback_payload)
            current_code = solution_package.function_code.code_string

            print(f"Generated Rationale: {solution_package.rationale}")
            
            # Simulate file preparation (paths only)
            solution_path = "/tmp/solution.py"
            test_path = "/tmp/test_solution.py"

            # 2. EXECUTE Tests
            self.executor.attempt_count = self.current_attempt
            execution_result = self.executor.run_tests(solution_path, test_path)

            # 3. ANALYZE Results
            if execution_result['success']:
                print("\n[SUCCESS] Code passed all tests.")
                return solution_package
            else:
                print(f"[FAILURE] Reason: {execution_result['reason']}")
                # print(f"Test STDERR snippet: {execution_result['stderr'].splitlines()[-1]}")

                # 4. CONSTRUCT FEEDBACK for next iteration
                feedback_payload = self._construct_feedback(current_code, execution_result)

        print(f"\n[FAILURE] Maximum attempts ({self.max_attempts}) reached without success.")
        return None

# # Example Usage:
# orchestrator = RefinementOrchestrator(
#     initial_prompt="Write a function `calculate_sum(a, b)`.",
#     max_attempts=4
# )
# final_solution = orchestrator.run_loop()
# if final_solution:
#     print("\nFinal Working Code:\n", final_solution.function_code.code_string)
