import asyncio
from typing import Dict, Any, List

# --- 1. Mock LLM Interaction Layer ---
async def mock_llm_call(prompt: str, role: str) -> Dict[str, Any]:
    """
    Simulates an asynchronous call to a sophisticated LLM service.
    This uses 'await asyncio.sleep' to model the I/O bound nature 
    of network requests, relating directly to the concept of Futures and Awaitables.
    """
    await asyncio.sleep(0.1) 
    
    # The mode is in `role` ("QualityAssurance/execute_test"); the state of the
    # code is in `prompt`. Mixing the two is why this mock used to answer every
    # call with its error branch.
    if "ProductOwner" in role:
        # PO clarifies the high-level goal into structured requirements
        return {
            "requirements": [
                "Implement a Flask endpoint '/fibonacci/{n}'",
                "The endpoint must accept an integer 'n' (max 20)",
                "Return the nth Fibonacci number as JSON: {'n': n, 'result': value}"
            ]
        }
    elif "Developer" in role:
        if "Refinement" in prompt:
            # Corrected code generation based on QA feedback (iterative)
            return {
                "code": "def fib(n):\n    # Optimized iterative implementation after bug fix\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return a",
                "status": "Refined Code"
            }
        # Initial code generation (intentionally buggy for demonstration)
        return {
            "code": "def fib(n):\n    # Initial naive recursive implementation\n    if n <= 1: return n\n    return fib(n-1) + fib(n-2)",
            "status": "Initial Draft"
        }
    elif "QualityAssurance" in role and role.endswith("test_suite"):
        # QA generates the test suite based on requirements
        return {
            "test_suite": [
                {"input": 0, "expected": 0},
                {"input": 1, "expected": 1},
                {"input": 5, "expected": 5}, 
                {"input": 7, "expected": 13}
            ]
        }
    elif "QualityAssurance" in role and role.endswith("execute_test"):
        # QA simulates execution. The refined code carries a marker the mock reads.
        if "Optimized iterative" in prompt:
            return {"test_results": [{"test": "All tests", "passed": True}], "overall_pass": True}
        return {
            "test_results": [
                {"test": "input 5", "passed": False, "reason": "Expected 5, Got 8 (index error in the recursive implementation)"},
                {"test": "input 7", "passed": True}
            ],
            "overall_pass": False
        }
    return {"error": "Unknown role or state"}

# --- 2. Agent Definitions ---

class ProductOwner:
    def __init__(self, goal: str):
        self.goal = goal
    
    async def define_requirements(self) -> List[str]:
        """Translates the high-level goal into actionable, measurable requirements."""
        print("[PO] Analyzing high-level goal and translating to user stories...")
        response = await mock_llm_call(f"Clarify requirements for: {self.goal}", "ProductOwner")
        return response.get("requirements", [])

class Developer:
    async def develop_code(self, requirements: List[str], feedback: str = None) -> str:
        """Generates or refines application code based on input."""
        if feedback:
            print(f"[DEV] Refining code based on QA feedback: {feedback[:50]}...")
            prompt = f"Refinement needed: {feedback}"
        else:
            print("[DEV] Generating initial draft based on PO requirements.")
            prompt = f"Requirements: {requirements}"
            
        response = await mock_llm_call(prompt, "Developer")
        return response.get("code", "Error generating code.")

class QualityAssurance:
    async def generate_tests(self, code: str) -> List[Dict]:
        """Creates a comprehensive test suite based on the provided code structure and implicit requirements."""
        print("[QA] Generating test suite...")
        response = await mock_llm_call(f"Generate tests for code: {code}", "QualityAssurance/test_suite")
        return response.get("test_suite", [])

    async def execute_tests(self, code: str, test_suite: List[Dict]) -> Dict[str, Any]:
        """Simulates running the tests and providing structured feedback (pass/fail/bug report)."""
        print("[QA] Executing tests against code...")
        # The prompt includes the code to allow the mock LLM to simulate the failure state based on the code's complexity/bugs.
        response = await mock_llm_call(f"Execute test suite {test_suite} on code: {code}", "QualityAssurance/execute_test")
        return response

# --- 3. Swarm Coordinator and Execution ---

class SoftwareAgencySwarm:
    def __init__(self, high_level_goal: str):
        self.goal = high_level_goal
        self.po = ProductOwner(high_level_goal)
        self.dev = Developer()
        self.qa = QualityAssurance()
        self.max_iterations = 3
        self.last_feedback = None
        
    async def execute_development_cycle(self) -> str:
        """Manages the sequential, yet asynchronous, iterative feedback loop."""
        
        # 1. Requirement Definition (PO is the initial producer)
        requirements = await self.po.define_requirements()
        print(f"\n[Coordinator] Defined Requirements: {requirements}")
        
        current_code = ""
        
        for iteration in range(1, self.max_iterations + 1):
            print(f"\n--- ITERATION {iteration} ---")
            
            # 2. Development (DEV consumes requirements or feedback)
            feedback = self.last_feedback if iteration > 1 and self.last_feedback else None
            current_code = await self.dev.develop_code(requirements, feedback)
            
            # 3. Test Suite Generation & Execution (QA consumes code)
            test_suite = await self.qa.generate_tests(current_code)
            test_result = await self.qa.execute_tests(current_code, test_suite)
            
            if test_result.get("overall_pass"):
                print("\n[Coordinator] SUCCESS! QA passed the code. Delivery approved.")
                return current_code
            else:
                # 4. Feedback Loop Activation
                self.last_feedback = f"Failed tests: {test_result.get('test_results')}"
                print(f"[Coordinator] FAILURE detected. Sending structured feedback back to Developer for refinement.")
                
        return f"Failed to reach consensus after {self.max_iterations} iterations. Last code: {current_code}"

async def main():
    goal = "Create a robust Python API endpoint for calculating Fibonacci numbers."
    agency = SoftwareAgencySwarm(goal)
    final_output = await agency.execute_development_cycle()
    
    print("\n==================================")
    print("FINAL DELIVERABLE:")
    print(final_output)
    print("==================================")

if __name__ == "__main__":
    # The use of asyncio.run ensures the main function executes in the event loop, 
    # managing all the internal awaitable operations.
    asyncio.run(main())
