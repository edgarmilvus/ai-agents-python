# Inside the WorkerAgent's run loop:
while True:
    try:
        # Wait for a task, but only for 5 seconds
        task_data = await asyncio.wait_for(self.task_queue.get(), timeout=5.0)
        # Process task...
        self.task_queue.task_done()
    except asyncio.TimeoutError:
        # If timeout occurs, signal the manager or raise a specific exception
        # that the manager catches to retire the worker.
        print(f"Worker {self.id} timed out. Signaling retirement.")
        raise WorkerIdleError(self.id) 
    except asyncio.CancelledError:
        # Handle safe shutdown if manager cancels the task
        print(f"Worker {self.id} cancelled by Manager.")
        return
