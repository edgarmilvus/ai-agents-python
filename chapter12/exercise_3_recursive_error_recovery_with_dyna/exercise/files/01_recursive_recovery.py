import re

# --- Custom Exceptions ---
class AgentError(Exception): pass

# --- Simulated LLM/Agent Interaction Functions (updated for this exercise) ---
def mock_llm_call(prompt: str, temperature: float = 0.1) -> str:
    """Simulates an LLM response based on prompt keywords."""
    prompt_lower = prompt.lower()
    
    if "code review" in prompt_lower:
        # The constraint text names the prohibited syntax, so the check has to
        # look at the code, not at the whole prompt.
        code = prompt_lower.split("code:", 1)[-1]
        if re.search(r"\[\s*\w+\s+for\s+", code):
            return "FAILURE: Code uses prohibited list comprehension syntax."
        return "SUCCESS: Code adheres to all constraints."

    # Default response for code generation (exercise 3)
    if "previous attempt failed" in prompt_lower:
        # Success on second attempt (no list comprehension)
        return "def process_data(data):\n    result = []\n    for item in data:\n        if item > 10:\n            result.append(item)\n    return result"
    
    # Failure on first attempt (uses list comprehension)
    return "def process_data(data):\n    return [item for item in data if item > 10]"


MAX_ATTEMPTS = 3

def code_review_agent(code: str, constraints: str) -> str:
    """Reflects on code quality based on constraints."""
    prompt = f"Perform a code review based on the constraint: '{constraints}'. Code:\n{code}"
    return mock_llm_call(prompt)

def recursive_task_solver(initial_prompt: str, constraints: str, attempt: int = 1):
    if attempt > MAX_ATTEMPTS:
        raise AgentError("Maximum self-correction attempts reached without success.")
    
    print(f"\n--- Attempt {attempt}/{MAX_ATTEMPTS} ---")
    
    # 3. Dynamic Prompt Generation: Augment the prompt based on previous failure context
    agent_prompt = initial_prompt
    if attempt > 1:
        # The initial_prompt has already been augmented in the previous recursive call
        print(f"  [AUGMENTED PROMPT] Using modified instructions for re-execution.")

    generated_code = mock_llm_call(agent_prompt, temperature=0.5)
    
    # 2. Reflection
    reflection_feedback = code_review_agent(generated_code, constraints)
    print(f"  [TRACE LOG] Generated Code:\n{generated_code.strip().splitlines()[0]}...")
    print(f"  [REFLECTION] Feedback: {reflection_feedback}")
    
    if reflection_feedback.startswith("SUCCESS"):
        print(f"  [SUCCESS] Task completed on attempt {attempt}.")
        print("Final Code:\n" + generated_code)
        return generated_code
    else:
        print(f"  [CORRECTION NEEDED] Modifying plan for next attempt...")
        
        # 3. Dynamic Prompt Generation: Synthesize feedback into a new directive prefix
        new_directive = f"Previous attempt failed: {reflection_feedback}. You MUST strictly adhere to the constraint: {constraints}. "
        
        # Recursive call with the augmented prompt
        recursive_task_solver(
            initial_prompt=new_directive + INITIAL_TASK,
            constraints=constraints,
            attempt=attempt + 1
        )

# Execution Setup
CONSTRAINTS = "The generated Python function must not use any list comprehensions."
INITIAL_TASK = "Write a Python function called 'process_data' that filters a list of numbers, keeping only those greater than 10."

try:
    print("--- exercise 3: Recursive Error Recovery ---")
    recursive_task_solver(INITIAL_TASK, CONSTRAINTS)
except AgentError as e:
    print(f"\n[FATAL ERROR] {e}")
