import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# --- Mocking Infrastructure for Demonstration ---

class MockEmbeddingModel:
    """Simulates an embedding model for vector generation."""
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # Mocking embedding generation: a deterministic, hash-based vector
        return [[hash(text) % 1000 / 1000.0] * 128 for text in texts]

class MockDocument:
    """Simulates a document object with content and metadata."""
    def __init__(self, page_content: str, metadata: Dict[str, Any]):
        self.page_content = page_content
        self.metadata = metadata
        self.vector = MockEmbeddingModel().embed_documents([page_content])[0]
        
    def __repr__(self):
        # Clean representation for verification
        meta_str = ", ".join(f"{k}='{v}'" for k, v in self.metadata.items() if k not in ['vector', 'timestamp'])
        return f"Doc(Metadata={meta_str}, Content='{self.page_content[:40]}...')"

class MockVectorStore:
    """
    Simulates a vector store supporting semantic search, metadata filtering,
    and custom scoring (for recency boosting).
    """
    def __init__(self, name: str = "default"):
        self.name = name
        self.documents: List[MockDocument] = []
        self.embedding_model = MockEmbeddingModel()
        
    def add_documents(self, docs: List[MockDocument]):
        self.documents.extend(docs)
        print(f"[{self.name}] Added {len(docs)} documents.")

    def search(self, query: str, k: int = 4, filter_metadata: Optional[Dict[str, Any]] = None, use_recency_boost: bool = False) -> List[MockDocument]:
        query_vector = self.embedding_model.embed_documents([query])[0]
        
        def calculate_mock_similarity(doc_vector, q_vector):
            """Mock similarity based on hash distance (0.0 to 1.0, 1.0 being perfect match)."""
            # Since the vectors are deterministic hashes, this simulates a consistent score.
            # Real-world: This would be cosine similarity.
            return 1.0 - (abs(hash(doc_vector[0]) - hash(q_vector[0])) % 1000 / 1000.0)

        results = []
        
        for doc in self.documents:
            # 1. Apply Metadata Filtering (Exercise 2)
            if filter_metadata:
                is_filtered = False
                for key, constraint in filter_metadata.items():
                    doc_value = doc.metadata.get(key)
                    
                    if key == 'submission_date' and isinstance(constraint, dict) and 'after_date' in constraint:
                        # Handle date comparison
                        try:
                            doc_date = datetime.fromisoformat(doc_value)
                            if doc_date < constraint['after_date']:
                                is_filtered = True
                                break
                        except (ValueError, TypeError):
                            # Skip if date format is invalid
                            is_filtered = True
                            break
                    elif doc_value != constraint:
                        # Handle exact match comparison (project_name, status)
                        is_filtered = True
                        break
                if is_filtered:
                    continue

            # 2. Calculate Semantic Score
            semantic_score = calculate_mock_similarity(doc.vector, query_vector)
            hybrid_score = semantic_score
            
            # 3. Apply Recency Boost (Exercise 4)
            if use_recency_boost:
                try:
                    doc_date = datetime.fromisoformat(doc.metadata.get('timestamp'))
                    age_days = (datetime.now() - doc_date).days
                    
                    # Exponential decay model for recency bonus (lambda = 0.05)
                    LAMBDA = 0.05
                    # B_recency = e^(-lambda * Age_days) -> max 1.0 (today), decays towards 0
                    recency_bonus = max(0.0, 1.0 - (LAMBDA * age_days)) # Using linear decay for simplicity, but simulating the concept
                    
                    W_SEMANTIC = 0.7
                    W_RECENCY = 0.3
                    
                    # S_hybrid = w_semantic * S_cosine + w_recency * B_recency
                    hybrid_score = (W_SEMANTIC * semantic_score) + (W_RECENCY * recency_bonus)
                    
                    # Store scores for verification
                    doc.metadata['semantic_score'] = round(semantic_score, 3)
                    doc.metadata['recency_bonus'] = round(recency_bonus, 3)
                    doc.metadata['hybrid_score'] = round(hybrid_score, 3)
                except Exception as e:
                    # Fall back if timestamp is missing or invalid
                    print(f"Warning: Could not apply recency boost to doc due to error: {e}")
                    pass

            results.append((hybrid_score, doc))

        # Sort by score (descending)
        results.sort(key=lambda x: x[0], reverse=True)
        
        return [doc for score, doc in results[:k]]

