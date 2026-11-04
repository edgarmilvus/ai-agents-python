from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
from rq import Queue, Retry, get_current_job
import time
import json
import os
from typing import Dict, Any

# --- 1. Configuration and Queue Setup ---

# Connect to Redis. Environment variables should manage production settings.
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
# Initialize the RQ queue named 'agent_analysis'
analysis_queue = Queue('agent_analysis', connection=redis_conn)

# --- 2. Pydantic Model for Input Validation ---
class AnalysisRequest(BaseModel):
    company_name: str

# --- 3. The Agent Task Runner (Executed by RQ Worker) ---
def agent_task_runner(company: str) -> str:
    """
    Simulates a complex, long-running autonomous agent process.
    This function executes entirely within the separate RQ worker process.
    """
    current_job = get_current_job(redis_conn)
    print(f"[{current_job.id}] Agent started analysis for: {company}")
    
    # Step 1: Tool Call Simulation (e.g., web scraping, data fetching)
    # The agent might spend 5s calling external APIs or tools.
    time.sleep(5) 
    
    # Step 2: LLM Reasoning and Synthesis
    sentiment = "Highly Positive" if len(company) % 2 == 0 else "Neutral/Cautious"
    
    # Step 3: Final Report Generation and Structured Output
    time.sleep(3) 

    report_data: Dict[str, Any] = {
        "company": company,
        "sentiment_score": 0.85 if sentiment == "Highly Positive" else 0.55,
        "final_sentiment": sentiment,
        "analysis_duration_s": 8.0,
        "recommendation": f"Buy signal based on {sentiment} market outlook."
    }
    print(f"[{current_job.id}] Agent finished analysis for: {company}")
    
    # RQ stores the return value. We use JSON serialization for structured data.
    return json.dumps(report_data)

# --- 4. FastAPI Application Initialization ---
app = FastAPI(
    title="Autonomous Agent Deployment Service",
    description="Scalable endpoints for long-running agent tasks using RQ."
)

# --- 5. Endpoint 1: Submission (Enqueueing the Job) ---
@app.post("/analyze/submit", status_code=202)
def submit_analysis(request: AnalysisRequest):
    """
    Accepts a request, enqueues the agent task, and returns the job ID immediately.
    The 202 Accepted status code signifies that the request has been accepted 
    for processing, but the processing is not yet complete.
    """
    company = request.company_name
    
    # Define retry behavior: If the worker fails, retry once after 60 seconds.
    retry_policy = Retry(max=1, interval=[60]) 
    
    # Enqueue the task. RQ handles serialization of the function and arguments.
    job = analysis_queue.enqueue(
        agent_task_runner, 
        company, 
        job_timeout='1h', # Maximum runtime for the job
        retry=retry_policy,
        result_ttl=86400 # Keep the result in Redis for 24 hours
    )
    
    # Return the job ID, which acts as the Future identifier.
    return {
        "message": "Analysis job submitted successfully.",
        "job_id": job.id,
        "status_endpoint": f"/analyze/status/{job.id}"
    }

# --- 6. Endpoint 2: Status Check and Retrieval (Polling) ---
@app.get("/analyze/status/{job_id}")
def get_analysis_status(job_id: str):
    """
    Checks the status of the queued job and returns the final result if complete.
    """
    job = analysis_queue.fetch_job(job_id)

    if job is None:
        raise HTTPException(status_code=404, detail="Job ID not found or expired.")

    status = job.get_status()
    
    if status == 'finished':
        # Retrieve the result and deserialize the JSON string
        result_data = json.loads(job.result)
        return {
            "job_id": job_id,
            "status": status,
            "result": result_data,
            "completion_time": job.ended_at.isoformat()
        }
    
    elif status == 'failed':
        # Provide debugging information for failed jobs
        return {
            "job_id": job_id,
            "status": status,
            "error": "Agent execution failed.",
            "exc_info": job.exc_info.splitlines()[-5:] if job.exc_info else "No traceback available."
        }
        
    else:
        # Job is queued, started, or deferred (still processing)
        return {
            "job_id": job_id,
            "status": status,
            "message": "Processing in progress. Please check back later."
        }
