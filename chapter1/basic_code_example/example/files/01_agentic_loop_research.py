import json
import os
import sys
import time
from typing import Dict, List

from openai import OpenAI

# --- 1. CONFIGURATION AND SETUP ---

# The client speaks the OpenAI wire format, so any OpenAI-compatible gateway
# works. OpenRouter is the default here, and the endpoint, the model and the key
# all come from the environment: no provider is hard-coded in the script.
BASE_URL = os.environ.get("OPENAI_COMPATIBLE_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("OPENAI_COMPATIBLE_MODEL", "~deepseek/deepseek-flash-latest")

try:
    client = OpenAI(
        base_url=BASE_URL,
        api_key=os.environ.get("OPENAI_COMPATIBLE_API_KEY"),
    )
except Exception as e:
    print(f"Error initializing the LLM client: {e}")
    print("Set OPENAI_COMPATIBLE_API_KEY before running this script.")
    sys.exit(1)

# Define the primary goal for the agent
PRIMARY_GOAL = (
    "Research the capital city of Brazil and the year it was officially founded. "
    "Once both facts are confirmed, generate a single, concise summary sentence."
)

# --- 2. AGENT SYSTEM PROMPT AND MEMORY ---

SYSTEM_PROMPT = """
You are a highly focused, autonomous research agent. Your sole purpose is to fulfill the PRIMARY_GOAL.
You operate in an iterative loop. Based on the current STATE and the ACTION_HISTORY, you must decide your next step.

Your output must always be a JSON object with two keys:

1. "next_action": A string describing the precise next research step required to move closer to the goal. 
2. "goal_achieved": A boolean (true or false). Set to true ONLY when the PRIMARY_GOAL is fully satisfied and the final synthesis is complete.

If "goal_achieved" is true, the "next_action" must contain the final summary sentence.
"""

# Agent memory structure (simplistic state tracking)
ACTION_HISTORY: List[Dict[str, str]] = []
CURRENT_STATE = "Goal initialized. Starting research."


# --- 3. THE AGENTIC LOOP FUNCTION ---

def run_agentic_loop(goal: str, max_iterations: int = 5) -> str:
    """
    Executes the iterative Observe-Orient-Decide-Act loop.
    """
    global CURRENT_STATE
    global ACTION_HISTORY

    # Every run starts from an empty memory: the state of a previous run
    # would otherwise leak into the first Observation of this one.
    ACTION_HISTORY = []
    CURRENT_STATE = "Goal initialized. Starting research."

    iteration = 0
    goal_achieved = False

    print(f"--- AGENT INITIATED ---")
    print(f"GOAL: {goal}")
    print("-" * 30)

    while not goal_achieved and iteration < max_iterations:
        iteration += 1
        print(f"\n[Iteration {iteration}/{max_iterations}]")
        
        # A. OBSERVE & ORIENT (Prepare the context for the LLM)
        # The agent observes the current state and history.
        context_messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"PRIMARY_GOAL: {goal}"},
            {"role": "user", "content": f"ACTION_HISTORY (last five steps): {ACTION_HISTORY[-5:]}"},
            {"role": "user", "content": f"CURRENT_STATE: {CURRENT_STATE}"}
        ]

        # B. DECIDE (LLM determines the next step)
        try:
            # We use a structured output request to force the JSON format
            response = client.chat.completions.create(
                model=MODEL,
                messages=context_messages,
                response_format={"type": "json_object"}
            )
        except Exception as e:
            return f"Error during decision phase: {e}"

        # C. PARSE THE DECISION (Act Preparation)
        try:
            # The response content is a JSON string, not Python source:
            # json.loads accepts it and cannot execute anything.
            decision_json = json.loads(response.choices[0].message.content)
            next_action = decision_json.get("next_action", "Error: No action defined.")
            goal_achieved = decision_json.get("goal_achieved", False)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error parsing JSON output: {e}. Raw response: {response.choices[0].message.content}")
            break

        # D. ACT (Simulate execution of the action)
        
        # Record the decision in history
        ACTION_HISTORY.append({
            "iteration": str(iteration),
            "decision": next_action
        })
        
        print(f"DECISION: {next_action}")

        if goal_achieved:
            # If goal achieved, the action contains the final answer
            CURRENT_STATE = f"Goal successfully completed. Final Answer: {next_action}"
            print(f"\n GOAL ACHIEVED ")
            return next_action
        
        else:
            # If not achieved, the agent executes the research step.
            # In a real agent, this would involve calling a Tool (e.g. Google Search, Code Interpreter).
            # Here, we simulate the tool result by asking the LLM to execute the action itself.
            
            execution_prompt = f"Execute the following research task precisely: '{next_action}'. Provide the factual result only."
            
            execution_response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a factual execution engine. Respond only with the requested fact."},
                    {"role": "user", "content": execution_prompt}
                ]
            )
            
            # Update the state based on the execution result
            execution_result = execution_response.choices[0].message.content.strip()
            CURRENT_STATE = f"Previous Action Result: {execution_result}. Now evaluate the remaining steps needed for the goal."
            print(f"RESULT: {execution_result}")
            
            # Wait briefly to simulate real-world latency
            time.sleep(0.5)

    if not goal_achieved:
        return f"Agent failed to achieve goal within {max_iterations} iterations. Final State: {CURRENT_STATE}"


if __name__ == "__main__":
    # --- 4. EXECUTION ---

    final_summary = run_agentic_loop(PRIMARY_GOAL)
    print("\n" + "="*50)
    print(f"FINAL OUTPUT: {final_summary}")
    print("="*50)
    print("\nFULL ACTION HISTORY:")
    for step in ACTION_HISTORY:
        print(f"[{step['iteration']}]: {step['decision']}")
