import random
import textwrap
import time
from typing import Dict, Any, Callable, List

# 1. Define the Tool (as provided, ensuring iteration)
def check_server_status(server_id: str) -> str:
    """Checks the current operational status and load of a specified server."""
    
    if not hasattr(check_server_status, 'call_count'):
        check_server_status.call_count = 0
    
    check_server_status.call_count += 1
    
    status = ""
    load = 0
    
    if check_server_status.call_count <= 2:
        # Initial status is poor, forcing iteration
        status = "Degraded"
        load = random.randint(60, 90)
    else:
        # Status eventually improves. We guarantee the target state on the 4th call.
        if check_server_status.call_count == 4:
            status = "Operational"
            load = random.randint(10, 49) # Target state reached
        else:
            status = random.choice(["Operational", "Testing", "Degraded"])
            load = random.randint(10, 85)
    
    time.sleep(0.01) # Minimal delay
    
    return f"Server {server_id} Status: {status}, Current Load: {load}%"

# 2. Agent Initialization & Prompt Definition
REACT_PROMPT = textwrap.dedent("""
You are a monitoring agent. Your goal is to find the status of server 'SRV-001' where the 'Status' is 'Operational' AND the 'Current Load' is strictly less than 50%.
You have one tool: check_server_status(server_id: str).

Follow the Thought/Action/Observation structure. If the condition is not met, you MUST continue checking.
When the condition is met, provide the final Answer.
""")

# 3. The Iterative Loop Simulation
def simulate_react_loop(tool: Callable, server_id: str = 'SRV-001'):
    """Simulates the ReAct loop based on the tool's output."""
    
    print(f"--- Starting ReAct Monitoring Loop for {server_id} ---")
    
    # Reset call count for simulation
    check_server_status.call_count = 0
    
    max_steps = 5
    trace: List[str] = []
    
    for step in range(1, max_steps + 1):
        print(f"\n--- STEP {step} ---")
        
        # --- Thought (Simulated LLM Reasoning) ---
        thought = f"The goal is not yet met. I must use the tool to check the server status again."
        if step == 1:
             thought = "Initial check required. I will use the check_server_status tool."
        
        trace.append(f"Thought: {thought}")
        print(f"Thought: {thought}")
        
        # --- Action (Simulated LLM Tool Call) ---
        action = f"check_server_status(server_id='{server_id}')"
        trace.append(f"Action: {action}")
        print(f"Action: {action}")
        
        # --- Observation (Tool Execution) ---
        observation = tool(server_id)
        trace.append(f"Observation: {observation}")
        print(f"Observation: {observation}")
        
        # Parse observation for conditional check
        if "Operational" in observation and "Load: " in observation:
            try:
                load_str = observation.split("Load: ")[1].split("%")[0]
                current_load = int(load_str)
                
                if "Operational" in observation and current_load < 50:
                    # Stopping Condition Met
                    final_answer = (
                        f"Answer: The server '{server_id}' is now in the target state. "
                        f"Status is Operational and Load is {current_load}% (< 50%). "
                        "Monitoring complete."
                    )
                    trace.append(final_answer)
                    print(f"\n{final_answer}")
                    return trace
            except ValueError:
                pass # Continue if parsing fails
        
        if step == max_steps:
             print("\nMaximum steps reached without meeting the goal.")
             return trace

# Run the simulation
simulation_trace = simulate_react_loop(check_server_status)