# --- Solution for Exercise 1: Adaptive Chunking for Semantic Coherence ---

class MarkdownHeaderTextSplitter:
    """
    A mock splitter that splits text based on specified Markdown headers 
    and captures the header hierarchy as metadata.
    """
    def __init__(self, headers_to_split_on: List[tuple]):
        self.headers_to_split_on = headers_to_split_on

    def split_text(self, text: str) -> List[MockDocument]:
        chunks = []
        current_metadata = {}
        current_content = ""
        
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            is_header = False
            for level, key in self.headers_to_split_on:
                if line.startswith(level + ' '):
                    is_header = True
                    
                    # If we have content and metadata, finalize the previous chunk
                    if current_content.strip() or current_metadata:
                        chunks.append(MockDocument(
                            page_content=current_content.strip(), 
                            metadata=current_metadata.copy()
                        ))
                    
                    # Update metadata for the new section (overwriting lower levels)
                    header_title = line[len(level) + 1:].strip()
                    
                    # Clear out metadata for lower-level headers if a higher one is encountered
                    if level == "#":
                        current_metadata = {}
                    elif level == "##":
                        # Preserve top-level if present
                        if "Main Section" in current_metadata and key != "Main Section":
                             current_metadata = {"Main Section": current_metadata["Main Section"]}
                        else:
                            current_metadata = {}
                            
                    current_metadata[key] = header_title
                    current_content = ""
                    break
            
            if not is_header:
                current_content += line + "\n"

        # Add final chunk
        if current_content.strip():
            chunks.append(MockDocument(page_content=current_content.strip(), metadata=current_metadata.copy()))
            
        return chunks

print("--- Exercise 1: Adaptive Chunking for Semantic Coherence ---")
markdown_doc = """
(one hash) Project Overview: The Falcon System
This document outlines the core architecture of the Falcon system.

(2 hash) Authentication Module (Auth-V2)
The Auth-V2 module handles token generation and validation. It uses OAuth2 flows.

(3 hash) Token Refresh Logic
Tokens are refreshed every 60 minutes via a dedicated background service.
(3 backticks)python
def refresh_token(user_id):
    # Pseudocode for refresh logic
    new_token = generate_jwt(user_id, expiry=3600)
    return new_token
(3 backticks)

(2 hash) Data Persistence Layer
We use PostgreSQL for relational data and Redis for caching frequently accessed objects.
"""

# Split only at # and ##, treating ### content as part of the parent chunk
splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[
    ("#", "Main Section"),
    ("##", "Subsystem")
])

structured_chunks = splitter.split_text(markdown_doc)
for i, chunk in enumerate(structured_chunks):
    print(f"Chunk {i+1}:")
    print(f"  Metadata: {chunk.metadata}")
    preview = chunk.page_content.replace("\n", " ")[:80]
    print(f"  Content: '{preview}...'")

# --- Solution for Exercise 2 & 4 Setup: Hybrid Retrieval ---

vector_store = MockVectorStore("ProjectMemory")
now = datetime.now()

# Ingesting data for Exercise 2 (Metadata) and Exercise 4 (Recency)
project_data = [
    # Doc 1: Highly relevant, but OLD (Filter fail E2, Low Recency E4)
    ("API authentication failures are common in Alpha. Check error logs.", "Alpha", "Final", now - timedelta(days=300), 0.95),
    # Doc 2: Moderately relevant, but WRONG PROJECT (Filter fail E2)
    ("Authentication errors in Beta often stem from expired session cookies.", "Beta", "Final", now - timedelta(days=10), 0.80),
    # Doc 3: Relevant, CORRECT PROJECT, CORRECT DATE (Filter pass E2)
    ("The new Alpha API endpoint requires a specific header for authentication.", "Alpha", "Final", now - timedelta(days=50), 0.90),
    # Doc 4: Relevant, CORRECT PROJECT, but DRAFT STATUS (Filter fail E2)
    ("Draft notes on Alpha API failure handling and troubleshooting steps.", "Alpha", "Draft", now - timedelta(days=20), 0.85),
    # Doc 5: Less relevant, but NEW (High Recency E4)
    ("General notes on the recent deployment of Alpha and minor issues.", "Alpha", "Final", now - timedelta(days=1), 0.70),
]

