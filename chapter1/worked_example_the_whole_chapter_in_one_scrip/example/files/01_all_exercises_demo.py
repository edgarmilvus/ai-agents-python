import json
import random
import re

# Chapter 1 - the whole chapter in one script.
# Each exercise keeps the functions its own listing defines; the
# __main__ block at the bottom runs all four in sequence.


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

# --- Exercise 2: Rudimentary Episodic Memory ---

class EpisodicMemory:
    """Stores success/failure status of the last completed task."""
    def __init__(self):
        self.memory = {}
    
    def record_outcome(self, task_name, status):
        """Records the outcome of the task."""
        self.memory['last_task'] = task_name
        self.memory['last_status'] = status
        print(f"  [Memory] Recorded: {task_name} -> {status}")

    def get_last_status(self):
        """Retrieves the status of the last task."""
        return self.memory.get('last_status')

def simulate_task_execution(task_name):
    """Simulates a task with a 30% chance of failure."""
    if random.random() < 0.3:
        return 'Failure'
    return 'Success'

def task_agent_orient_decide(memory, current_task_name):
    """
    The Orient/Decide phase, incorporating memory lookup.
    """
    last_status = memory.get_last_status()
    
    if last_status == 'Failure':
        print(f"\n[Orient] Previous task failed. Prioritizing self-correction.")
        return 'Review Previous Failure'
    
    print(f"\n[Orient] Previous task successful. Proceeding with execution.")
    return f'Execute {current_task_name}'

def run_task_agent():
    tasks = [
        'Task A: Data Ingestion',
        'Task B: Model Training',
        'Task C: Deployment'
    ]
    memory = EpisodicMemory()
    task_index = 0
    
    # Initialize memory state to 'Success' so the first task executes immediately
    memory.record_outcome('Initialization', 'Success') 
    
    print("--- Starting State-Aware Task Agent ---")
    
    while task_index < len(tasks):
        current_task = tasks[task_index]
        
        # Orient/Decide Phase
        action = task_agent_orient_decide(memory, current_task)
        
        # Act Phase
        if action == 'Review Previous Failure':
            print(f"[Act] Performing mandatory review of failed task...")
            # Simulate review success (100% chance for simplicity)
            memory.record_outcome('Self-Correction Review', 'Success')
            # Task index does NOT increment, forcing a retry of the current task
            continue 
            
        elif action.startswith('Execute'):
            print(f"[Act] Attempting: {current_task}...")
            outcome = simulate_task_execution(current_task)
            memory.record_outcome(current_task, outcome)
            
            if outcome == 'Success':
                task_index += 1 # Move to the next task only on success
                print(f"  [Status] {current_task} completed successfully.")
            else:
                print(f"  [Status] {current_task} FAILED. Must review before retrying.")
                # Task index remains the same, forcing a review next loop.
                
    print("\n--- All Tasks Completed Successfully ---")

# --- Exercise 3: Rule-Based Tool Routing and Execution ---

# 1. Define Mock Tools
def financial_calculator(expression):
    """Mock tool for calculating math."""
    # A tool that evals whatever text reached it is an execution hole, so the
    # expression is checked before it is evaluated: digits, operators, spaces.
    if not re.fullmatch(r"[0-9+\-*/(). ]+", str(expression)):
        return "Calculation Tool Error: Invalid expression."
    try:
        result = eval(str(expression))
        return f"Calculation Tool Result: The result of {expression} is {result}."
    except Exception:
        return "Calculation Tool Error: Invalid expression."

def weather_api_lookup(city):
    """Mock tool for looking up weather."""
    if 'london' in city.lower():
        return f"Weather Tool Result: Current weather in {city}: 15°C and cloudy."
    return f"Weather Tool Result: Cannot find current weather data for {city}."

def database_query(query_string):
    """Mock tool for database retrieval."""
    if 'user data' in query_string.lower():
        return "DB Tool Result: Retrieved 1,500 records of user data from the main table."
    return "DB Tool Result: Query executed, but no specific data found."

# 2. Tool Manifest (Mapping keywords to functions)
TOOL_MANIFEST = {
    'calculate': financial_calculator,
    'weather': weather_api_lookup,
    'database': database_query
}

# Words the routing layer accepts in place of an operator
OPERATOR_WORDS = (
    ('multiplied by', '*'),
    ('divided by', '/'),
    ('times', '*'),
    ('plus', '+'),
    ('minus', '-'),
)

def route_query(query):
    """
    The Decide phase: Routes the query to the appropriate tool and extracts args.
    """
    query_lower = query.lower()
    
    if 'calculate' in query_lower or 'math' in query_lower:
        # Rewrite the operator words, then keep the arithmetic run. Splitting on
        # spaces and gluing the last three tokens together turns "5 times 12"
        # into "5times12", which is not an expression.
        expression = query_lower
        for word, operator in OPERATOR_WORDS:
            expression = expression.replace(word, operator)
        match = re.search(r"[0-9.][0-9.+\-*/() ]*", expression)
        if match:
            return 'calculate', match.group(0).strip()
        return 'calculate', '1+1' # Default if extraction fails
            
    elif 'weather' in query_lower or 'forecast' in query_lower:
        # Extract the city that follows the preposition "in". A word boundary
        # keeps the "in" of "Berlin" from splitting the city name.
        match = re.search(r"\bin\s+([A-Za-z][A-Za-z .'-]*)", query)
        if match:
            city = match.group(1).strip()
            return 'weather', city
        return 'weather', 'default city'
        
    elif 'database' in query_lower or 'retrieve' in query_lower:
        # Simple argument extraction for database
        return 'database', query
        
    return None, None

