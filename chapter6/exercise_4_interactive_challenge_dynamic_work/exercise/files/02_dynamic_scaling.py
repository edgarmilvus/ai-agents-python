import asyncio
import time
import random
from typing import Dict, Any, List

# --- Custom Exceptions for Exercise 4 ---
class WorkerIdleError(Exception):
    """Raised when a worker is idle and should be retired."""
    pass

# --- Worker Agent with Dynamic Lifecycle ---
class WorkerAgent:
    def __init__(self, agent_id: int, specialization: str = "Dynamic"):
        self.id = agent_id
        self.specialization = specialization
        self.task_queue: asyncio.Queue = None 

    async def run_loop(self):
        """
        The continuous execution loop. Uses a 5s timeout to signal idleness.
        """
        if not self.task_queue:
            raise ValueError("Task queue must be set for run_loop.")
            
        print(f"[W{self.id}] Worker started.")
        
        while True:
            try:
                # Wait for a task, with a timeout (T=5s) for retirement check
                task_data = await asyncio.wait_for(self.task_queue.get(), timeout=5.0)
                
                # Execute the task
                task_name = task_data.get('task_name', 'Queue Task')
                duration = task_data.get('duration', 1)
                
                print(f"[W{self.id}] Starting queued task: {task_name} (Duration: {duration:.1f}s)")
                await asyncio.sleep(duration)
                print(f"[W{self.id}] Finished queued task: {task_name}")
                
                self.task_queue.task_done()
                
            except asyncio.TimeoutError:
                # 3. If timeout occurs, signal the manager to retire the worker
                print(f"[W{self.id}] Idle timeout reached. Signaling retirement.")
                raise WorkerIdleError(self.id) 
                
            except asyncio.CancelledError:
                # 4. Handle safe shutdown if manager cancels the task
                print(f"[W{self.id}] Cancelled by Manager.")
                return
            except Exception as e:
                print(f"[W{self.id}] Encountered an error: {e}")
                try:
                    self.task_queue.task_done()
                except ValueError:
                    pass 
                
# --- Manager Class for Dynamic Scaling ---
class DynamicScalingManager:
    MAX_WORKERS = 8
    MIN_WORKERS = 2
    SCALE_UP_THRESHOLD = 5 # 2. Scaling Up: If queue > 5, scale up

    def __init__(self):
        self.task_queue = asyncio.Queue()
        self.active_workers: Dict[int, asyncio.Task] = {}
        self.next_worker_id = 1
        self.running = True

    async def _launch_worker(self):
        """Launches a new worker and adds it to the active pool."""
        if len(self.active_workers) >= self.MAX_WORKERS:
            return
            
        worker_id = self.next_worker_id
        self.next_worker_id += 1
        
        worker = WorkerAgent(worker_id)
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
        """1. Task Queue Monitoring and 2/3. Scaling Logic."""
        while self.running:
            await asyncio.sleep(1) 
            queue_size = self.task_queue.qsize()
            current_workers = len(self.active_workers)

            print(f"[MONITOR] Queue size: {queue_size}, Active workers: {current_workers}")

            # 2. Scaling Up Logic
            if queue_size > self.SCALE_UP_THRESHOLD and current_workers < self.MAX_WORKERS:
                print(f"[MANAGER] Scale Up Triggered: Queue size ({queue_size}) > Threshold ({self.SCALE_UP_THRESHOLD})")
                await self._launch_worker()

            # 3. Scaling Down (Retiring) Logic
            # A worker that has finished is retired whether or not the pool is
            # above the floor: it is no longer serving the queue, so keeping it
            # in the count would leave the manager believing it still has help.
            workers_to_retire = []
            for worker_id, task in list(self.active_workers.items()):
                if not task.done():
                    continue
                try:
                    # Check if the worker finished due to an idle error
                    task.result()
                except WorkerIdleError:
                    workers_to_retire.append(worker_id)
                except asyncio.CancelledError:
                    # Worker was cancelled by the manager previously
                    pass
                except Exception:
                    print(f"[MANAGER] Worker {worker_id} failed unexpectedly.")
                    workers_to_retire.append(worker_id)

            for worker_id in workers_to_retire:
                self._retire_worker(worker_id)

            # Refill to the floor, otherwise the last idle worker retires and
            # the next burst of tasks is never picked up.
            while self.running and len(self.active_workers) < self.MIN_WORKERS:
                await self._launch_worker()

    async def submit_tasks(self, tasks: List[Dict[str, Any]]):
        """Submits tasks to the queue."""
        for task in tasks:
            await self.task_queue.put(task)
            print(f"[MANAGER] Submitted Task {task['task_name']}")

    async def run_system(self, tasks: List[Dict[str, Any]]):
        """5. Test Scenario Execution Flow."""
        
        # Start minimum required workers
        for _ in range(self.MIN_WORKERS):
            await self._launch_worker()

        monitor_task = asyncio.create_task(self._scaling_monitor())
        
        # Part 1: Submit burst load (10 tasks)
        print("\n--- PHASE 1: Submitting Burst Load (10 tasks) ---")
        await self.submit_tasks(tasks[:10])
        
        # Wait for processing and scale-up (workers should be hired here)
        print("\n--- PHASE 2: Waiting for processing and stabilization (10s) ---")
        await asyncio.sleep(10) 
        
        # Part 2: Demonstrate retirement during idle period (Workers should retire after 5s timeout)
        print("\n--- PHASE 3: System is idle. Workers should start retiring (15s pause) ---")
        await asyncio.sleep(15) 
        
        # Part 3: Submit small load to reactivate workers
        print("\n--- PHASE 4: Submitting small load (2 tasks) to reactivate workers ---")
        await self.submit_tasks(tasks[10:])
        
        # Wait for final tasks to complete
        await self.task_queue.join()
        
        # Final shutdown
        self.running = False
        monitor_task.cancel()
        await asyncio.sleep(0.1) 
        
        print("\n[MANAGER] Initiating final shutdown of remaining workers.")
        for worker_id in list(self.active_workers.keys()):
            self._retire_worker(worker_id)
        
        print("\n[MANAGER] Dynamic MAS shutdown complete.")

async def main_exercise_4():
    # Simulate a total of 12 tasks with varying durations
    tasks_to_submit = [
        {"task_name": f"Task_{i}", "duration": random.uniform(1.0, 3.0)}
        for i in range(1, 13)
    ]
    
    manager = DynamicScalingManager()
    await manager.run_system(tasks_to_submit)

if __name__ == "__main__":
    asyncio.run(main_exercise_4())
