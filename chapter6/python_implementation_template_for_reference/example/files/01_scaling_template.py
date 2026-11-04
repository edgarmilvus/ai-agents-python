import asyncio
import time
import random
from typing import Dict, Any, List

# --- Custom Exceptions for Exercise 4 ---
class WorkerIdleError(Exception):
    """Raised when a worker is idle and should be retired."""
    pass

# --- Exercise 2: Asynchronous Context Manager ---
class AsyncFinancialAPI:
    """Simulates a safe, asynchronous connection to a financial data API."""
    def __init__(self, name="Financial_Tool"):
        self.name = name

    async def __aenter__(self):
        print(f"[{self.name}] Establishing secure connection...")
        await asyncio.sleep(0.1)  # Simulate connection handshake
        print(f"[{self.name}] Connection established.")
        return self

    async def fetch_quote(self, symbol: str) -> Dict[str, Any]:
        """Mock method to fetch data."""
        await asyncio.sleep(random.uniform(0.5, 1.5))
        price = round(random.uniform(100.0, 2000.0), 2)
        return {"symbol": symbol, "price": price, "source": self.name}

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print(f"[{self.name}] Connection closed due to exception: {exc_val}")
        else:
            print(f"[{self.name}] Connection safely closed.")
        await asyncio.sleep(0.1)

# --- Base Agent for all Exercises ---
class WorkerAgent:
    def __init__(self, agent_id: int, specialization: str = "General"):
        self.id = agent_id
        self.specialization = specialization
        self.task_queue: asyncio.Queue = None # Used primarily in Exercise 4

    async def execute_task(self, task_data: Dict[str, Any], tool=None) -> Dict[str, Any]:
        """
        Generic task execution method, adapts based on specialization and tooling.
        Used primarily for Exercises 1, 2, and 3.
        """
        task_name = task_data.get('task_name', 'Unnamed Task')
        duration = task_data.get('duration', 1)
        
        print(f"Worker {self.id} ({self.specialization}) starting: {task_name} (Duration: {duration}s)")
        
        if self.specialization == "DataFetcherAgent" and tool:
            # Exercise 2 logic
            async with tool as api:
                result = await api.fetch_quote(task_data.get('symbol', 'UNKNOWN'))
                details = f"Fetched data: {result}"
        
        elif self.specialization == "CalculationAgent":
            # Exercise 2 logic
            await asyncio.sleep(duration)
            details = f"Complex calculation completed for {task_name}."
            
        else:
            # Exercise 1 & 3 generic logic
            await asyncio.sleep(duration)
            details = f"Analysis complete in {duration}s."
            
        print(f"Worker {self.id} finished: {task_name}")
        return {
            'worker_id': self.id,
            'task': task_name,
            'status': 'Completed',
            'details': details
        }

    async def run_loop(self):
        """
        The continuous execution loop for Exercise 4 (Dynamic Scaling).
        Assumes self.task_queue is set by the Manager.
        """
        if not self.task_queue:
            raise ValueError("Task queue must be set for run_loop.")
            
        while True:
            try:
                # Wait for a task, with a timeout for retirement check
                task_data = await asyncio.wait_for(self.task_queue.get(), timeout=5.0)
                
                # Execute the task (using a simplified version of execute_task)
                task_name = task_data.get('task_name', 'Queue Task')
                duration = task_data.get('duration', 1)
                print(f"Worker {self.id} starting queued task: {task_name} (Duration: {duration}s)")
                await asyncio.sleep(duration)
                print(f"Worker {self.id} finished queued task: {task_name}")
                
                self.task_queue.task_done()
                
            except asyncio.TimeoutError:
                # Signal to the manager that this worker is idle
                raise WorkerIdleError(self.id) 
                
            except asyncio.CancelledError:
                # Safe exit when manager cancels the task
                print(f"Worker {self.id} cancelled by Manager.")
                return
            except Exception as e:
                print(f"Worker {self.id} encountered an error: {e}")
                # Ensure the queue item is marked done even on failure if it was retrieved
                try:
                    self.task_queue.task_done()
                except ValueError:
                    pass # Already marked or never retrieved
                
