import asyncio
from typing import Dict, Any, List

# --- Structured Worker Output ---
AgentResult = Dict[str, Any]

class SourceReliabilityAgent:
    def __init__(self, id: int = 1):
        self.agent_type = "SourceReliabilityAgent"

    async def execute_verification(self, source_reliability_score: float) -> AgentResult:
        await asyncio.sleep(0.5) 
        
        rationale = (
            "Source is highly authoritative (Peer-Reviewed Journal)." 
            if source_reliability_score >= 0.7 
            else "Source is low quality (Unverified Blog Post)."
        )
        
        # 1. Standardized dictionary output
        return {
            'confidence_score': source_reliability_score,
            'rationale': rationale,
            'agent_type': self.agent_type
        }

class DataVerificationAgent:
    def __init__(self, id: int = 2):
        self.agent_type = "DataVerificationAgent"

    async def execute_verification(self, factual_accuracy_score: float) -> AgentResult:
        await asyncio.sleep(1.0) 
        
        rationale = (
            "Factual claim matches internal knowledge base."
            if factual_accuracy_score >= 0.8
            else "Factual claim contains inaccuracies."
        )
        
        # 1. Standardized dictionary output
        return {
            'confidence_score': factual_accuracy_score,
            'rationale': rationale,
            'agent_type': self.agent_type
        }

# --- Manager Synthesis Logic ---
class FactValidationManager:
    def __init__(self):
        self.source_agent = SourceReliabilityAgent()
        self.data_agent = DataVerificationAgent()
    
    def _synthesize_results(self, results: List[AgentResult]) -> Dict[str, Any]:
        
        # Identify results by agent type
        source_result = next(r for r in results if r['agent_type'] == "SourceReliabilityAgent")
        data_result = next(r for r in results if r['agent_type'] == "DataVerificationAgent")

        source_score = source_result['confidence_score']
        data_score = data_result['confidence_score']
        
        final_score = 0.0
        applied_rule = ""
        veto_rationale = ""
        
        # 2. Rule A (Source Veto)
        if source_score < 0.4:
            final_score = min(0.6, data_score) # Cap at 0.6
            applied_rule = "Rule A (Source Veto Applied)"
            
            veto_rationale = (
                f"Source reliability ({source_score:.2f}) is below 0.4 (Unreliable Source). "
                f"Final confidence capped at 0.6."
            )
        
        # 2. Rule B (Weighted Average)
        else:
            final_score = (data_score * 0.6) + (source_score * 0.4)
            applied_rule = "Rule B (Weighted Average)"
            veto_rationale = (
                f"Source is reliable. Final score calculated using 60% Data Verification ({data_score:.2f}) "
                f"and 40% Source Reliability ({source_score:.2f})."
            )

        # 2. Final Rationale Compilation
        comprehensive_rationale = (
            f"--- Synthesis Summary ({applied_rule}) ---\n"
            f"Source Agent Finding: Score={source_score:.2f}. Rationale: '{source_result['rationale']}'\n"
            f"Data Agent Finding: Score={data_score:.2f}. Rationale: '{data_result['rationale']}'\n"
            f"Manager Decision: {veto_rationale}"
        )
        
        return {
            "final_confidence_score": round(final_score, 3),
            "final_rationale": comprehensive_rationale,
            "raw_results": results
        }


    async def validate_statement(self, statement: str, source_score: float, data_score: float) -> Dict[str, Any]:
        print(f"\n[MANAGER] Validating statement: '{statement}'")
        
        coros = [
            self.source_agent.execute_verification(source_score),
            self.data_agent.execute_verification(data_score)
        ]
        
        raw_results = await asyncio.gather(*coros)
        
        return self._synthesize_results(raw_results)

async def main_exercise_3():
    manager = FactValidationManager()
    statement = "Whale lifespan and diet facts."

    # 3. Scenario 1: High reliability (Rule B)
    print("\n--- SCENARIO 1: High Reliability (Expected: ~0.84) ---")
    report_1 = await manager.validate_statement(statement, source_score=0.9, data_score=0.8)
    print(f"\n[SCENARIO 1 FINAL SCORE]: {report_1['final_confidence_score']}")
    print("-" * 50)
    print(report_1['final_rationale'])
    
    # 3. Scenario 2: Low reliability source (Rule A Veto)
    print("\n--- SCENARIO 2: Low Reliability Source Veto (Expected: 0.60) ---")
    report_2 = await manager.validate_statement(statement, source_score=0.3, data_score=0.95)
    print(f"\n[SCENARIO 2 FINAL SCORE]: {report_2['final_confidence_score']}")
    print("-" * 50)
    print(report_2['final_rationale'])

if __name__ == "__main__":
    asyncio.run(main_exercise_3())
