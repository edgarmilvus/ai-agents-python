import re
from typing import List, Tuple, Dict, Any, Optional

# Re-defining necessary classes for standalone execution (if not imported)
from pydantic import BaseModel, Field
class CodeBlock(BaseModel):
    code_string: str = Field(description="The actual code content.")
    language: str = Field(default="python", description="The programming language of the code.")
class SolutionPackage(BaseModel):
    rationale: str = Field(description="A brief explanation of the code design and strategy.")
    function_code: CodeBlock = Field(description="The implementation of the required function(s).")
    test_code: CodeBlock = Field(description="The unit tests designed to validate the function_code.")

# Mock components from Exercise 3 (simplified for integration)
class MockExecutor:
    def __init__(self): self.attempt_count = 0
    def run_tests(self, solution_path: str, test_path: str) -> Dict[str, Any]:
        # Succeeds on attempts 3 onwards
        if self.attempt_count >= 3:
            return {'success': True, 'stdout': 'OK', 'stderr': '', 'exit_code': 0, 'reason': 'Success'}
        else:
            return {'success': False, 'stdout': 'FAILED', 'stderr': 'AssertionError: Logic error.', 'exit_code': 1, 'reason': 'Test Failure'}

class MockGenerator:
    def __init__(self, initial_prompt: str):
        self.initial_prompt = initial_prompt
        self.current_code = ""

    def generate_solution(self, feedback_payload: Optional[Dict[str, Any]] = None) -> SolutionPackage:
        
        # Simulate agent learning: fix style if style error is present
        if feedback_payload and feedback_payload.get('failure_type') == 'STYLE_ERROR':
            new_code = "def calculate_sum(a, b):\n    # Style corrected\n    return a + b"
            rationale = f"Attempt {feedback_payload['attempt_number']}: Corrected PEP 8 violations (used snake_case)."
        else:
            # Code that will initially contain a style violation (for attempt 1)
            new_code = "def calculate_sum(a, b):\n    return a + b"
            rationale = "Initial implementation."
        
        # Tests remain consistent
        test_code = "import unittest\nclass TestSum(unittest.TestCase):\n    def test_basic(self):\n        self.assertEqual(calculate_sum(1, 2), 3)"
        
        self.current_code = new_code
        return SolutionPackage(rationale=rationale, function_code=CodeBlock(code_string=new_code), test_code=CodeBlock(code_string=test_code))


def check_style_compliance(code_string: str) -> Tuple[bool, List[str]]:
    """
    Simulates static analysis, specifically checking for CamelCase function or variable names.
    """
    errors = []
    
    # Check for CamelCase in function definitions (e.g., def MyFunction...)
    func_pattern = re.compile(r'^\s*def\s+([A-Z][a-zA-Z0-9_]*)\s*\(', re.MULTILINE)
    
    # Check for CamelCase in variable assignments (e.g., myVariable = ...)
    var_pattern = re.compile(r'\b([a-z]+[A-Z][a-zA-Z0-9_]*)\s*=', re.MULTILINE)

    # Check for function naming violations
    for match in func_pattern.finditer(code_string):
        errors.append(f"Function '{match.group(1)}' uses CamelCase. PEP 8 requires snake_case.")

    # Check for variable naming violations
    for match in var_pattern.finditer(code_string):
        errors.append(f"Variable '{match.group(1)}' uses mixed case. PEP 8 requires snake_case.")

    is_compliant = not errors
    return is_compliant, errors

class ExtendedOrchestrator:
    """
    Manages the iterative code generation and testing loop, including static analysis.
    """
    def __init__(self, initial_prompt: str, max_attempts: int = 5):
        self.initial_prompt = initial_prompt
        self.max_attempts = max_attempts
        self.generator = MockGenerator(initial_prompt)
        self.executor = MockExecutor()
        self.current_attempt = 0

    def _construct_execution_feedback(self, prev_code: str, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """Creates feedback for execution errors."""
        return {
            'prompt': self.initial_prompt,
            'previous_code': prev_code,
            'attempt_number': self.current_attempt,
            'failure_type': 'EXECUTION_ERROR',
            'failure_reason': execution_result['reason'],
            'test_output': {
                'stdout': execution_result['stdout'],
                'stderr': execution_result['stderr']
            }
        }

    def _construct_style_feedback(self, prev_code: str, style_errors: List[str]) -> Dict[str, Any]:
        """Creates feedback for style correction."""
        error_list = "\n".join([f"- {err}" for err in style_errors])
        return {
            'prompt': self.initial_prompt,
            'previous_code': prev_code,
            'attempt_number': self.current_attempt,
            'failure_type': 'STYLE_ERROR',
            'failure_reason': 'Code failed static analysis due to PEP 8 violations.',
            'style_report': error_list
        }

    def run_loop(self) -> Optional[SolutionPackage]:
        feedback_payload: Optional[Dict[str, Any]] = None

        print(f"Starting Extended Refinement Loop (Style Validation Enabled).")

        while self.current_attempt < self.max_attempts:
            self.current_attempt += 1
            print(f"\n--- Attempt {self.current_attempt} ---")

            # 1. GENERATE Code
            solution_package = self.generator.generate_solution(feedback_payload)
            current_code = solution_package.function_code.code_string
            
            # MOCK INJECTION: Force a style error on attempt 1 to demonstrate validation
            if self.current_attempt == 1:
                current_code = current_code.replace("calculate_sum", "CalculateSum")
                solution_package.function_code.code_string = current_code
                print("[MOCK] Injecting CamelCase style error.")

            print(f"Generated Rationale: {solution_package.rationale}")

            # 2. VALIDATE Style (New Step)
            is_compliant, style_errors = check_style_compliance(current_code)

            if not is_compliant:
                print(f"[STYLE FAILURE] Found {len(style_errors)} PEP 8 violation(s). Skipping execution.")
                
                # Construct style-specific feedback and loop again
                feedback_payload = self._construct_style_feedback(current_code, style_errors)
                continue # Skip execution and proceed to the next attempt

            # 3. EXECUTE Tests (Only if style is compliant)
            print("[STYLE SUCCESS] Code is PEP 8 compliant. Proceeding to execution.")
            
            solution_path = "/tmp/solution.py"
            test_path = "/tmp/test_solution.py"
            
            self.executor.attempt_count = self.current_attempt
            execution_result = self.executor.run_tests(solution_path, test_path)

            # 4. ANALYZE Execution Results
            if execution_result['success']:
                print("\n[SUCCESS] Code passed all tests.")
                return solution_package
            else:
                print(f"[EXECUTION FAILURE] Reason: {execution_result['reason']}")
                
                # Construct execution-specific feedback
                feedback_payload = self._construct_execution_feedback(current_code, execution_result)
                
        print(f"\n[FAILURE] Maximum attempts ({self.max_attempts}) reached.")
        return None

# # Example Usage demonstrating the flow:
# extended_orchestrator = ExtendedOrchestrator(
#     initial_prompt="Write a function for summation, ensuring strict PEP 8 compliance.",
#     max_attempts=5
# )
# final_solution = extended_orchestrator.run_loop()
