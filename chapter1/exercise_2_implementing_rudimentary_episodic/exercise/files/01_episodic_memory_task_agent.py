import random

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

if __name__ == "__main__":
    run_task_agent()
