import random
import json

# --- Exercise 1: OODA Loop Simulation ---

def observe(state):
    """
    Reads the current state and simulates environment input.
    """
    # Simulate available resources in the environment (1 to 5 units)
    available_resources = random.randint(1, 5)
    state['observation'] = available_resources
    state['iteration'] += 1
    print(f"\n--- Iteration {state['iteration']} ---")
    print(f"  [Observe] Available resources detected: {available_resources}")
    return state

def orient(state):
    """
    Analyzes observation against the goal. Determines the gap.
    """
    current_count = state['resource_count']
    required_goal = state['goal']
    gap = required_goal - current_count
    
    state['analysis'] = {
        'gap': gap,
        'is_goal_met': gap <= 0
    }
    
    if state['analysis']['is_goal_met']:
        print(f"  [Orient] Goal met. Total collected: {current_count}/{required_goal}.")
    else:
        print(f"  [Orient] Gap analysis: Need {gap} more units.")
        
    return state

def decide(state):
    """
    Determines the next action based on the analysis.
    """
    if state['analysis']['is_goal_met']:
        action = 'Terminate'
    else:
        # Decide to collect the available resources
        action = 'Collect Resource'
        
    state['action'] = action
    print(f"  [Decide] Chosen Action: {action}")
    return state

def act(state, action):
    """
    Executes the determined action and updates the world state.
    """
    if action == 'Collect Resource':
        collected = state['observation']
        state['resource_count'] += collected
        print(f"  [Act] Collecting {collected} units. New total: {state['resource_count']}")
    elif action == 'Terminate':
        # Only the Act phase ends the loop. Reaching the goal is something the
        # agent observes; stopping is a decision it then carries out.
        state['running'] = False
        print("  [Act] Termination signal received. Shutting down.")
        
    return state

def run_resource_agent():
    """Main loop for the OODA agent simulation."""
    world_state = {
        'resource_count': 0,
        'goal': 10,
        'iteration': 0,
        'running': True,
        'observation': 0,
        'analysis': {},
        'action': None
    }
    
    print("--- Starting Resource Collector Agent (OODA) ---")
    while world_state['running']:
        # 1. Observe
        world_state = observe(world_state)
        
        # 2. Orient
        world_state = orient(world_state)
        
        # 3. Decide
        world_state = decide(world_state)
        
        # 4. Act
        world_state = act(world_state, world_state['action'])

    print("\n--- Agent Execution Complete ---")

if __name__ == "__main__":
    run_resource_agent()
