# --- Exercise 5: SQLAlchemy Mock Setup ---

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
        # Simulate moving records from session buffer to persistent storage
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
    """
    Mock SQLAlchemy ORM Model for persistence of agent critique history.
    """
    def __init__(self, **kwargs):
        # Simulate Primary Key generation and timestamp
        self.id = len(db_storage) + 1 
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.artifact_id = kwargs.get('artifact_id')
        self.agent_id = kwargs.get('agent_id')
        self.score_out_of_10 = kwargs.get('score_out_of_10')
        self.rationale_summary = kwargs.get('rationale_summary')
        self.suggested_refinement_steps = kwargs.get('suggested_refinement_steps') # Stored as JSON string
        self.critical_error_flag = kwargs.get('critical_error_flag')

    def __repr__(self):
        return f"<CritiqueRecord id={self.id} agent={self.agent_id} artifact={self.artifact_id} score={self.score_out_of_10}>"


# 2. Persistence Function
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
        
        # Store the list of strings as a JSON-encoded string
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

# --- 3. Demonstration ---
print("\n--- Exercise 5: Persistence and Auditability ---")

# Reuse the critiques generated in Exercise 4
artifact_id = 'project_alpha_v2'

# Use the mock session context manager to simulate transactional commit
with MockSession() as session:
    persist_critique_history(session, artifact_id, critiques_ex4)

print(f"\nTotal records in simulated DB (db_storage): {len(db_storage)}")
for record in db_storage:
    # Demonstrate retrieval of the JSON field (optional, but shows audit trail)
    refinements = json.loads(record.suggested_refinement_steps)
    print(f"{record} | Rationale: {record.rationale_summary[:30]}... | Refinements: {refinements}")
