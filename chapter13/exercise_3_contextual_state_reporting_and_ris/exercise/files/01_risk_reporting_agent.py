class AnalysisAgent:
    """
    An agent that provides contextual history and risk assessment before 
    requesting approval for critical actions.
    """
    def __init__(self):
        # Use deque for rolling history buffer (maxlen=10)
        self.agent_history = deque(maxlen=10)
        self.tasks = [
            {'desc': 'Analyze input stream 1', 'critical': False},
            {'desc': 'Pre-process data set A', 'critical': False},
            {'desc': 'Execute complex ML model training (High Compute)', 'critical': True},
            {'desc': 'Generate final report summary', 'critical': False},
            {'desc': 'Write results to production DB (Schema Write)', 'critical': True},
            {'desc': 'Cleanup temporary files', 'critical': False},
        ]
        self.current_task_index = 0

    def _log_action(self, action: str):
        """Adds an action to the history buffer."""
        self.agent_history.append(f"Task [{self.current_task_index}]: {action}")
        print(f"LOG: {action}")

    def _calculate_risk(self, action_plan: str) -> int:
        """Scores the plan: an irreversible write is riskier than heavy compute.

        A real system would ask the LLM here. The listing scores deterministically
        so that every run shows both branches: one task pauses, one passes.
        """
        if "DB" in action_plan or "Write" in action_plan:
            return 9
        if "Compute" in action_plan or "training" in action_plan:
            return 6
        return 3
    def _present_contextual_approval(self, action_plan: str, risk_score: int) -> bool:
        """Presents context, risk score, and prompts for approval."""
        print("\n" + "=" * 60)
        print("!!! HUMAN INTERVENTION REQUIRED: HIGH-RISK ACTION PENDING !!!")
        print(f"Current State: AWAITING_APPROVAL | Proposed Risk Score: {risk_score}/10")
        print("-" * 60)
        
        print("--- Recent Agent History (Last 5 Actions) ---")
        # Display the last 5 entries
        history_slice = list(self.agent_history)[-5:]
        if not history_slice:
            print("  (No recent history available)")
        for i, entry in enumerate(history_slice):
            print(f"  ({i+1}) {entry}")
        
        print("-" * 60)
        print("Proposed Critical Action Plan:")
        print(action_plan)
        print("-" * 60)
        
        while True:
            response = input("Approve this critical action? (Y/N): ").strip().upper()
            if response in ['Y', 'N']:
                return response == 'Y'
            print("Invalid input.")

    def run(self):
        for i, task in enumerate(self.tasks):
            self.current_task_index = i
            task_desc = task['desc']
            
            if task['critical']:
                risk = self._calculate_risk(task_desc)
                self._log_action(f"Calculated risk for '{task_desc}': {risk}/10")
                
                if risk > 7:
                    if self._present_contextual_approval(task_desc, risk):
                        self._log_action(f"Executing critical task '{task_desc}' (Approved).")
                    else:
                        self._log_action(f"Critical task '{task_desc}' Denied by Human. Skipping.")
                        continue # Skip to the next task
                else:
                    self._log_action(f"Executing critical task '{task_desc}' (Risk acceptable: {risk}).")
            else:
                self._log_action(f"Executing standard task: {task_desc}")
            
            time.sleep(0.2)
        
        print("\nAnalysis Agent completed all tasks.")

# =============================================================================
# Exercise 4: Interactive Challenge - Multi-Tier Secure Deployment Pipeline
# =============================================================================

class DeploymentAgent:
    """
    Manages a pipeline with multi-tiered approval gates, including a secure 
    authorization code requirement for high-risk stages.
    """
    HIGH_RISK_AUTH_CODE = "PROD_OVERSEER_2024"

    def __init__(self):
        self.pipeline = [
            ('Code Review', 'LOW'),
            ('Staging Deployment', 'LOW'),
            ('Automated Testing', 'LOW'),
            ('Production Deployment', 'HIGH') # Requires Tier 2 approval
        ]
    
    def _tier1_approval(self) -> bool:
        """Simple Y/N approval for low-risk transition."""
        print("\n--- TIER 1 APPROVAL REQUIRED (Staging Complete) ---")
        response = input("Testing passed. Ready to merge to main and plan production? (Y/N): ").strip().upper()
        return response == 'Y'

    def _tier2_secure_approval(self, stage_name: str) -> bool:
        """Secure approval requiring a secret authorization code."""
        print(f"\n--- TIER 2 SECURE APPROVAL REQUIRED: {stage_name} ---")
        print("This action is irreversible and requires explicit authorization.")
        
        # First, check general approval
        while True:
            response = input("Approve execution? (Y/N): ").strip().upper()
            if response == 'N':
                return False
            elif response == 'Y':
                break
            else:
                print("Invalid input.")

        # Second, check authorization code
        attempts = 0
        while attempts < 3:
            auth_code = input("Enter mandatory Authorization Code: ").strip()
            
            if auth_code == self.HIGH_RISK_AUTH_CODE:
                print("Authorization Code validated.")
                return True
            else:
                attempts += 1
                print(f"ERROR: Invalid Authorization Code. {3 - attempts} attempts remaining.")
        
        # If loop finishes without success (3 failed attempts)
        raise AuthorizationFailure("Tier 2 authorization failed after multiple attempts.")

    def run(self):
        print("Deployment Agent Pipeline Initiated.")
        try:
            for index, (stage_name, risk_level) in enumerate(self.pipeline):
                print(f"\n[{index+1}/{len(self.pipeline)}] Starting Stage: {stage_name} (Risk: {risk_level})")
                
                # Simulate stage work
                time.sleep(0.5)

                if stage_name == 'Automated Testing':
                    # Tier 1 Gate Injection
                    if not self._tier1_approval():
                        print("Tier 1 Approval Denied. Halting pipeline.")
                        break
                    print("Tier 1 Approval Granted. Proceeding to production planning.")
                
                elif stage_name == 'Production Deployment':
                    # Tier 2 Gate Injection
                    if self._tier2_secure_approval(stage_name):
                        print("--- PRODUCTION DEPLOYMENT EXECUTING ---")
                        time.sleep(1.5)
                        print("Production deployment successful.")
                    else:
                        # This path is hit if the user denies ('N') the Y/N question in the Tier 2 prompt
                        print("Production deployment denied by human operator.")
                        break
            
            print("\nDeployment Agent finished execution successfully.")

        except AuthorizationFailure as e:
            print(f"\n!!! SECURITY VIOLATION !!!: {e}")
            print("Agent terminated due to critical authorization failure.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

# Example usage (for testing purposes, not part of the required solution structure output):
"""
# print("\n--- Running Exercise 1: ConfigAgent ---")
# agent1 = ConfigAgent()
# agent1.run()

# print("\n--- Running Exercise 2: DataMigrationAgent ---")
# tasks = ["file_a", "file_b", "file_c_CRITICAL_REVIEW", "file_d", "file_e_CRITICAL_REVIEW", "file_f"]
# agent2 = DataMigrationAgent(tasks)
# agent2.run()

# print("\n--- Running Exercise 3: AnalysisAgent ---")
# agent3 = AnalysisAgent()
# agent3.run()

# print("\n--- Running Exercise 4: DeploymentAgent (Interactive Challenge) ---")
# agent4 = DeploymentAgent()
# agent4.run()
"""

if __name__ == "__main__":
    AnalysisAgent().run()
