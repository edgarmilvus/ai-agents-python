import json
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime

# --- Pydantic and SQLAlchemy Setup Mock ---

class PydanticValidationError(Exception):
    """Custom exception for simulated Pydantic errors."""
    pass

class MockPydanticModel:
    """Simulates basic Pydantic validation and type coercion."""
    
    def __init__(self, **data):
        self._data = data
        self._validate()

    def _validate(self):
        # Placeholder, implemented in subclass
        pass 

    @classmethod
    def parse_raw(cls, json_data: str) -> 'AgentCritique':
        try:
            data = json.loads(json_data)
            return cls(**data)
        except json.JSONDecodeError as e:
            raise PydanticValidationError(f"JSON decoding failed: {e}")
        except TypeError as e:
            raise PydanticValidationError(f"Initialization failed due to type error: {e}")

    def dict(self):
        return self._data

# --- Exercise 1: Structured Feedback with Pydantic Validators ---

class AgentCritique(MockPydanticModel):
    """
    Defines the structured schema for agent feedback.
    """
    def __init__(self, 
                 score_out_of_10: int, 
                 rationale_summary: str, 
                 suggested_refinement_steps: List[str], 
                 critical_error_flag: bool,
                 **kwargs):
        
        self._data = {
            'score_out_of_10': score_out_of_10,
            'rationale_summary': rationale_summary,
            'suggested_refinement_steps': suggested_refinement_steps,
            'critical_error_flag': critical_error_flag,
        }
        self._validate()

    def _validate(self):
        # 1. Score Validation (Type and Range 1-10)
        score = self._data.get('score_out_of_10')
        if not isinstance(score, int):
            raise PydanticValidationError("Field 'score_out_of_10' must be an integer.")
        if not 1 <= score <= 10:
            raise PydanticValidationError(f"Score {score} is out of range (1-10).")

        # 2. Rationale Validation
        rationale = self._data.get('rationale_summary')
        if not isinstance(rationale, str):
             raise PydanticValidationError("Missing or invalid 'rationale_summary' (must be str).")

        # 3. Refinement Steps Validation
        refinements = self._data.get('suggested_refinement_steps')
        if refinements is None:
            raise PydanticValidationError("Missing mandatory field 'suggested_refinement_steps'.")
        if not isinstance(refinements, list):
            raise PydanticValidationError("'suggested_refinement_steps' must be a list.")
        
        # 4. Critical Flag Validation
        flag = self._data.get('critical_error_flag')
        if not isinstance(flag, bool):
            raise PydanticValidationError("Missing or invalid 'critical_error_flag' (must be bool).")

def parse_raw_critique(raw_text: str) -> AgentCritique:
    """Simulates parsing raw LLM JSON output and validating it."""
    print(f"\nAttempting to parse raw text...")
    try:
        critique = AgentCritique.parse_raw(raw_text)
        print("-> SUCCESS: Critique validated successfully.")
        return critique
    except PydanticValidationError as e:
        print(f"-> VALIDATION FAILED: {e}")
        raise

# Successful Case
raw_success = json.dumps({
    "score_out_of_10": 9,
    "rationale_summary": "The logic is sound and highly optimized, but documentation needs minor cleanup.",
    "suggested_refinement_steps": ["Add docstrings to helper functions.", "Verify license header."],
    "critical_error_flag": False
})

# Failure Case A (Range Error)
raw_fail_a = json.dumps({
    "score_out_of_10": 15,
    "rationale_summary": "Too high.",
    "suggested_refinement_steps": [],
    "critical_error_flag": False
})

# Failure Case B (Missing Field Error)
raw_fail_b = json.dumps({
    "score_out_of_10": 5,
    "rationale_summary": "Incomplete.",
    "critical_error_flag": True
})

print("--- Exercise 1 Demonstration ---")
try:
    critique_success = parse_raw_critique(raw_success)
except PydanticValidationError:
    pass

try:
    parse_raw_critique(raw_fail_a)
except PydanticValidationError:
    pass

try:
    parse_raw_critique(raw_fail_b)