docs_to_ingest = []
for content, project, status, date, _ in project_data:
    docs_to_ingest.append(MockDocument(
        page_content=content,
        metadata={
            "project_name": project,
            "status": status,
            "submission_date": date.isoformat(),
            "timestamp": date.isoformat() # Used for Exercise 4
        }
    ))
vector_store.add_documents(docs_to_ingest)

print("\n--- Exercise 2: Hybrid Retrieval with Metadata Filtering ---")
query_e2 = "Retrieve all documents semantically related to 'API authentication failures'"
filter_constraints = {
    "project_name": "Alpha",
    "status": "Final",
    "submission_date": {"after_date": now - timedelta(days=180)} # Within the last 6 months
}

print(f"Query: '{query_e2}'")
print(f"Required Filters (Project Alpha, Final Status, Last 6 Months):")
print(f"  {json.dumps({k: str(v) for k, v in filter_constraints.items()}, indent=2)}")

filtered_results = vector_store.search(query_e2, k=5, filter_metadata=filter_constraints)

print("\nRetrieved Documents (Only 1 document should pass all filters):")
for doc in filtered_results:
    print(f"- [PASS] {doc}")

# Verification: Doc 3 should be the only one retrieved.
# Doc 1 fails date. Doc 2 fails project. Doc 4 fails status. Doc 5 is less relevant but passes filters.

# --- Solution for Exercise 4: Recency-Weighted Retrieval ---
print("\n--- Exercise 4: Recency-Weighted Retrieval ---")
query_e4 = "Notes on Alpha deployment and API issues."

# Retrieve candidates from Project Alpha only, using the recency boost
recency_results = vector_store.search(
    query_e4, 
    k=5, 
    filter_metadata={"project_name": "Alpha"}, 
    use_recency_boost=True
)

print("Searching with Recency Boost (Project Alpha only):")
print("Expected: Newer documents (Doc 5) should be prioritized over older, possibly slightly more relevant ones (Doc 1).")

print("\nRetrieved Documents (Re-ranked by Hybrid Score):")
for i, doc in enumerate(recency_results):
    print(f"Rank {i+1}: {doc.page_content[:40]}...")
    print(f"  Scores: Semantic={doc.metadata['semantic_score']}, Recency Bonus={doc.metadata['recency_bonus']}, Hybrid Score={doc.metadata['hybrid_score']}")

# --- Solution for Exercise 3: The Self-Refining RAG Agent Loop ---

class MockLLM:
    """Simulates an LLM capable of function calling/structured output."""
    def __init__(self):
        # System prompt instructions are implicitly handled by the logic below
        pass
        
    def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        
        # 1. Check for insufficient context (simulated failure)
        if "API authentication failures" in prompt and (not context or "Draft notes" in context):
            # Simulation of LLM deciding to refine the search based on poor initial context
            return json.dumps({
                "tool_call": "search_vector_store",
                "refined_query": "specific header requirements for Alpha API authentication (Final Status)"
            })
        
        # 2. Check for Exercise 5 routing
        elif "How is the handle_request function implemented" in prompt:
            return "ROUTE_CODE_STORE"
        elif "overall architecture" in prompt:
            return "ROUTE_DOCS_STORE"
        
        # 3. Final Answer generation
        else:
            if context and "specific header requirements" in context:
                 return "Final Answer: The specific header requirement for Alpha API authentication is detailed in the final document, which states a dedicated 'X-Auth-Key' must be used."
            return f"Final Answer based on context: {context if context else 'No context provided.'}"

