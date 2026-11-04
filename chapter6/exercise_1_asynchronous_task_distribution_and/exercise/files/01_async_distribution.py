import asyncio
import time
import json
from typing import Dict, Any, List

# --- Agent Definition ---
class WorkerAgent:
    def __init__(self, agent_id: int):
        self.id = agent_id

    async def execute_task(self, task_name: str, duration: float) -> Dict[str, Any]:
        print(f"Worker {self.id} starting: {task_name} (Duration: {duration}s)")
        start_time = time.monotonic()
        
        # 1. Simulate work
        await asyncio.sleep(duration)
        
        end_time = time.monotonic()
        
        details = f"Analysis complete in {round(end_time - start_time, 2)}s."
        print(f"Worker {self.id} finished: {task_name}")
        
        # 1. Return structured result
        return {
            'task': task_name,
            'status': 'Completed',
            'duration_simulated': duration,
            'worker_id': self.id,
            'details': details
        }

# --- Manager Role ---
class ResearchManager:
    def __init__(self):
        # Initialize reusable workers
        self.workers = [WorkerAgent(i) for i in range(1, 4)]
        
    async def run_analysis(self) -> Dict[str, Any]:
        print("--- Manager initiating parallel research tasks ---")
        start_global_time = time.monotonic()
        
        # Define tasks and their required durations
        tasks_data = [
            ("Market Size Estimation", 2.0, self.workers[0]), 
            ("Competitor Landscape Analysis", 4.0, self.workers[1]), # Longest task
            ("Regulatory Compliance Check", 1.0, self.workers[2]), 
        ]
        
        # 3. Parallel Execution: Create coroutines and gather them
        coros = [
            worker.execute_task(name, duration)
            for name, duration, worker in tasks_data
        ]
        
        results: List[Dict[str, Any]] = await asyncio.gather(*coros)
        
        end_global_time = time.monotonic()
        total_time = round(end_global_time - start_global_time, 2)
        
        # 4. Collation: Aggregate results
        final_report = {
            "total_execution_time": total_time,
            "tasks": {}
        }
        
        for result in results:
            task_name = result.pop('task')
            final_report['tasks'][task_name] = result
            
        print(f"\n--- Manager Collation Complete ---")
        
        return final_report

async def main_exercise_1():
    manager = ResearchManager()
    report = await manager.run_analysis()
    
    print("\n[FINAL REPORT STRUCTURE]")
    print(json.dumps(report, indent=4))
    
    # 5. Timing Verification
    print(f"\nVerification: Total execution time ({report['total_execution_time']}s) confirms parallelism.")

if __name__ == "__main__":
    asyncio.run(main_exercise_1())
