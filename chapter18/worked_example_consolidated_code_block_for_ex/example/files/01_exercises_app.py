import threading
import time
import uuid
import random
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
import asyncio

# --- 1. Pydantic Models (Used across Exercises) ---

class AgentInput(BaseModel):
    query: str = Field(..., min_length=10, max_length=200, description="The user query for the agent.")
    context_id: str = Field(..., description="Unique session identifier.")
    required_tools: List[str] = Field(default=[], description="List of tool keys to enable for this task.")

class AgentResponse(BaseModel):
    status: str
    result: str
    execution_time_ms: int

class JobSubmission(BaseModel):
    job_id: str
    status: str

class JobStatus(BaseModel):
    job_id: str
    status: str
    result: Optional[str] = None
    
# --- 2. Tool Registry and Worker Simulation (Exercise 4) ---

def tool_math_solver(expression: str) -> str:
    """Simulates a complex mathematical calculation tool."""
    time.sleep(1)
    return f"Math Solver executed: Result for '{expression}' is 42."

def tool_web_search(topic: str) -> str:
    """Simulates a long-running web search tool."""
    time.sleep(3)
    return f"Web Search executed: Found 10 results for '{topic}'."

# The worker must have access to the actual callable functions
TOOL_REGISTRY: Dict[str, Any] = {
    "math_solver": tool_math_solver,
    "web_search": tool_web_search
}

# --- 3. RQ/Redis Simulation (Used for Exercises 2, 3, 4) ---
# In a real environment, this would be handled by actual RQ/Redis objects.

class SimulatedJob:
    def __init__(self, func, args):
        self.id = str(uuid.uuid4())
        self.status = 'queued'
        self.result = None
        self.func = func
        self.args = args

    @property
    def is_finished(self):
        return self.status == 'finished'

    @property
    def is_started(self):
        return self.status == 'started'

# Global store for jobs (simulating Redis storage)
JOB_STORE: Dict[str, SimulatedJob] = {}

class SimulatedQueue:
    def enqueue(self, func, *args):
        job = SimulatedJob(func, args)
        JOB_STORE[job.id] = job
        print(f"[{time.strftime('%H:%M:%S')}] Job {job.id} enqueued.")
        # A real RQ worker is a separate process. A thread is the closest thing
        # that outlives the request which submitted the job, and it keeps the
        # blocking tool calls off the event loop.
        threading.Thread(target=self._run_worker, args=(job,), daemon=True).start()
        return job

    def fetch(self, job_id: str) -> Optional[SimulatedJob]:
        return JOB_STORE.get(job_id)

    def _run_worker(self, job: SimulatedJob):
        time.sleep(0.5)  # network delay before the worker picks the job up
        job.status = 'started'
        print(f"[{time.strftime('%H:%M:%S')}] Worker started job {job.id}.")
        
        try:
            job.result = job.func(*job.args)
            job.status = 'finished'
            print(f"[{time.strftime('%H:%M:%S')}] Worker finished job {job.id}.")
        except Exception as e:
            job.status = 'failed'
            job.result = str(e)
            print(f"[{time.strftime('%H:%M:%S')}] Worker failed job {job.id}: {e}")


# Initialize simulated queue
q = SimulatedQueue()
app = FastAPI()

# --- 4. Agent Worker Function (Exercise 2 & 4) ---

def run_long_agent(query: str, context_id: str, required_tools: List[str]) -> str:
    """
    Simulates the execution of a complex, long-running agent.
    This function runs in the worker process (simulated by _simulate_worker_execution).
    """
    
    # 4. Dynamic Tool Registration Logic (Exercise 4)
    active_tools = []
    tool_logs = []
    
    if required_tools:
        for tool_key in required_tools:
            if tool_key in TOOL_REGISTRY:
                tool_func = TOOL_REGISTRY[tool_key]
                active_tools.append(tool_func.__name__)
                # Simulate agent using the tool
                tool_output = tool_func(query)
                tool_logs.append(tool_output)
            else:
                tool_logs.append(f"Warning: Tool '{tool_key}' not found in registry.")

    # Simulate core agent reasoning and execution time
    # Long enough to be worth a queue, short enough to watch in a demo.
    execution_time = random.randint(1, 3)
    time.sleep(execution_time)

    final_result = (
        f"Agent Execution Complete (Context: {context_id}).\n"
        f"Query: {query}\n"
        f"Time Taken: {execution_time} seconds.\n"
        f"Tools Used: {', '.join(active_tools) if active_tools else 'None'}.\n"
        f"Tool Logs: {'; '.join(tool_logs)}"
    )
    return final_result

# ====================================================================
# API ENDPOINTS
# ====================================================================

# --- Exercise 1: Synchronous Agent Endpoint ---

@app.post("/agent/execute_sync", response_model=AgentResponse)
async def execute_sync(data: AgentInput):
    """
    Handles fast, synchronous agent tasks directly in the API thread.
    """
    start_time = time.time()
    
    # Simulate very fast agent operation
    await asyncio.sleep(0.05)
    
    # Simulate a result based on the query
    result = f"Synchronous response for query: '{data.query[:50]}...'"
    
    end_time = time.time()
    execution_ms = int((end_time - start_time) * 1000)
    
    return AgentResponse(
        status="completed",
        result=result,
        execution_time_ms=execution_ms
    )

# --- Exercise 2 & 4: Asynchronous Job Submission ---

@app.post("/agent/submit", response_model=JobSubmission)
async def submit_agent_task(data: AgentInput):
    """
    Submits a long-running agent task to the message queue (RQ).
    (Handles dynamic tool list from Exercise 4)
    """
    
    # Enqueue the worker function with the required parameters
    job = q.enqueue(
        run_long_agent, 
        data.query, 
        data.context_id, 
        data.required_tools
    )
    
    return JobSubmission(
        job_id=job.id,
        status="submitted"
    )

# --- Exercise 2 & 3: Status Polling Endpoint ---

@app.get("/agent/status/{job_id}", response_model=JobStatus)
async def get_agent_status(job_id: str, long_poll: bool = False):
    """
    Checks the status of an enqueued job. Supports optional long polling (Exercise 3).
    """
    job = q.fetch(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job ID {job_id} not found.")

    # --- Exercise 3: Asynchronous Long Polling Logic ---
    if long_poll:
        timeout = 30 # Max wait time in seconds
        poll_interval = 2 # Check every 2 seconds
        start_time = time.time()

        while time.time() - start_time < timeout:
            job = q.fetch(job_id) # Re-fetch status inside the loop
            if job.is_finished:
                # Break out and return result
                break
            
            # CRITICAL: Use non-blocking sleep
            await asyncio.sleep(poll_interval) 
        
        # Check status again after loop finishes (either by completion or timeout)
        job = q.fetch(job_id) 
        
        if not job.is_finished:
            # If still not finished after timeout
            raise HTTPException(
                status_code=408, 
                detail=f"Processing timeout reached (30s). Job {job_id} is still '{job.status}'."
            )
    # --- End Exercise 3 Logic ---

    # Standard status response (used by Exercise 2 if long_poll=False, 
    # or by Exercise 3 after completion)
    status = job.status
    result = job.result if job.is_finished else None
    
    return JobStatus(
        job_id=job_id,
        status=status,
        result=result
    )

# Example usage (run this file and access via Uvicorn):
# uvicorn your_file_name:app --reload