def execute_tool(tool_name, args):
    """
    The Act phase: Dynamically calls the selected tool.
    """
    if tool_name and tool_name in TOOL_MANIFEST:
        tool_function = TOOL_MANIFEST[tool_name]
        print(f"[Act] Invoking Tool: {tool_name} with arguments: '{args}'")
        
        # Handle tuple vs single argument call
        if isinstance(args, tuple):
            result = tool_function(*args)
        else:
            result = tool_function(args)
            
        return result
    else:
        return "Agent Decision: No appropriate tool found for this query."

def run_tool_router_agent(query):
    print(f"\n--- Processing Query: '{query}' ---")
    
    # Decide (Route)
    tool_name, args = route_query(query)
    
    # Act (Execute)
    result = execute_tool(tool_name, args)
    
    print(f"--- Final Agent Response ---\n{result}")
    return result

# --- Exercise 4: Interactive Challenge - Planning Layer for RAG ---

# 1. Planning Prompt Template (Simulated LLM Input)
PLANNING_PROMPT_TEMPLATE = """
As the Agent Planner, analyze the user query. Determine if the query requires external knowledge retrieval (RAG) or if it is a simple, direct question.
Output must be a JSON object with two keys:

1. "search_required": boolean (True if RAG is needed, False otherwise).
2. "refined_query": string (The optimized search query, or the original query if search is not needed).

User Query: {query}
"""

def simulate_llm_planning(user_query):
    """
    Simulates the LLM's Orient phase by parsing keywords and outputting structured JSON.
    """
    # Simple rule-based simulation of LLM intelligence
    query_lower = user_query.lower()
    
    if 'what is the capital' in query_lower or 'who is the ceo' in query_lower:
        # Simple factual query, no complex RAG needed
        search_required = False
        refined_query = user_query
    elif 'history of' in query_lower or 'technical specifications' in query_lower or 'compare and contrast' in query_lower:
        # Complex query likely requiring external knowledge
        search_required = True
        # Simple refinement: strip the introductory phrase that carries no
        # signal for the vector store, whatever its capitalisation.
        refined_query = re.sub(
            r"^what is the history of\s+", "", user_query, flags=re.IGNORECASE
        ).strip()
    else:
        # Default to search if uncertain
        search_required = True
        refined_query = user_query
        
    # Format output as if it came from the LLM based on the template
    planner_output = {
        "search_required": search_required,
        "refined_query": refined_query
    }
    
    print(f"[Planner Output Simulation]: {json.dumps(planner_output)}")
    return planner_output

def execute_rag(query):
    """
    Simulates the Act phase of the RAG system.
    """
    print(f"\n[RAG System Act] Performing semantic search using refined query: '{query}'...")
    print("...Retrieving relevant documents from vector store...")
    print("...Generating grounded response based on retrieved context...")
    return "RAG Result: Response successfully generated using external context."

def execute_direct_answer(query):
    """
    Simulates a direct, non-RAG response.
    """
    return f"Direct Answer Result: Answering simple query '{query}' using internal parametric knowledge."

def run_planning_agent(user_query):
    """
    Main agent loop incorporating the Planning/Orient step.
    """
    print(f"--- Agent Processing User Query: '{user_query}' ---")
    
    # 1. Orient/Decide Phase (Planning)
    planning_result = simulate_llm_planning(user_query)
    
    search_needed = planning_result['search_required']
    refined_query = planning_result['refined_query']
    
    # 2. Act Phase (Conditional Execution)
    if search_needed:
        print("\n[Decide] RAG is REQUIRED. Proceeding to execution.")
        final_response = execute_rag(refined_query)
    else:
        print("\n[Decide] RAG NOT required. Executing direct answer.")
        final_response = execute_direct_answer(user_query)
        
    print(f"\n--- Final Agent Action ---\n{final_response}")
    return final_response

# --- Execution Demonstration ---

if __name__ == '__main__':
    
    # Exercise 1 Execution
    print("===================================================")
    print("EXERCISE 1: OODA Loop Agent Simulation")
    run_resource_agent()
    print("===================================================\n")
    
    # Exercise 2 Execution
    print("===================================================")
    print("EXERCISE 2: State-Aware Task Agent (Memory)")
    # Note: Execution will loop and review if a task fails.
    run_task_agent()
    print("===================================================\n")

    # Exercise 3 Execution
    print("===================================================")
    print("EXERCISE 3: Rule-Based Tool Router")
    run_tool_router_agent("I need to calculate 5 times 12")
    run_tool_router_agent("What is the weather in London?")
    run_tool_router_agent("Retrieve user data from the database.")
    run_tool_router_agent("Tell me a joke.") # Should fail to route
    print("===================================================\n")

    # Exercise 4 Execution
    print("===================================================")
    print("EXERCISE 4: Planning Layer for RAG (Interactive Challenge)")
    
    # Case A: Simple query (no RAG needed)
    run_planning_agent("What is the capital of France?")
    
    # Case B: Complex query (RAG needed)
    run_planning_agent("What is the history of the early development of Python's GIL?")
    
    print("===================================================")
