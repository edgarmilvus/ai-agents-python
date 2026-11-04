import asyncio
import random
from typing import Literal, Any, Dict, List, Optional
from pydantic import BaseModel, Field

# --- Pydantic Models for Structured Communication ---

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

# --- Base Agent Class (Used in Exercises 2, 3, 4, 5) ---

class BaseAgent:
    """Base class providing common agent functionality and resilience hooks."""
    def __init__(self, name: str):
        self.name = name
        self.task_queue = asyncio.Queue()
        self.current_task_count = 0
        self.is_responsive = True
        self.development_plan = ""

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
        """Simulates continuous task processing loop."""
        print(f"[{self.name}] Agent started.")
        while True:
            task_data, future = await self.task_queue.get()
            
            # Simulated work
            await asyncio.sleep(0.1)
            
            # Handle structured feedback (Exercise 3/4 integration)
            if isinstance(task_data, BugReport):
                result = await self._handle_refinement(task_data.suggested_fix_summary)
            elif isinstance(task_data, SecurityViolation):
                result = await self._handle_refinement(task_data.remediation_instruction)
            else:
                # Initial task or artifact passing
                result = await self._execute_development(task_data)
            
            if not future.done():
                future.set_result(result)
            self.current_task_count -= 1
            self.task_queue.task_done()

    async def _execute_development(self, requirements: Any) -> Any:
        """Placeholder for initial development/core function."""
        return f"Artifact_v{random.randint(1, 10)}_InitialCode"

    async def _handle_refinement(self, instruction: str) -> str:
        """Handles structured feedback for refinement (Exercise 3/4)."""
        print(f"[{self.name}] Entering Refinement Cycle. Adapting plan based on: {instruction[:30]}...")
        self.development_plan = f"Refined plan based on: {instruction}"
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