# --- Manager Class for Exercise 4 (Dynamic Scaling) ---
class DynamicScalingManager:
    MAX_WORKERS = 8
    MIN_WORKERS = 2
    SCALE_UP_THRESHOLD = 5 # If queue > 5, scale up

    def __init__(self):
        self.task_queue = asyncio.Queue()
        self.active_workers: Dict[int, asyncio.Task] = {}
        self.next_worker_id = 1
        self.running = True

    async def _launch_worker(self):
        """Launches a new worker and adds it to the active pool."""
        worker_id = self.next_worker_id
        self.next_worker_id += 1
        
        worker = WorkerAgent(worker_id, specialization="Dynamic")
        worker.task_queue = self.task_queue
        
        worker_task = asyncio.create_task(worker.run_loop(), name=f"WorkerTask-{worker_id}")
        self.active_workers[worker_id] = worker_task
        print(f"\n[MANAGER] Hired Worker {worker_id}. Total active: {len(self.active_workers)}")

    def _retire_worker(self, worker_id: int):
        """Safely retires a worker."""
        if worker_id in self.active_workers:
            task = self.active_workers.pop(worker_id)
            if not task.done():
                task.cancel()
            print(f"[MANAGER] Retired Worker {worker_id}. Total active: {len(self.active_workers)}")

    async def _scaling_monitor(self):
        """Monitors the queue and manages the worker pool size."""
        while self.running:
            await asyncio.sleep(2) # Check every 2 seconds
            queue_size = self.task_queue.qsize()
            current_workers = len(self.active_workers)

            # 1. Scaling Up Logic
            if queue_size > self.SCALE_UP_THRESHOLD and current_workers < self.MAX_WORKERS:
                await self._launch_worker()

            # 2. Worker Monitoring (Retirement check)
            workers_to_retire = []
            for worker_id, task in list(self.active_workers.items()):
                # A finished worker is retired even when the pool is at its
                # floor: it is no longer serving the queue, and counting it as
                # active would leave the manager blind to the next burst.
                if not task.done():
                    continue
                try:
                    # Check if the worker finished due to an idle error
                    task.result()
                except WorkerIdleError:
                    workers_to_retire.append(worker_id)
                except asyncio.CancelledError:
                    # Worker was cancelled by the manager previously, just remove it
                    pass
                except Exception as e:
                    print(f"[MANAGER] Worker {worker_id} failed unexpectedly: {e}")
                    workers_to_retire.append(worker_id) # Retire failed worker

            for worker_id in workers_to_retire:
                self._retire_worker(worker_id)

            # Keep the floor: the last worker idles out on the same timer as the
            # others, and without a replacement the next tasks are never picked.
            while self.running and len(self.active_workers) < self.MIN_WORKERS:
                await self._launch_worker()

    async def submit_tasks(self, tasks: List[Dict[str, Any]]):
        """Submits tasks to the queue."""
        for i, task in enumerate(tasks):
            await self.task_queue.put(task)
            print(f"[MANAGER] Submitted Task {i+1}: {task['task_name']}")

    async def run_system(self, tasks: List[Dict[str, Any]]):
        """Main entry point for the dynamic system."""
        
        # Start minimum required workers
        for _ in range(self.MIN_WORKERS):
            await self._launch_worker()

        monitor_task = asyncio.create_task(self._scaling_monitor())
        
        # Part 1: Submit burst load
        await self.submit_tasks(tasks[:10])
        
        # Wait for the initial burst to be processed and scaling to stabilize
        print("\n--- Waiting for initial burst processing (10s) ---")
        await asyncio.sleep(10) 
        
        # Part 2: Demonstrate retirement during idle period
        print("\n--- System is idle. Workers should start retiring (15s) ---")
        await asyncio.sleep(15) 
        
        # Part 3: Submit small load to reactivate workers
        print("\n--- Submitting small load to reactivate workers ---")
        await self.submit_tasks(tasks[10:])
        
        # Wait for final tasks to complete
        await self.task_queue.join()
        
        # Stop monitoring and retire all remaining workers
        self.running = False
        monitor_task.cancel()
        for worker_id in list(self.active_workers.keys()):
            self._retire_worker(worker_id)
        
        print("\n[MANAGER] Dynamic MAS shutdown complete.")

# Example usage structure for Exercise 4 (The reader fills in the logic above)
async def main_exercise_4():
    print("--- Starting Exercise 4: Dynamic Worker Scaling ---")
    
    # Simulate a total of 12 tasks with varying durations
    tasks_to_submit = [
        {"task_name": f"Task_{i}", "duration": random.uniform(1.0, 3.0)}
        for i in range(1, 13)
    ]
    
    manager = DynamicScalingManager()
    await manager.run_system(tasks_to_submit)

# To run a specific exercise (e.g., Exercise 4):
# if __name__ == "__main__":
#     asyncio.run(main_exercise_4())
