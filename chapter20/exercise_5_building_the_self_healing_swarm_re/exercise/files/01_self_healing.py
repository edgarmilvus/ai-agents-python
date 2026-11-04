# --- Exercise 5: Supervisor Agent Implementation ---

class SupervisorAgent:
    """Monitors agent health and initiates recovery."""
    def __init__(self, monitored_agents: List[BaseAgent]):
        self.monitored_agents = monitored_agents

    async def run_monitoring(self):
        print("[SUPERVISOR] Starting health monitoring...")
        while True:
            await asyncio.sleep(1.0) # Check every second
            
            for i, agent in enumerate(self.monitored_agents):
                try:
                    # Use asyncio.wait_for for strict timeout enforcement
                    # Timeout is set low (0.5s) to catch the simulated 2.0s delay
                    await asyncio.wait_for(agent.check_health(), timeout=0.5)
                    # print(f"[SUPERVISOR] {agent.name}: Health OK.")
                
                except asyncio.TimeoutError:
                    print(f"\n[SUPERVISOR] CRITICAL: {agent.name} timed out (>{0.5}s). Initiating recovery.")
                    await self._recover_agent(i)
                except Exception as e:
                    print(f"\n[SUPERVISOR] CRITICAL: {agent.name} failed with error: {type(e).__name__}. Initiating recovery.")
                    await self._recover_agent(i)

    async def _recover_agent(self, index: int):
        """Simulates replacing a failed agent instance."""
        failed_agent = self.monitored_agents[index]
        print(f"[SUPERVISOR] INFO: Provisioning new instance for {failed_agent.name}.")
        
        # Determine the type of replacement needed
        if isinstance(failed_agent, DeveloperAgent):
            new_agent = DeveloperAgent(f"Dev_Replica_{random.randint(100, 999)}")
        elif isinstance(failed_agent, QAAgent):
            new_agent = QAAgent(f"QA_Replica_{random.randint(100, 999)}")
        else:
            return

        # Replace the agent in the monitored list
        self.monitored_agents[index] = new_agent
        print(f"[SUPERVISOR] SUCCESS: {failed_agent.name} replaced by {new_agent.name}.")
        
        # Start the task processing loop for the new agent
        asyncio.create_task(new_agent.process_tasks())
        
        # Crucially, reset the failure flag on the new agent
        new_agent.is_responsive = True
        
        # We can also turn off the failure flag on the old agent to stop its long sleep
        failed_agent.is_responsive = True

# --- Demonstration for Exercise 5 ---

async def main_ex5_demo():
    dev1 = DeveloperAgent("Dev_Alpha")
    dev1.is_responsive = False # Force failure (2.0s sleep) on the first health check
    qa1 = QAAgent("QA_Beta")
    
    # Start agent processing loops
    asyncio.create_task(dev1.process_tasks())
    asyncio.create_task(qa1.process_tasks())
    
    supervisor = SupervisorAgent([dev1, qa1])
    monitoring_task = asyncio.create_task(supervisor.run_monitoring())
    
    print("--- Starting Exercise 5 Demo: Self-Healing Swarm ---")
    print(f"Initial Developer Agent: {dev1.name}. Forced to fail heartbeat.")
    
    # Let the supervisor run for a few seconds to detect and recover
    await asyncio.sleep(4.0)
    
    print("\n--- Final Agent Status ---")
    print(f"Monitored Agents: {[agent.name for agent in supervisor.monitored_agents]}")
    
    # Example of submitting a task to the recovered agent
    if len(supervisor.monitored_agents) > 0 and supervisor.monitored_agents[0].name.startswith("Dev_Replica"):
        new_dev = supervisor.monitored_agents[0]
        print(f"\nSubmitting task to new agent: {new_dev.name}")
        result = await new_dev.run_task("Test task after recovery")
        print(f"Task result: {result}")
        
    monitoring_task.cancel()
    print("--- Exercise 5 Demo Complete ---")

# --- Consolidated Main Execution ---

async def main():
    # Uncomment the desired exercise demonstration below:
    
    # await main_ex1_demo()
    # await main_ex2_demo()
    # await main_ex3_demo()
    # await main_ex4_demo()
    await main_ex5_demo()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting.")
    except asyncio.CancelledError:
        # Expected when cancelling monitoring tasks
        pass
