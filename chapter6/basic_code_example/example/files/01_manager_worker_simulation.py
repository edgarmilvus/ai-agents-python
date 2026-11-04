import asyncio
import time
from typing import List, Tuple

# --- 1. Worker Agent Definition ---
async def worker_agent(task_id: int, duration: float) -> str:
    """
    Simulates an independent worker processing a task.
    The worker reports its status and sleeps for the required duration.
    This function represents the autonomous execution layer.
    """
    start_time = time.monotonic()
    print(f"[Worker {task_id}] Starting task. Estimated time: {duration:.2f}s.")
    
    # Simulate the actual CPU-bound or I/O-bound work being done
    await asyncio.sleep(duration)
    
    end_time = time.monotonic()
    elapsed = end_time - start_time
    
    # The worker returns a structured result string
    result = f"Task {task_id} completed successfully (Actual time: {elapsed:.2f}s)."
    print(f"[Worker {task_id}] Finished processing and reporting result.")
    return result

# --- 2. Manager Agent Definition ---
async def manager_agent(task_list: List[Tuple[int, float]]):
    """
    The Manager Agent coordinates and distributes tasks to workers using a TaskGroup.
    It waits for all results before aggregating the final report.
    This function represents the orchestration and aggregation layer.
    """
    print("--- Manager: Initiating task distribution ---")
    worker_tasks = []

    # asyncio.TaskGroup is the modern, robust way to manage concurrent tasks (Python 3.11+)
    # The 'async with' block ensures proper cleanup and exception handling.
    try:
        async with asyncio.TaskGroup() as tg:
            
            # 2a. Task Decomposition and Assignment
            for task_id, duration in task_list:
                # Create a task for each worker function call and launch it immediately
                task = tg.create_task(worker_agent(task_id, duration))
                worker_tasks.append(task)
                print(f"Manager: Assigned Task {task_id} (Duration: {duration:.2f}s) to a new worker.")

        # 2b. Implicit Synchronization Point
        # Control only reaches here once ALL tasks launched within the 'tg' block are completed.
        print("\n--- Manager: All workers have reported in. Aggregating results. ---")

        final_results = []
        # 2c. Result Aggregation
        for task in worker_tasks:
            # task.result() retrieves the return value of the worker_agent function
            final_results.append(task.result())

        print("\n--- FINAL REPORT (Manager Aggregation) ---")
        # Sort results for clean presentation (based on Task ID)
        for res in sorted(final_results):
            print(f"-> {res}")

    except ExceptionGroup as e:
        # TaskGroup wraps multiple exceptions into an ExceptionGroup
        print(f"\n!!! Manager detected critical failure during execution: {e}")
        print("!!! Execution halted. Some tasks may not have completed.")


# --- 3. Execution Setup ---
async def main():
    # Define the tasks: (Task ID, Simulated Duration in seconds)
    tasks_to_run = [
        (101, 3.5), # Task 1: Longest
        (102, 1.0), # Task 2: Shortest
        (103, 2.0), # Task 3: Medium
        (104, 1.5)  # Task 4: Another short task
    ]
    
    print(f"Total tasks to process: {len(tasks_to_run)}")
    print("Expected total time (sequential): 3.5 + 1.0 + 2.0 + 1.5 = 8.0 seconds.")
    print("Expected total time (concurrent): Approximately 3.5 seconds (limited by the longest task).")
    
    start_series = time.monotonic()
    await manager_agent(tasks_to_run)
    end_series = time.monotonic()
    
    print(f"\nSYSTEM STATS: Total runtime for concurrent tasks: {end_series - start_series:.2f} seconds.")

if __name__ == "__main__":
    print("Starting Multi-Agent System Simulation (Manager-Worker Pattern)...")
    asyncio.run(main())
