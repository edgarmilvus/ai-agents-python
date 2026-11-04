# Assume MockFinancialAPI and LOG_FILE_PATH are defined from the setup

def check_live_service_status(service_name: str) -> str:
    """
    Checks the real-time, current operational status of a specific internal microservice 
    (e.g., 'deployment_api', 'log_aggregator'). Use for current uptime checks.
    """
    status = MockFinancialAPI.get_service_status(service_name)
    return f"Current status of the '{service_name}' service is: {status}."

def analyze_deployment_log(log_path: str) -> str:
    """
    Reads the historical deployment log file, summarizes error counts, and extracts the last critical error. 
    Use this tool for historical context, failure analysis, and error counting.
    """
    try:
        with open(log_path, 'r') as f:
            lines = f.readlines()
            
        total_lines = len(lines)
        error_count = 0
        last_error = "N/A"
        
        # Iterate backwards to find the last error quickly
        for line in reversed(lines):
            line = line.strip()
            if "ERROR" in line:
                error_count += 1
                if last_error == "N/A":
                    last_error = line
            
        return (f"Log analysis complete: Total lines analyzed = {total_lines}. "
                f"Total ERROR entries found = {error_count}. "
                f"Last critical error logged: {last_error}.")

    except FileNotFoundError:
        return f"ERROR: Log file not found at path: {log_path}"

# --- Advanced Tool Routing and Orchestration Challenge ---
# System Prompt Policy:
# "You are the Deployment Analyst. Use `check_live_service_status` only for questions about 
# current uptime or real-time status. Use `analyze_deployment_log` only for questions 
# requiring historical data, error counts, or past events."
#
# Query: "The log aggregator service seems slow. What is its current status, and what were the two most recent errors logged in the deployment history?"
#
# Agent Execution Sequence (Simulated):
# 1. Tool Call (Current Status): 
#    check_live_service_status(service_name="log_aggregator")
#    Output: "Current status of the 'log_aggregator' service is: DEGRADED."
#
# 2. Tool Call (Historical Errors): 
#    analyze_deployment_log(log_path="deployment_logs.txt")
#    Output: "Log analysis complete: Total lines analyzed = 6. Total ERROR entries found = 2. 
#             Last critical error logged: ERROR: 2024-08-01 10:07:05 - Critical exception in worker process 7: Memory limit exceeded."
#
# LLM Synthesis:
# "The log aggregator service is currently reporting a **DEGRADED** status. Historically, the logs show 2 errors. 
# The two most recent errors logged were a 'Database connection failure on node 3' and the last critical error: 
# 'Critical exception in worker process 7: Memory limit exceeded'."