except PydanticValidationError:
    pass


# --- Exercise 2 & 4 Setup: Weighted Consensus and Semantic Scoring ---

AGENT_WEIGHTS: Dict[str, float] = {
    'Agent_A': 3.0,  # Senior
    'Agent_B': 1.5,  # Junior
    'Agent_C': 2.5   # Mid-Level
}

TARGET_TASK_VECTOR = [0.8, 0.1, 0.7, 0.2] 

def get_embedding(text: str) -> List[float]:
    """Mock function simulating an embedding model call."""
    if "optimization" in text or "latency" in text:
        return [0.75, 0.15, 0.8, 0.1]  # High similarity
    if "color scheme" in text or "font" in text:
        return [0.05, 0.9, 0.1, 0.9]   # Low similarity
    if "structure" in text or "error handling" in text:
        return [0.5, 0.3, 0.6, 0.4]    # Medium similarity
    return [0.4, 0.4, 0.4, 0.4]

def calculate_semantic_similarity(vector_a: List[float], vector_b: List[float]) -> float:
    """Calculates cosine similarity."""
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    magnitude_a = sum(a**2 for a in vector_a)**0.5
    magnitude_b = sum(b**2 for b in vector_b)**0.5

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
    
    similarity = dot_product / (magnitude_a * magnitude_b)
    return max(0.0, min(1.0, similarity))


def calculate_weighted_consensus(
    critiques_with_ids: List[Tuple[str, AgentCritique]], 
    use_semantic_scoring: bool = False,
    target_vector: Optional[List[float]] = None
) -> Tuple[float, str, bool]:
    """
    Calculates the final consensus score and synthesizes rationale using weights.
    """
    total_weighted_score = 0.0
    total_weight = 0.0
    critical_veto = False
    weighted_critiques = []

    # 1. Calculate Adjusted Weights and Check Veto
    for agent_id, critique in critiques_with_ids:
        base_weight = AGENT_WEIGHTS.get(agent_id, 1.0)
        current_weight = base_weight
        critique_data = critique.dict()
        
        if critique_data.get('critical_error_flag', False):
            critical_veto = True
            
        # Exercise 4: Semantic Scoring Adjustment
        if use_semantic_scoring and target_vector:
            rationale_text = critique_data.get('rationale_summary', '')
            rationale_vector = get_embedding(rationale_text)
            similarity = calculate_semantic_similarity(rationale_vector, target_vector)
            
            # Adjusted Weight = Base Weight * (1 + Similarity Score)
            current_weight = base_weight * (1 + similarity)
            if use_semantic_scoring:
                print(f"  [Semantic Check] {agent_id}: Base={base_weight:.1f}, Similarity={similarity:.2f}, Adjusted={current_weight:.2f}")

        weighted_critiques.append({
            'agent_id': agent_id,
            'score': critique_data['score_out_of_10'],
            'weight': current_weight,
            'rationale': critique_data['rationale_summary'],
            'refinements': critique_data['suggested_refinement_steps']
        })
        
        total_weighted_score += critique_data['score_out_of_10'] * current_weight
        total_weight += current_weight

    # Handle Veto
    if critical_veto:
        return 0.0, "CRITICAL VETO: One or more agents flagged a blocking error.", True

    # 2. Calculate Final Score
    if total_weight == 0:
        return 0.0, "No critiques provided.", False
        
    consensus_score = total_weighted_score / total_weight

    # 3. Rationale Synthesis
    consolidated_rationales = [f"Consensus Score: {consensus_score:.2f}/10.0\n--- Consolidated Feedback ---"]
    avg_weight = total_weight / len(weighted_critiques) if weighted_critiques else 0

    # Prioritize rationales from agents whose weight is above average
    prioritized_rationales = sorted(weighted_critiques, key=lambda x: x['weight'], reverse=True)
    
    for item in prioritized_rationales:
        if item['weight'] >= avg_weight:
            consolidated_rationales.append(
                f"[{item['agent_id']} (Weight: {item['weight']:.2f})]: {item['rationale']}"
            )
            for step in item['refinements']:
                consolidated_rationales.append(f"  - Refinement: {step}")

    return consensus_score, "\n".join(consolidated_rationales), False

