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
    DeploymentAgent().run()
