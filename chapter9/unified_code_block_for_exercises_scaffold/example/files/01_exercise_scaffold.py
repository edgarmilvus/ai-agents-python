import json
import time
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any

# --- Pydantic and SQLAlchemy Setup Mock ---
# In a real environment, these would be imported from external libraries.
# We simulate their behavior here for functional testing.

class PydanticValidationError(Exception):
    """Custom exception for simulated Pydantic errors."""
    pass

class MockPydanticModel:
    """Simulates basic Pydantic validation and type coercion."""
    
    def __init__(self, **data):
        self._data = data
        self._validate()

    def _validate(self):
        # Mandatory fields and type checks (Simplified)
        if 'score_out_of_10' not in self._data or not isinstance(self._data['score_out_of_10'], int):
            try:
                # Attempt coercion
                self._data['score_out_of_10'] = int(self._data['score_out_of_10'])
            except (ValueError, TypeError, KeyError):
                 raise PydanticValidationError("Score must be an integer.")

        score = self._data['score_out_of_10']
        if not 1 <= score <= 10:
            raise PydanticValidationError(f"Score {score} is out of range (1-10).")

        if 'rationale_summary' not in self._data or not isinstance(self._data['rationale_summary'], str):
             raise PydanticValidationError("Missing or invalid rationale_summary.")

        if 'suggested_refinement_steps' not in self._data:
            raise PydanticValidationError("Missing suggested_refinement_steps list.")
        if not isinstance(self._data['suggested_refinement_steps'], list):
            raise PydanticValidationError("suggested_refinement_steps must be a list.")
        
        if 'critical_error_flag' not in self._data or not isinstance(self._data['critical_error_flag'], bool):
            raise PydanticValidationError("Missing or invalid critical_error_flag.")

    @classmethod
    def parse_raw(cls, json_data: str) -> 'AgentCritique':
        try:
            data = json.loads(json_data)
            return cls(**data)
        except json.JSONDecodeError as e:
            raise PydanticValidationError(f"JSON decoding failed: {e}")

    def dict(self):
        return self._data

# --- Exercise 1: Structured Feedback with Pydantic Validators ---

class AgentCritique(MockPydanticModel):
    """
    Defines the structured schema for agent feedback.
    Fields are validated upon instantiation via MockPydanticModel.
    """
    def __init__(self, 
                 score_out_of_10: int = None, 
                 rationale_summary: str = None, 
                 suggested_refinement_steps: List[str] = None, 
                 critical_error_flag: bool = None,
                 **kwargs):
        # Every field is optional at the signature level, as in Pydantic: a
        # missing key must reach the validator, which reports it, instead of
        # dying with a TypeError before validation runs.
        provided = {
            key: value
            for key, value in (
                ("score_out_of_10", score_out_of_10),
                ("rationale_summary", rationale_summary),
                ("suggested_refinement_steps", suggested_refinement_steps),
                ("critical_error_flag", critical_error_flag),
            )
            if value is not None
        }
        provided.update(kwargs)
        super().__init__(**provided)

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

# Failure Case A (Type/Range Error)
raw_fail_a = json.dumps({
    "score_out_of_10": 15,  # Out of range
    "rationale_summary": "The code is amazing, but the score is too high.",
    "suggested_refinement_steps": [],
    "critical_error_flag": False
})

