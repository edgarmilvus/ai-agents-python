import random
import time
from typing import Dict, Any

# 1. Define the Tool
def check_server_status(server_id: str) -> str:
    """Checks the current operational status and load of a specified server."""
    
    # Simulate status changes over time/calls
    if not hasattr(check_server_status, 'call_count'):
        check_server_status.call_count = 0
    
    check_server_status.call_count += 1
    
    if check_server_status.call_count <= 2:
        # Initial status is poor, forcing iteration
        status = "Degraded"
        load = random.randint(60, 90)
    else:
        # Status eventually improves
        status = random.choice(["Operational", "Testing"])
        load = random.randint(10, 85)
        if status == "Operational" and load < 50:
             # Target state reached
             load = random.randint(10, 49)
    
    time.sleep(0.5) # Simulate network latency
    
    return f"Server {server_id} Status: {status}, Current Load: {load}%"

# 2. Agent Execution (Conceptual structure, requires LLM framework setup)
# This block illustrates the required logic flow, assuming a framework like LangChain/LlamaIndex is used.

def run_react_simulation(agent_executor: Any):
    """
    Runs the ReAct agent simulation until the desired state is reached.
    Goal: Find status 'Operational' AND Load < 50%.
    """
    
    # The agent prompt must incorporate the goal and the tool description.
    prompt_input = (
        "Monitor server 'SRV-001'. You must continuously check its status "
        "using the 'check_server_status' tool until the status is 'Operational' "
        "AND the 'Current Load' is strictly less than 50%. "
        "Do not stop until both conditions are met. Start now."
    )
    
    # In a real environment, agent_executor.run() handles the Thought/Action/Observation loop internally.
    # The exercise requires the student to set up the prompt and tool definition 
    # such that the LLM *chooses* to iterate multiple times.
    
    # Example execution (conceptual):
    # result = agent_executor.run(prompt_input)
    # print(result)

# The student's task is to define the full agent setup (LLM, tools, executor) 
# and verify the output shows multiple Thought/Action/Observation cycles.
