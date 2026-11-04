import asyncio

# --- Helper Functions for Agent Simulation ---

async def simulate_agent_task(task_name: str, duration: int) -> None:
    """
    Simulates a non-critical, asynchronous task the agent performs.
    Uses asyncio.sleep to mimic I/O bound work without blocking the loop.
    """
    print(f"\n[{task_name}] Starting task...")
    # Simulate work being done
    await asyncio.sleep(duration)
    print(f"[{task_name}] Task phase complete after {duration} seconds.")


# --- The Critical Human-in-the-Loop Gate ---

async def get_human_approval(prompt: str) -> bool:
    """
    Implements the blocking human approval step using asyncio.to_thread.
    This prevents the synchronous input() call from freezing the event loop.
    """
    print(f"\n{'='*50}")
    print(f"[CRITICAL APPROVAL REQUIRED]")
    print(f"Agent Action: {prompt}")
    print(f"{'='*50}")

    # Define the synchronous function that requires user input
    def synchronous_input_prompt(message: str) -> str:
        """Synchronous helper function using standard blocking input()."""
        # This function runs in a separate thread managed by asyncio.to_thread
        return input(message)

    # CRITICAL STEP: Offload the blocking input() call to a separate thread.
    # We await the result of the synchronous function execution.
    approval_response = await asyncio.to_thread(
        synchronous_input_prompt, 
        "Type 'APPROVE' to continue, 'ABORT' to stop, or 'STATUS' to check agent state: "
    )
    
    # Process the human's input (the interruption pattern)
    response = approval_response.strip().upper()
    
    if response == 'STATUS':
        # Example of a simple redirection/interruption pattern: 
        # The human requests information before making a decision.
        print("\n[AGENT STATUS REPORT]")
        print("Current State: Pre-Deployment Validation Complete.")
        print("Risk Assessment: Moderate (New dependencies added).")
        # Recursively call the approval function after providing status
        return await get_human_approval(prompt) 
    
    # Standard approval/abort flow
    return response == 'APPROVE'


# --- The Main Agent Workflow ---

async def agent_workflow():
    """Defines the sequential steps of the agent, including the gate."""
    print("--- Agent Workflow Initiated: Deployment Process ---")
    
    # 1. Pre-Gate Phase: Non-critical setup and analysis
    await simulate_agent_task("Phase 1: Code Analysis & Testing", 2)
    
    # --- Interruption Point / Approval Gate ---
    critical_action = "Pushing validated build to Production Environment."
    
    is_approved = await get_human_approval(critical_action)
    
    # 2. Post-Gate Phase: Conditional Execution
    if is_approved:
        print("\n[HUMAN APPROVED] Resuming workflow and executing critical action.")
        # Execute the high-risk action
        await simulate_agent_task("Phase 2: Production Deployment", 3)
        print("\n--- Agent Workflow Complete: Deployment Successful ---")
    else:
        print("\n[HUMAN ABORTED] Workflow terminated before critical action. Rollback initiated.")
        # In a real system, we would trigger a rollback function here.
        await simulate_agent_task("Phase 3: Cleanup and Rollback", 1)
        print("--- Agent Workflow Terminated Safely ---")


# --- Entry Point ---

if __name__ == "__main__":
    try:
        # Start the asyncio event loop and run the main agent workflow
        asyncio.run(agent_workflow())
    except KeyboardInterrupt:
        print("\nProcess manually interrupted by user (Ctrl+C).")