# --- Exercise 4 Demonstration (Semantic Scoring) ---
print("\n--- Exercise 4 Demonstration: Semantic Scoring ---")

critique_a_sem = AgentCritique(score_out_of_10=9, rationale_summary="Excellent optimization strategy, minimal latency found.", suggested_refinement_steps=["Check memory allocation."], critical_error_flag=False)
critique_b_sem = AgentCritique(score_out_of_10=7, rationale_summary="The documentation uses a poor color scheme and font choices.", suggested_refinement_steps=["Change font to serif."], critical_error_flag=False)
critique_c_sem = AgentCritique(score_out_of_10=8, rationale_summary="General structure is good, but error handling needs hardening.", suggested_refinement_steps=["Add try/except blocks."], critical_error_flag=False)

critiques_ex4 = [
    ('Agent_A', critique_a_sem),
    ('Agent_B', critique_b_sem),
    ('Agent_C', critique_c_sem),
]

base_score, _, _ = calculate_weighted_consensus(critiques_ex4, use_semantic_scoring=False)
print(f"Base Consensus Score (No Semantic Adjustment): {base_score:.2f}")

adjusted_score, rationale, veto = calculate_weighted_consensus(
    critiques_ex4, 
    use_semantic_scoring=True, 
    target_vector=TARGET_TASK_VECTOR
)
print(f"Adjusted Consensus Score (Semantic Boosted): {adjusted_score:.2f}")


# --- Exercise 3: Iterative Refinement Loop ---

MAX_ITERATIONS = 5
SUCCESS_THRESHOLD = 8.0

def generate_artifact(revision_feedback: str, iteration: int) -> str:
    """Mock function for the Generator Agent creating or revising work."""
    print(f"\n[Iteration {iteration}] Generator Agent creating Artifact...")
    if iteration == 1:
        content = "Initial Draft: Functionality is 60% complete, focusing on speed."
    elif iteration == 2:
        content = f"Revision 1: Implemented error handling and addressed initial feedback.\nFeedback: {revision_feedback[:100]}..."
    elif iteration == 3:
        content = f"Revision 2: Implemented optimization and addressed remaining structural feedback.\nFeedback: {revision_feedback[:100]}..."
    else:
        content = f"Revision {iteration-1}: Final polish based on minor critiques.\nFeedback: {revision_feedback[:100]}..."
    return content

def run_critique_group(artifact: str, iteration: int) -> List[Tuple[str, AgentCritique]]:
    """Mock function for the Reviewer Group providing structured critiques."""
    
    if iteration == 1:
        scores = [6, 7, 5]
        rationales = ["Missing error handling.", "Needs optimization.", "Incomplete features."]
        critical = True
    elif iteration == 2:
        scores = [7, 8, 6]
        rationales = ["Error handling added, but optimization is weak.", "Still needs speed improvement.", "Minor bugs remain."]
        critical = False
    elif iteration == 3:
        scores = [9, 8, 8]
        rationales = ["Optimization is excellent.", "Meets all requirements.", "Ready for deployment."]
        critical = False
    else:
        scores = [9, 10, 9]
        rationales = ["Perfect.", "Flawless.", "No issues found."]
        critical = False

    critiques = []
    agent_ids = list(AGENT_WEIGHTS.keys())
    for i, agent_id in enumerate(agent_ids):
        is_critical = critical and (agent_id == 'Agent_A') 
        
        critique = AgentCritique(
            score_out_of_10=scores[i],
            rationale_summary=rationales[i],
            suggested_refinement_steps=[f"Refinement step {i+1}"],
            critical_error_flag=is_critical
        )
        critiques.append((agent_id, critique))
    return critiques

