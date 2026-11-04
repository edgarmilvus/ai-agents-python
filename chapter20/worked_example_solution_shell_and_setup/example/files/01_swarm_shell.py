import asyncio
import random
from typing import Literal, Any, Dict, List, Optional
from pydantic import BaseModel, Field

# --- Pydantic Models for Structured Communication (Exercises 1, 3, 4) ---

class ProjectState(BaseModel):
    """Defines the centralized, structured state of the project."""
    status: str = Field(default='REQUIREMENTS_GATHERING')
    current_artifact: Optional[str] = None
    version: int = Field(default=0)
    bug_count: int = Field(default=0)

class BugReport(BaseModel):
    """Structured output for the QA Agent (Exercise 3)."""
    bug_id: int = Field(default_factory=lambda: random.randint(1000, 9999))
    severity: Literal['CRITICAL', 'MAJOR', 'MINOR']
    description: str
    steps_to_reproduce: List[str]
    suggested_fix_summary: str

class SecurityViolation(BaseModel):
    """Structured output for the Security Auditor Agent (Exercise 4)."""
    violation_id: int = Field(default_factory=lambda: random.randint(500, 999))
    vulnerability_type: str
    risk_level: Literal['HIGH', 'MEDIUM', 'LOW']
    vulnerable_code_snippet: str
    remediation_instruction: str

# --- Exercise 1: Swarm State Hub ---

class SwarmStateHub:
    """
    Centralized, thread-safe manager for ProjectState using asyncio.Lock and Futures.
    """
    def __init__(self):
        self._state = ProjectState()
        self._lock = asyncio.Lock()
        # Map: {target_status: [list_of_futures_waiting]}
        self._waiting_futures: Dict[str, List[asyncio.Future]] = {}

    async def get_state(self) -> ProjectState:
        """Retrieves the current state safely."""
        async with self._lock:
            return self._state.model_copy(deep=True)

    async def update_state(self, new_data: Dict[str, Any]):
        """Updates the state and resolves any waiting futures."""
        async with self._lock:
            old_status = self._state.status
            
            # Update state model
            updated_state = self._state.model_copy(update=new_data)
            updated_state.version += 1
            self._state = updated_state
            
            print(f"[HUB] State updated to: {self._state.status} (V{self._state.version})")

            # Check for and resolve waiting futures
            if self._state.status != old_status and self._state.status in self._waiting_futures:
                futures_to_resolve = self._waiting_futures.pop(self._state.status)
                for future in futures_to_resolve:
                    if not future.done():
                        future.set_result(self._state.model_copy(deep=True))

    async def wait_for_status(self, target_status: str) -> ProjectState:
        """Pauses execution until the state transitions to the target status."""
        async with self._lock:
            if self._state.status == target_status:
                return self._state.model_copy(deep=True)
            
            # Create a new future and register it
            future = asyncio.Future()
            if target_status not in self._waiting_futures:
                self._waiting_futures[target_status] = []
            self._waiting_futures[target_status].append(future)
            
        # Await the future outside the lock
        return await future

# --- Base Agent Class for Exercises 2, 4, 5 ---

class BaseAgent:
    """Base class providing common agent functionality."""
    def __init__(self, name: str):
        self.name = name
        self.task_queue = asyncio.Queue()
        self.current_task_count = 0
        self.is_responsive = True

    async def submit_task(self, task_data: Any) -> asyncio.Future:
        """Submits a task to the agent's internal queue."""
        future = asyncio.Future()
        await self.task_queue.put((task_data, future))
        self.current_task_count += 1
        return future

    async def run_task(self, task_data: Any) -> Any:
        """Submits a task and waits for the result, not just the future."""
        future = await self.submit_task(task_data)
        return await future

    async def process_tasks(self):
        """Simulates continuous task processing."""
        while True:
            task_data, future = await self.task_queue.get()
            print(f"[{self.name}] Starting task processing...")
            
            # Simulated work
            await asyncio.sleep(0.1)
            
            # Handle structured feedback (Exercise 3/4 integration)
            if isinstance(task_data, (BugReport, SecurityViolation)):
                print(f"[{self.name}] Entering Refinement Cycle based on report.")
                result = await self._handle_refinement(task_data)
            else:
                result = await self._execute_development(task_data)
            
            future.set_result(result)
            self.current_task_count -= 1
            self.task_queue.task_done()

    async def _execute_development(self, requirements: Any) -> str:
        """Placeholder for initial development."""
        return f"Artifact_v{random.randint(1, 10)}_InitialCode"

    async def _handle_refinement(self, report: Any) -> str:
        """Placeholder for handling structured feedback."""
        print(f"[{self.name}] Adapting plan based on: {report.suggested_fix_summary if isinstance(report, BugReport) else report.remediation_instruction}")
        await asyncio.sleep(0.5)
        return f"Artifact_v{random.randint(10, 20)}_FixedCode"

    # Health Check for Exercise 5
    async def check_health(self):
        """Provides a simulated heartbeat check."""
        if not self.is_responsive:
            # Simulate intentional non-response/failure
            await asyncio.sleep(2.0)
            raise ConnectionError(f"{self.name} is unresponsive.")
            
        await asyncio.sleep(0.05) # Quick check
        return {"status": "OK", "agent": self.name}

