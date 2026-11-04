# --- Exercise 1: Swarm State Hub Implementation ---

class SwarmStateHub:
    """
    Centralized, thread-safe manager for ProjectState using asyncio.Lock and Futures.
    """
    def __init__(self):
        self._state = ProjectState()
        self._lock = asyncio.Lock()
        # Map: {target_status: [list_of_futures_waiting]}
        self._waiting_futures: Dict[str, List[asyncio.Future]] = {}

    async def get_state(self) -> ProjectState:
        """Retrieves the current state safely."""
        async with self._lock:
            return self._state.model_copy(deep=True)

    async def update_state(self, new_data: Dict[str, Any]):
        """Updates the state and resolves any waiting futures."""
        async with self._lock:
            old_status = self._state.status
            
            # Update state model
            updated_state = self._state.model_copy(update=new_data)
            updated_state.version += 1
            self._state = updated_state
            
            print(f"[HUB] State updated to: {self._state.status} (V{self._state.version})")

            # Check for and resolve waiting futures
            if self._state.status != old_status and self._state.status in self._waiting_futures:
                futures_to_resolve = self._waiting_futures.pop(self._state.status)
                for future in futures_to_resolve:
                    if not future.done():
                        future.set_result(self._state.model_copy(deep=True))

    async def wait_for_status(self, target_status: str) -> ProjectState:
        """Pauses execution until the state transitions to the target status."""
        async with self._lock:
            if self._state.status == target_status:
                return self._state.model_copy(deep=True)
            
            # Create a new future and register it
            future = asyncio.Future()
            if target_status not in self._waiting_futures:
                self._waiting_futures[target_status] = []
            self._waiting_futures[target_status].append(future)
            
        # Await the future outside the lock
        return await future

# --- Demonstration for Exercise 1 ---

async def main_ex1_demo():
    hub = SwarmStateHub()
    
    async def po_agent_task():
        print("[PO Agent] Finalizing requirements...")
        await asyncio.sleep(0.5)
        await hub.update_state({"status": "IN_DEVELOPMENT", "current_artifact": "Reqs_Final_V1"})
        await asyncio.sleep(1.0)
        await hub.update_state({"status": "QA_FAILED", "bug_count": 5})

    async def dev_agent_task():
        print("[DEV Agent] Waiting for IN_DEVELOPMENT status signal...")
        state = await hub.wait_for_status("IN_DEVELOPMENT")
        print(f"[DEV Agent] Signal received. Starting work on artifact: {state.current_artifact}. Current Version: {state.version}")
        
        await asyncio.sleep(1.5)
        
        print("[DEV Agent] Waiting for QA_FAILED status signal...")
        state = await hub.wait_for_status("QA_FAILED")
        print(f"[DEV Agent] Received signal. Starting fix cycle. Current Bug Count: {state.bug_count}")
        
    print("--- Starting Exercise 1 Demo: Future-Based State Handoff ---")
    await asyncio.gather(po_agent_task(), dev_agent_task())
    print("--- Exercise 1 Demo Complete ---")

if __name__ == "__main__":
    asyncio.run(main_ex1_demo())
