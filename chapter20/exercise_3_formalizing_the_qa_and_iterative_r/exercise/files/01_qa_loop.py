# --- Agent Specialization for Exercise 3 ---

class QAAgent(BaseAgent):
    """The agent responsible for quality assurance and bug reporting."""
    async def _execute_development(self, artifact: str) -> Any:
        """Simulates QA testing, potentially generating a BugReport."""
        print(f"[{self.name}] Testing artifact: {artifact}")
        await asyncio.sleep(0.3)
        
        # The first artifact always fails and the refined one always passes, so
        # the demo shows the refinement loop instead of a coin flip.
        self._qa_runs = getattr(self, "_qa_runs", 0) + 1
        if self._qa_runs == 1:
            report = BugReport(
                severity='MAJOR',
                description=f"Critical validation failure found in {artifact}.",
                steps_to_reproduce=["1. Load component", "2. Input invalid data"],
                suggested_fix_summary="Implement robust input sanitation on the server side."
            )
            print(f"[{self.name}] Artifact FAILED QA. Generating Bug Report {report.bug_id}.")
            return report
        else:
            print(f"[{self.name}] Artifact passed QA.")
            return {"status": "QA_PASS", "artifact": artifact}

# --- Demonstration for Exercise 3: Orchestrator Logic ---

async def main_ex3_demo():
    dev_agent = DeveloperAgent("Dev_A")
    qa_agent = QAAgent("QA_1")
    
    # Start agent processing loops
    asyncio.create_task(dev_agent.process_tasks())
    asyncio.create_task(qa_agent.process_tasks())
    
    initial_reqs = "Implement user authentication module."
    current_artifact = await dev_agent.run_task(initial_reqs)
    
    max_iterations = 3
    iteration = 0
    
    print("--- Starting Exercise 3 Demo: Iterative Refinement Loop ---")
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n--- Refinement Cycle {iteration} ---")
        
        # 1. QA Check
        qa_result = await qa_agent.run_task(current_artifact)
        
        if isinstance(qa_result, BugReport):
            print(f"[ORCHESTRATOR] Routing Bug Report {qa_result.bug_id} back to Developer.")
            # 2. Developer Refinement
            current_artifact = await dev_agent.run_task(qa_result)
            print(f"[ORCHESTRATOR] Developer returned new artifact: {current_artifact}")
            continue
        
        # Success
        print("\n[ORCHESTRATOR] SUCCESS: Artifact passed QA and is delivered.")
        print(f"Final Artifact: {qa_result['artifact']}")
        break
    
    if iteration >= max_iterations:
        print("[ORCHESTRATOR] FAILURE: Max refinement iterations reached.")

if __name__ == "__main__":
    asyncio.run(main_ex3_demo())