# --- Exercise 2: Dynamic Role Assignment Middleware ---

class TaskRouterMiddleware:
    """Routes tasks to the least-busy agent in a pool."""
    def __init__(self, agent_pool: List[BaseAgent]):
        self.agent_pool = agent_pool

    async def route_task(self, task_data: Any) -> Any:
        """Finds the least loaded agent and submits the task."""
        
        # 1. Find the least busy agent
        least_busy_agent = min(self.agent_pool, key=lambda agent: agent.current_task_count)
        
        print(f"[ROUTER] Routing task to {least_busy_agent.name} (Tasks: {least_busy_agent.current_task_count})")
        
        # 2. Submit the task and await the result
        result_future = await least_busy_agent.submit_task(task_data)
        
        return await result_future

# --- Exercise 4: Specialized Agents and Orchestration ---

class DeveloperAgent(BaseAgent):
    """The agent responsible for generating and fixing artifacts."""
    pass

class QAAgent(BaseAgent):
    """The agent responsible for quality assurance and bug reporting."""
    async def _execute_development(self, artifact: str) -> Any:
        """Simulates QA testing, potentially generating a BugReport."""
        print(f"[{self.name}] Testing artifact: {artifact}")
        await asyncio.sleep(0.3)
        
        # 50% chance of passing, 50% chance of failing
        if random.random() < 0.5:
            print(f"[{self.name}] Artifact passed QA.")
            return {"status": "QA_PASS", "artifact": artifact}
        else:
            report = BugReport(
                severity='MAJOR',
                description=f"UI element misalignment in {artifact}.",
                steps_to_reproduce=["1. Load page", "2. Click button X"],
                suggested_fix_summary="Adjust CSS padding on main container."
            )
            print(f"[{self.name}] Artifact FAILED QA. Generating Bug Report.")
            return report

class SecurityAuditorAgent(BaseAgent):
    """The new agent for mandatory security review (Exercise 4)."""
    async def _execute_development(self, artifact: str) -> Any:
        """Simulates security audit, potentially generating a SecurityViolation."""
        print(f"[{self.name}] Auditing artifact: {artifact}")
        await asyncio.sleep(0.2)
        
        # 30% chance of failure
        if random.random() < 0.3:
            violation = SecurityViolation(
                vulnerability_type="SQL Injection Risk",
                risk_level='HIGH',
                vulnerable_code_snippet="SELECT * FROM users WHERE id='{user_id}'",
                remediation_instruction="Use parameterized queries immediately."
            )
            print(f"[{self.name}] Security Audit FAILED. Generating Violation Report.")
            return violation
        else:
            print(f"[{self.name}] Security Audit PASSED.")
            return {"status": "SECURITY_PASS", "artifact": artifact}