def refinement_loop():
    """Implements the core iterative refinement process."""
    revision_feedback = "Initial task prompt."
    iteration = 0
    final_score = 0.0

    print("\n--- Exercise 3: Iterative Refinement Loop Start ---")

    while iteration < MAX_ITERATIONS:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")
        
        # 1. Generation/Revision
        current_artifact = generate_artifact(revision_feedback, iteration)

        # 2. Critique
        critiques = run_critique_group(current_artifact, iteration)

        # 3. Consensus 
        final_score, consolidated_rationale, veto = calculate_weighted_consensus(critiques, use_semantic_scoring=False)
        
        print(f"Consensus Result: Score={final_score:.2f}, Veto={veto}")

        # 4. Validation Check and Decision
        if veto or final_score < SUCCESS_THRESHOLD:
            if veto:
                print("Status: CRITICAL VETO. Revision required.")
            else:
                print(f"Status: Score {final_score:.2f} < Threshold {SUCCESS_THRESHOLD:.1f}. Revision required.")
            
            revision_feedback = consolidated_rationale
            
            if iteration == MAX_ITERATIONS:
                print("LOOP TERMINATED: Max iterations reached without success.")
                break
        else:
            print("Status: SUCCESS! Artifact meets consensus threshold.")
            break
    
    print(f"\n--- Loop Finished. Final Score: {final_score:.2f} (Iterations: {iteration}) ---")

refinement_loop()


# --- Exercise 5: Auditability and Persistence (SQLAlchemy Mock) ---

db_storage = [] # Global list to simulate the database table

class MockSession:
    """Simulates a database session for transactional persistence."""
    def __init__(self):
        self.records = []
        self.committed = False
    
    def add(self, record: 'CritiqueRecord'):
        self.records.append(record)
        print(f"  [DB] Added record for Agent {record.agent_id}")

    def commit(self):
        self.committed = True
        for record in self.records:
            db_storage.append(record)
        print(f"  [DB] Session committed. {len(self.records)} records persisted.")

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
        else:
            print(f"  [DB] Transaction rolled back due to error: {exc_val}")

# 1. Define the ORM Model
class CritiqueRecord:
    """Mock ORM Model for Persistence."""
    def __init__(self, **kwargs):
        self.id = len(db_storage) + 1 
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.artifact_id = kwargs.get('artifact_id')
        self.agent_id = kwargs.get('agent_id')
        self.score_out_of_10 = kwargs.get('score_out_of_10')
        self.rationale_summary = kwargs.get('rationale_summary')
        self.suggested_refinement_steps = kwargs.get('suggested_refinement_steps') # JSON string
        self.critical_error_flag = kwargs.get('critical_error_flag')

    def __repr__(self):
        return f"<CritiqueRecord id={self.id} agent={self.agent_id} score={self.score_out_of_10}>"


# 2. Persistence Function
def persist_critique_history(
    session: MockSession, 
    artifact_id: str, 
    critiques: List[Tuple[str, AgentCritique]]
):
    """Persists structured critique data to the database within a session."""
    print(f"\nPersisting {len(critiques)} critiques for artifact {artifact_id}...")
    
    for agent_id, critique in critiques:
        critique_data = critique.dict()
        
        # Convert list of strings to JSON string
        refinement_json = json.dumps(critique_data['suggested_refinement_steps'])
        
        record = CritiqueRecord(
            artifact_id=artifact_id,
            agent_id=agent_id,
            score_out_of_10=critique_data['score_out_of_10'],
            rationale_summary=critique_data['rationale_summary'],
            suggested_refinement_steps=refinement_json,
            critical_error_flag=critique_data['critical_error_flag']
        )
        session.add(record)

# --- Exercise 5 Demonstration ---
print("\n--- Exercise 5: Persistence and Auditability ---")

artifact_id = 'project_alpha_v2'

# Use the mock session context manager
with MockSession() as session:
    # Use the critiques generated in Exercise 4
    persist_critique_history(session, artifact_id, critiques_ex4)

print(f"\nTotal records in simulated DB: {len(db_storage)}")
for record in db_storage:
    refinements = json.loads(record.suggested_refinement_steps)
    print(f"{record} | Refinements: {refinements}")