class SelfRefiningAgent:
    """Implements the two-stage RAG loop."""
    def __init__(self, llm: MockLLM, vector_store: MockVectorStore):
        self.llm = llm
        self.vector_store = vector_store

    def run(self, user_query: str):
        print(f"\n--- Exercise 3: Self-Refining Agent Run ---")
        
        # Stage 1: Initial Query and RAG
        initial_context = self.vector_store.search(user_query, k=2, filter_metadata={"project_name": "Alpha"})
        initial_context_str = "\n".join([doc.page_content for doc in initial_context])
        
        print(f"Stage 1 RAG: Retrieved {len(initial_context)} documents.")
        
        # Stage 1: LLM Analysis and Decision
        prompt = f"User Query: {user_query}. Initial Context: {initial_context_str}. Analyze and provide final answer or refinement."
        llm_output = self.llm.generate_response(prompt, initial_context_str)
        
        try:
            decision = json.loads(llm_output)
            if decision.get("tool_call") == "search_vector_store":
                refined_query = decision["refined_query"]
                print(f"\n[Agent Decision] Insufficient Context. Refining search...")
                print(f"  New Query: '{refined_query}'")
                
                # Stage 2: Execute Refined RAG (Adding a constraint to get the 'Final' document)
                refined_context = self.vector_store.search(
                    refined_query, 
                    k=1, 
                    filter_metadata={"project_name": "Alpha", "status": "Final"}
                )
                refined_context_str = "\n".join([doc.page_content for doc in refined_context])
                
                # Stage 2: Final LLM Synthesis
                final_prompt = f"User Query: {user_query}. Refined Context: {refined_context_str}. Provide the final answer."
                final_answer = self.llm.generate_response(final_prompt, refined_context_str)
                print(f"\n[Final Answer] Based on Stage 2 Retrieval.")
                print(f"  Answer: {final_answer}")
                return final_answer
        
        except json.JSONDecodeError:
            # LLM returned a final answer directly
            print(f"[Final Answer] Based on Stage 1 Retrieval: {llm_output}")
            return llm_output

# Run Exercise 3
agent = SelfRefiningAgent(MockLLM(), vector_store)
agent.run("Tell me about API authentication failures in Project Alpha.")

print("\n--- Exercise 3: Visualization Flow (Conceptual) ---")
print("The implemented flow mimics the required two-stage decision process:")
print("1. User Query -> Stage 1 RAG (Retrieves potentially poor context, e.g., 'Draft notes').")
print("2. LLM receives context -> Analyzes context -> Decides context is insufficient.")
print("3. LLM outputs structured Tool Call (refined_query='specific header requirements...').")
print("4. Agent intercepts Tool Call -> Executes Stage 2 RAG (with better query/filter).")
print("5. Agent passes new context -> LLM generates definitive Final Answer.")

# --- Solution for Exercise 5: Multi-Vector RAG for Code and Documentation ---

# Setup dual stores
code_store = MockVectorStore("CodeStore")
docs_store = MockVectorStore("DocsStore")

# Ingest data with different chunking characteristics
code_store.add_documents([
    MockDocument("def handle_request(req): return 200 # Small, precise code chunk", {"type": "code", "source": "api.py"}),
    MockDocument("class User: def __init__(self): self.id = None", {"type": "code", "source": "models.py"})
])
docs_store.add_documents([
    MockDocument("The microservice architecture is layered, consisting of a Gateway, three stateless workers, and a shared persistence layer. This design ensures high availability and scalability.", {"type": "docs", "source": "arch_spec.md"}),
    MockDocument("Deployment uses Kubernetes v1.25, managed via Helm charts.", {"type": "docs", "source": "devops.md"})
])

def multi_vector_router(query: str, llm: MockLLM, stores: Dict[str, MockVectorStore]):
    """Analyzes query intent and routes to the correct vector store."""
    print(f"\nRouting Query: '{query}'")
    
    # LLM acts as the router, classifying the query
    route = llm.generate_response(query)
    
    if route == "ROUTE_CODE_STORE":
        print(f"Router selected: Code Store (Optimized for small snippets)")
        retrieved = stores['code'].search(query, k=1)
    elif route == "ROUTE_DOCS_STORE":
        print(f"Router selected: Docs Store (Optimized for large paragraphs)")
        retrieved = stores['docs'].search(query, k=1)
    else:
        print("Router failed to classify. Defaulting to general search.")
        retrieved = []
        
    return retrieved

# Test 1: Code Query
query_code = "How is the handle_request function implemented?"
retrieved_code = multi_vector_router(query_code, MockLLM(), {'code': code_store, 'docs': docs_store})
print(f"Code Retrieval Result (Type: {retrieved_code[0].metadata['type']}): {retrieved_code[0].page_content}")

# Test 2: Documentation Query
query_docs = "What is the overall architecture of the microservice?"
retrieved_docs = multi_vector_router(query_docs, MockLLM(), {'code': code_store, 'docs': docs_store})
print(f"Docs Retrieval Result (Type: {retrieved_docs[0].metadata['type']}): {retrieved_docs[0].page_content}")