async def capstone_orchestrator():
    """
    Simplified Orchestrator for the Security Auditor Challenge (Exercise 4).
    This function manages the complex routing logic.
    """
    # Setup Agents
    dev_agent = DeveloperAgent("Dev_A")
    qa_agent = QAAgent("QA_1")
    sec_agent = SecurityAuditorAgent("Sec_Audit_1")
    
    # Start agent processing loops
    asyncio.create_task(dev_agent.process_tasks())
    asyncio.create_task(qa_agent.process_tasks())
    asyncio.create_task(sec_agent.process_tasks())
    
    # Initial task submission (Simulated PO input)
    current_artifact = await dev_agent.run_task("Initial requirements: Build a login page.")
    
    max_iterations = 5
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")
        
        # 1. Mandatory Security Audit
        audit_result = await sec_agent.run_task(current_artifact)
        
        if isinstance(audit_result, SecurityViolation):
            print("[ORCHESTRATOR] Security Violation detected. Rerouting to Developer for remediation.")
            current_artifact = await dev_agent.run_task(audit_result)
            continue # Restart loop for re-audit

        # 2. Quality Assurance Check (Only if Security Passed)
        qa_result = await qa_agent.run_task(audit_result['artifact'])
        
        if isinstance(qa_result, BugReport):
            print("[ORCHESTRATOR] QA Bug Report received. Rerouting to Developer for fix.")
            current_artifact = await dev_agent.run_task(qa_result)
            continue # Restart loop for re-audit (must go through security again)
        
        # 3. Successful Delivery
        print("\n[ORCHESTRATOR] SUCCESS: Artifact passed Security and QA.")
        print(f"Final Artifact Delivered: {qa_result['artifact']}")
        break
    
    if iteration >= max_iterations:
        print("[ORCHESTRATOR] FAILURE: Max iterations reached. Project halted.")

# --- Exercise 5: Supervisor Agent and Resilience ---

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
                    health_status = await asyncio.wait_for(agent.check_health(), timeout=0.5)
                    # print(f"[SUPERVISOR] {agent.name}: Health OK.")
                
                except asyncio.TimeoutError:
                    print(f"[SUPERVISOR] CRITICAL: {agent.name} timed out during heartbeat check.")
                    await self._recover_agent(i)
                except Exception as e:
                    print(f"[SUPERVISOR] CRITICAL: {agent.name} failed with error: {e}")
                    await self._recover_agent(i)

    async def _recover_agent(self, index: int):
        """Simulates replacing a failed agent instance."""
        failed_agent = self.monitored_agents[index]
        print(f"[SUPERVISOR] INFO: Initiating replacement for {failed_agent.name}.")
        
        # Determine the type of replacement needed
        if isinstance(failed_agent, DeveloperAgent):
            new_agent = DeveloperAgent(f"Dev_Replica_{random.randint(100, 999)}")
        elif isinstance(failed_agent, QAAgent):
            new_agent = QAAgent(f"QA_Replica_{random.randint(100, 999)}")
        else:
            print(f"ERROR: Unknown agent type {type(failed_agent)}")
            return

        # Replace the agent in the monitored list
        self.monitored_agents[index] = new_agent
        print(f"[SUPERVISOR] SUCCESS: {failed_agent.name} replaced by {new_agent.name}.")
        
        # Crucially, start the task processing loop for the new agent
        asyncio.create_task(new_agent.process_tasks())
        
        # Note: In a real system, tasks held by the failed agent would need to be
        # recovered and reassigned to the new agent instance.

# --- Example Execution Block (Uncomment to test specific exercises) ---

async def main():
    
    # --- Exercise 1 Demonstration ---
    # hub = SwarmStateHub()
    # async def po_task():
    #     await asyncio.sleep(0.5)
    #     await hub.update_state({"status": "IN_DEVELOPMENT"})
    #     await asyncio.sleep(0.5)
    #     await hub.update_state({"status": "QA_FAILED", "bug_count": 5})

    # async def dev_task():
    #     print("[DEV] Waiting for IN_DEVELOPMENT status...")
    #     state = await hub.wait_for_status("IN_DEVELOPMENT")
    #     print(f"[DEV] Received signal. Starting work. Current Version: {state.version}")
    #     print("[DEV] Waiting for QA_FAILED status...")
    #     state = await hub.wait_for_status("QA_FAILED")
    #     print(f"[DEV] Received signal. Starting fix. Current Bug Count: {state.bug_count}")
        
    # await asyncio.gather(po_task(), dev_task())
    
    # --- Exercise 4 Demonstration (Interactive Challenge) ---
    # await capstone_orchestrator()
    
    # --- Exercise 5 Demonstration ---
    dev1 = DeveloperAgent("Dev_Alpha")
    dev1.is_responsive = False # Force failure on first check
    qa1 = QAAgent("QA_Beta")
    
    # Start agent processing loops (required for the Supervisor to interact)
    asyncio.create_task(dev1.process_tasks())
    asyncio.create_task(qa1.process_tasks())
    
    supervisor = SupervisorAgent([dev1, qa1])
    await supervisor.run_monitoring()

# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         print("Exiting.")