# Failure Case B (Missing Field Error)
raw_fail_b = json.dumps({
    "score_out_of_10": 5,
    "rationale_summary": "The code is incomplete.",
    "critical_error_flag": True
    # 'suggested_refinement_steps' is missing
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

# Agent weights (Base Weights)
AGENT_WEIGHTS: Dict[str, float] = {
    'Agent_A': 3.0,  # Senior
    'Agent_B': 1.5,  # Junior
    'Agent_C': 2.5   # Mid-Level
}

# Target vector representing the ideal task focus (4D for simplicity)
TARGET_TASK_VECTOR = [0.8, 0.1, 0.7, 0.2] 

def get_embedding(text: str) -> List[float]:
    """
    Mock function simulating an embedding model call. 
    In reality, this would use a library like SentenceTransformer.
    """
    # Simple simulation: vector depends on text length/content
    if "optimization" in text:
        return [0.75, 0.15, 0.8, 0.1]  # High similarity to TARGET_TASK_VECTOR
    if "color scheme" in text:
        return [0.05, 0.9, 0.1, 0.9]   # Low similarity
    return [0.5, 0.3, 0.6, 0.4]        # Medium similarity

def calculate_semantic_similarity(vector_a: List[float], vector_b: List[float]) -> float:
    """
    Calculates cosine similarity between two vectors.
    (Requires numpy in a real environment, simulated here manually/simplified).
    """
    if len(vector_a) != len(vector_b):
        return 0.0

    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    magnitude_a = sum(a**2 for a in vector_a)**0.5
    magnitude_b = sum(b**2 for b in vector_b)**0.5

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
    
    # Cosine Similarity is dot product divided by the product of magnitudes
    similarity = dot_product / (magnitude_a * magnitude_b)
    
    # Clamp similarity between 0 and 1 for weight adjustment
    return max(0.0, min(1.0, similarity))


def calculate_weighted_consensus(
    critiques_with_ids: List[Tuple[str, AgentCritique]], 
    use_semantic_scoring: bool = False,
    task_vector: Optional[List[float]] = None,
) -> Tuple[float, str, bool]:
    """
    Calculates the final consensus score and synthesizes rationale using weights.
    Includes optional semantic scoring for weight adjustment (Ex 4).
    Returns: (Consensus Score, Consolidated Rationale, Critical Veto Status)
    """
    total_weighted_score = 0.0
    total_weight = 0.0
    critical_veto = False
    consolidated_rationales = []
    
    weighted_critiques = []

    # 1. Calculate Adjusted Weights and Check Veto
    for agent_id, critique in critiques_with_ids:
        base_weight = AGENT_WEIGHTS.get(agent_id, 1.0)
        current_weight = base_weight
        
        # Check for Veto (Exercise 2 Requirement 5)
        if critique.dict().get('critical_error_flag', False):
            critical_veto = True
            
        # Semantic Scoring (Exercise 4 Requirement 3)
        if use_semantic_scoring:
            rationale_text = critique.dict().get('rationale_summary', '')
            rationale_vector = get_embedding(rationale_text)
            # The caller may supply the vector it is scoring against; the module
            # constant is the default.
            similarity = calculate_semantic_similarity(
                rationale_vector, task_vector if task_vector is not None else TARGET_TASK_VECTOR
            )
            
            # Adjust weight based on similarity (up to 100% bonus)
            current_weight = base_weight * (1 + similarity)
            print(f"  [Semantic Check] {agent_id}: Base={base_weight:.1f}, Similarity={similarity:.2f}, Adjusted={current_weight:.2f}")

        weighted_critiques.append({
            'agent_id': agent_id,
            'score': critique.dict()['score_out_of_10'],
            'weight': current_weight,
            'rationale': critique.dict()['rationale_summary'],
            'refinements': critique.dict()['suggested_refinement_steps']
        })
        
        total_weighted_score += critique.dict()['score_out_of_10'] * current_weight
        total_weight += current_weight

    # Handle Veto
    if critical_veto:
        return 0.0, "CRITICAL VETO: One or more agents flagged a blocking error.", True

    # 2. Calculate Final Score (Exercise 2 Requirement 3)
    if total_weight == 0:
        return 0.0, "No critiques provided.", False
        
    consensus_score = total_weighted_score / total_weight

    # 3. Rationale Synthesis (Exercise 2 Requirement 4)
    
    # Determine the average weight for filtering
    avg_weight = total_weight / len(weighted_critiques) if weighted_critiques else 0

    consolidated_rationales.append(f"Consensus Score: {consensus_score:.2f}/10.0\n--- Consolidated Feedback ---")
    
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

# --- Exercise 4 Demonstration ---
print("\n--- Exercise 4 Demonstration: Semantic Scoring ---")

# Agent A: High relevance (focus on optimization)
critique_a = AgentCritique(
    score_out_of_10=9, rationale_summary="Excellent optimization strategy, minimal latency found.", 
    suggested_refinement_steps=["Check memory allocation."], critical_error_flag=False
)
# Agent B: Low relevance (focus on superficial aspects)
critique_b = AgentCritique(
    score_out_of_10=7, rationale_summary="The documentation uses a poor color scheme and font choices.", 
    suggested_refinement_steps=["Change font to serif."], critical_error_flag=False
)
# Agent C: Medium relevance
critique_c = AgentCritique(
    score_out_of_10=8, rationale_summary="General structure is good, but error handling needs hardening.", 
    suggested_refinement_steps=["Add try/except blocks."], critical_error_flag=False
)

critiques_ex4 = [
    ('Agent_A', critique_a),
    ('Agent_B', critique_b),
    ('Agent_C', critique_c),
]

# Calculate consensus without semantic scoring (Base Weights)
base_score, _, _ = calculate_weighted_consensus(critiques_ex4, use_semantic_scoring=False)
print(f"Base Consensus Score (No Semantic Adjustment): {base_score:.2f}")

# Calculate consensus WITH semantic scoring (Adjusted Weights)
adjusted_score, rationale, veto = calculate_weighted_consensus(critiques_ex4, use_semantic_scoring=True)
print(f"Adjusted Consensus Score (Semantic Boosted): {adjusted_score:.2f}")
# Agent A's high relevance should pull the score up relative to the base score.


# --- Exercise 3: Iterative Refinement Loop ---

MAX_ITERATIONS = 5
SUCCESS_THRESHOLD = 8.0

def generate_artifact(revision_history: str, iteration: int) -> str:
    """Mock function for the Generator Agent creating or revising work."""
    print(f"\n[Iteration {iteration}] Generator Agent creating Artifact...")
    if iteration == 1:
        content = "Initial Draft: Functionality is 60% complete, focusing on speed."
    elif iteration == 2:
        content = f"Revision 1 based on feedback: Implemented error handling. {revision_history}"
    elif iteration == 3:
        content = f"Revision 2 based on feedback: Implemented optimization. {revision_history}"
    else:
        content = f"Revision {iteration-1}: Final polish. {revision_history}"
    return content

def run_critique_group(artifact: str, iteration: int) -> List[Tuple[str, AgentCritique]]:
    """Mock function for the Reviewer Group providing structured critiques."""
    
    # Simulate scores improving over time
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
    else: # High score for subsequent runs
        scores = [9, 10, 9]
        rationales = ["Perfect.", "Flawless.", "No issues found."]
        critical = False

    critiques = []
    for i, agent_id in enumerate(AGENT_WEIGHTS.keys()):
        critique = AgentCritique(
            score_out_of_10=scores[i],
            rationale_summary=rationales[i],
            suggested_refinement_steps=[f"Fix item {i}"],
            critical_error_flag=critical and (i == 0) # Only Agent A can veto initially
        )
        critiques.append((agent_id, critique))
    return critiques

def refinement_loop():
    """Implements the core iterative refinement process."""
    current_artifact = ""
    revision_feedback = ""
    iteration = 0
    final_score = 0.0

    print("\n--- Exercise 3: Iterative Refinement Loop Start ---")

    while iteration < MAX_ITERATIONS:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")
        
        # 1. Generation/Revision
        current_artifact = generate_artifact(revision_feedback, iteration)
        print(f"Artifact Snippet: {current_artifact[:50]}...")

        # 2. Critique
        critiques = run_critique_group(current_artifact, iteration)

        # 3. Consensus (Using weighted consensus from Ex 2)
        final_score, consolidated_rationale, veto = calculate_weighted_consensus(critiques, use_semantic_scoring=False)
        
        print(f"Consensus Result: Score={final_score:.2f}, Veto={veto}")

        # 4. Validation Check and Decision
        if veto or final_score < SUCCESS_THRESHOLD:
            if veto:
                print("Status: CRITICAL VETO. Revision required.")
            else:
                print(f"Status: Score {final_score:.2f} < Threshold {SUCCESS_THRESHOLD:.1f}. Revision required.")
            
            # Prepare feedback for the next generation cycle
            revision_feedback = consolidated_rationale
            
            if iteration == MAX_ITERATIONS:
                print("LOOP TERMINATED: Max iterations reached without success.")
                break
        else:
            print("Status: SUCCESS! Artifact meets consensus threshold.")
            break
    
    print(f"\n--- Loop Finished. Final Score: {final_score:.2f} ---")

# Run the loop
refinement_loop()


# --- Exercise 5: Auditability and Persistence (SQLAlchemy Mock) ---

# Mock SQLAlchemy Setup
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
        print(f"  [DB] Session committed. {len(self.records)} records persisted.")

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
        else:
            print(f"  [DB] Transaction rolled back due to error: {exc_val}")

db_storage = [] # Global list to simulate the database table

class CritiqueRecord:
    """Mock ORM Model for Persistence."""
    def __init__(self, **kwargs):
        # Simulate Primary Key generation
        self.id = len(db_storage) + 1 
        self.timestamp = datetime.now()
        
        self.artifact_id = kwargs.get('artifact_id')
        self.agent_id = kwargs.get('agent_id')
        self.score_out_of_10 = kwargs.get('score_out_of_10')
        self.rationale_summary = kwargs.get('rationale_summary')
        self.suggested_refinement_steps = kwargs.get('suggested_refinement_steps')
        self.critical_error_flag = kwargs.get('critical_error_flag')

    def __repr__(self):
        return f"<CritiqueRecord id={self.id} agent={self.agent_id} score={self.score_out_of_10}>"


def persist_critique_history(
    session: MockSession, 
    artifact_id: str, 
    critiques: List[Tuple[str, AgentCritique]]
):
    """
    Persists structured critique data to the database within a session.
    """
    print(f"\nPersisting {len(critiques)} critiques for artifact {artifact_id}...")
    
    for agent_id, critique in critiques:
        critique_data = critique.dict()
        
        # Convert list of strings to JSON string for database storage
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
        db_storage.append(record) # Simulate adding to the global table

# --- Exercise 5 Demonstration ---
print("\n--- Exercise 5: Persistence and Auditability ---")

# Use critiques generated in Exercise 4
artifact_id = 'project_alpha_v2'

# Use the mock session context manager
with MockSession() as session:
    persist_critique_history(session, artifact_id, critiques_ex4)

print(f"\nTotal records in simulated DB: {len(db_storage)}")
for record in db_storage:
    print(record)
