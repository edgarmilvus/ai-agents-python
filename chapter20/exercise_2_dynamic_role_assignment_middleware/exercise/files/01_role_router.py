# --- Agent Specialization for Exercise 2 ---

class DeveloperAgent(BaseAgent):
    """The agent responsible for generating and fixing artifacts."""
    async def _execute_development(self, requirements: Any) -> str:
        # Simulate variable workload
        work_time = random.uniform(0.3, 1.0)
        await asyncio.sleep(work_time)
        return f"Completed task: {requirements} by {self.name} in {work_time:.2f}s"

# --- Exercise 2: Dynamic Role Assignment Middleware Implementation ---

class TaskRouterMiddleware:
    """Routes tasks to the least-busy agent in a pool."""
    def __init__(self, agent_pool: List[DeveloperAgent]):
        self.agent_pool = agent_pool

    async def route_task(self, task_data: Any) -> Any:
        """Finds the least loaded agent and submits the task."""
        
        # 1. Find the least busy agent
        # Note: If tied, Python's min function selects the first one encountered, 
        # which is sufficient for rudimentary load balancing.
        least_busy_agent = min(self.agent_pool, key=lambda agent: agent.current_task_count)
        
        print(f"[ROUTER] Routing task to {least_busy_agent.name} (Tasks: {least_busy_agent.current_task_count})")
        
        # 2. Submit the task and await the result
        result_future = await least_busy_agent.submit_task(task_data)
        
        return await result_future

# --- Demonstration for Exercise 2 ---

async def main_ex2_demo():
    # Setup Agent Pool
    dev_pool = [DeveloperAgent(f"Dev_{i}") for i in range(1, 4)]
    router = TaskRouterMiddleware(dev_pool)
    
    # Start agent processing loops
    agent_tasks = [asyncio.create_task(dev.process_tasks()) for dev in dev_pool]
    
    # Submit tasks concurrently
    tasks_to_submit = [f"Feature {i}" for i in range(1, 10)]
    
    print("--- Starting Exercise 2 Demo: Dynamic Load Balancing ---")
    
    # Submit tasks quickly to overload the system and test routing
    submission_futures = []
    for task in tasks_to_submit:
        submission_futures.append(router.route_task(task))
        await asyncio.sleep(0.05) # Small delay to ensure agents start processing

    results = await asyncio.gather(*submission_futures)
    
    print("\n--- Load Balancing Results ---")
    for result in results:
        print(f" -> {result}")
        
    print("\n--- Final Agent Workloads ---")
    for dev in dev_pool:
        print(f"{dev.name}: {dev.current_task_count} tasks remaining (should be 0)")
        
    # Cancel processing loops
    for task in agent_tasks:
        task.cancel()
    print("--- Exercise 2 Demo Complete ---")

if __name__ == "__main__":
    asyncio.run(main_ex2_demo())
