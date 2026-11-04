from pydantic import BaseModel, Field, ValidationError
import json
import os
import tempfile
from typing import Dict, Any, Optional, Tuple

class CodeBlock(BaseModel):
    """Represents a block of code with its language."""
    code_string: str = Field(description="The actual code content.")
    language: str = Field(default="python", description="The programming language of the code.")

class SolutionPackage(BaseModel):
    """The complete structured output expected from the LLM agent."""
    rationale: str = Field(description="A brief explanation of the code design and strategy.")
    function_code: CodeBlock = Field(description="The implementation of the required function(s).")
    test_code: CodeBlock = Field(description="The unit tests designed to validate the function_code.")

def parse_agent_output(json_output: str) -> Optional[SolutionPackage]:
    """
    Parses and validates the raw JSON output from the LLM against the defined schema.
    """
    try:
        data = json.loads(json_output)
        package = SolutionPackage.model_validate(data)
        return package
    except ValidationError as e:
        print(f"Validation Error: The LLM output did not match the required schema.")
        # print(f"Details: {e}") # Uncomment for full traceback
        return None
    except json.JSONDecodeError:
        print("JSON Decode Error: The output was not valid JSON.")
        return None

def prepare_files_for_execution(package: SolutionPackage) -> Tuple[str, str]:
    """
    Saves the function code and test code to temporary files for sandboxed execution.
    Returns the paths to the saved files (solution_path, test_path).
    """
    # Define paths in the system's temporary directory
    solution_path = os.path.join(tempfile.gettempdir(), "solution_agent.py")
    test_path = os.path.join(tempfile.gettempdir(), "test_solution_agent.py")

    # 1. Create the solution file
    with open(solution_path, 'w') as f:
        f.write(package.function_code.code_string)

    # 2. Create the test file, ensuring it can import the solution
    temp_dir = tempfile.gettempdir().replace("\\", "/") # Handle Windows paths
    test_content = (
        f"import sys\n"
        f"sys.path.append(r'{temp_dir}')\n"
        f"import solution_agent as solution_module\n"
        f"from solution_agent import *\n" # Import all definitions for unittest access
        f"{package.test_code.code_string}"
    )
    with open(test_path, 'w') as f:
        f.write(test_content)

    return solution_path, test_path

# # Simulation Example:
# simulated_llm_json = """
# {
#   "rationale": "Uses recursion for factorial calculation.",
#   "function_code": {
#     "code_string": "def factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n - 1)"
#   },
#   "test_code": {
#     "code_string": "import unittest\nclass TestFactorial(unittest.TestCase):\n    def test_five(self):\n        self.assertEqual(factorial(5), 120)\n"
#   }
# }
# """
# parsed_package = parse_agent_output(simulated_llm_json)
# if parsed_package:
#     solution_file, test_file = prepare_files_for_execution(parsed_package)
#     # print(f"Files prepared: Solution at {solution_file}, Tests at {test_file}")
#     # os.remove(solution_file)
#     # os.remove(test_file)
