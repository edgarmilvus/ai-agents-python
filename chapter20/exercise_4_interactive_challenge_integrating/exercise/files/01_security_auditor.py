# --- Agent Specialization for Exercise 4 ---

class SecurityAuditorAgent(BaseAgent):
    """The new agent for mandatory security review."""
    async def _execute_development(self, artifact: str) -> Any:
        """Simulates security audit, potentially generating a SecurityViolation."""
        print(f"[{self.name}] Auditing artifact: {artifact}")
        await asyncio.sleep(0.2)
        
        # The first audit finds a violation and the later ones pass, so the demo
        # shows both branches and always converges (a random verdict made it
        # flaky under load).
        self._audits = getattr(self, "_audits", 0) + 1
        if self._audits == 1:
            violation = SecurityViolation(
                vulnerability_type="XSS Risk",
                risk_level='HIGH',
                vulnerable_code_snippet="<script>alert('xss')</script>",
                remediation_instruction="Sanitize all user input before rendering in the UI."
            )
            print(f"[{self.name}] Security Audit FAILED. Generating Violation Report.")
            return violation
        else:
            print(f"[{self.name}] Security Audit PASSED.")
            return {"status": "SECURITY_PASS", "artifact": artifact}

async def main_ex4_demo():
    """
    Orchestrator managing the mandatory Security Auditor step and remediation loop.
    """
    # Setup Agents
    dev_agent = DeveloperAgent("Dev_A")
    qa_agent = QAAgent("QA_1")
    sec_agent = SecurityAuditorAgent("Sec_Audit_1")
    
    # Start agent processing loops
    asyncio.create_task(dev_agent.process_tasks())
    asyncio.create_task(qa_agent.process_tasks())
    asyncio.create_task(sec_agent.process_tasks())
    
    # Initial task submission (Simulated PO input)
    current_artifact = await dev_agent.run_task("Initial requirements: Build a secure API endpoint.")
    
    max_iterations = 5
    iteration = 0
    
    print("--- Starting Exercise 4 Demo: Security and QA Workflow ---")
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")
        
        # 1. Mandatory Security Audit
        audit_result = await sec_agent.run_task(current_artifact)
        
        if isinstance(audit_result, SecurityViolation):
            print(f"[ORCHESTRATOR] Security Violation detected ({audit_result.risk_level}). Rerouting to Developer for remediation.")
            # Developer handles the violation report
            current_artifact = await dev_agent.run_task(audit_result)
            continue # Restart loop for re-audit

        # 2. Quality Assurance Check (Only if Security Passed)
        qa_result = await qa_agent.run_task(audit_result['artifact'])
        
        if isinstance(qa_result, BugReport):
            print("[ORCHESTRATOR] QA Bug Report received. Rerouting to Developer for fix.")
            # Developer handles the bug report
            current_artifact = await dev_agent.run_task(qa_result)
            continue # Restart loop for re-audit (Security must be checked again)
        
        # 3. Successful Delivery
        print("\n[ORCHESTRATOR] SUCCESS: Artifact passed Security and QA.")
        print(f"Final Artifact Delivered: {qa_result['artifact']}")
        break
    
    if iteration >= max_iterations:
        print("[ORCHESTRATOR] FAILURE: Max iterations reached. Project halted.")

if __name__ == "__main__":
    asyncio.run(main_ex4_demo())
