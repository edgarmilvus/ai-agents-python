import os
import time
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Mocking necessary external libraries for demonstration purposes
# In a real scenario, these would be imported from LangChain, LlamaIndex, Chroma, etc.
class MockEmbeddingModel:
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # Mocking embedding generation
        return [[hash(text) % 1000 / 1000.0] * 128 for text in texts]

class MockDocument:
    def __init__(self, page_content: str, metadata: Dict[str, Any]):
        self.page_content = page_content
        self.metadata = metadata
        self.vector = MockEmbeddingModel().embed_documents([page_content])[0]
        
    def __repr__(self):
        return f"Doc(Source={self.metadata.get('source', 'N/A')}, Date={self.metadata.get('submission_date', 'N/A')}, Content='{self.page_content[:30]}...')"

class MockVectorStore:
    def __init__(self, name="default"):
        self.name = name
        self.documents = []
        self.embedding_model = MockEmbeddingModel()
        
    def add_documents(self, docs: List[MockDocument]):
        self.documents.extend(docs)
        print(f"[{self.name}] Added {len(docs)} documents.")

    def search(self, query: str, k: int = 4, filter_metadata: Optional[Dict[str, Any]] = None, use_recency_boost: bool = False) -> List[MockDocument]:
        query_vector = self.embedding_model.embed_documents([query])[0]
        
        # Simple mock similarity calculation (using mock hash distance)
        def calculate_similarity(doc_vector, q_vector):
            # In a real system, this would be cosine similarity
            # Here, we use a mock score based on the hash of the content
            return 1.0 - (abs(hash(doc_vector[0]) - hash(q_vector[0])) % 1000 / 1000.0)

        results = []
        for doc in self.documents:
            # 1. Apply Metadata Filtering (Exercise 2)
            if filter_metadata:
                is_filtered = False
                for key, constraint in filter_metadata.items():
                    doc_value = doc.metadata.get(key)
                    
                    # Mock date filtering (assuming constraint is 'after_date')
                    if key == 'submission_date' and 'after_date' in constraint:
                        doc_date = datetime.fromisoformat(doc_value)
                        if doc_date < constraint['after_date']:
                            is_filtered = True
                            break
                    elif doc_value != constraint:
                        is_filtered = True
                        break
                if is_filtered:
                    continue

            # 2. Calculate Semantic Score
            semantic_score = calculate_similarity(doc.vector, query_vector)
            hybrid_score = semantic_score
            
            # 3. Apply Recency Boost (Exercise 4)
            if use_recency_boost:
                doc_date = datetime.fromisoformat(doc.metadata.get('timestamp'))
                age_days = (datetime.now() - doc_date).days
                
                # Decay constant lambda: 0.05 means significant decay over 20 days
                LAMBDA = 0.05 
                recency_bonus = max(0.0, 1.0 - LAMBDA * age_days) # Simple linear decay for mock
                
                W_SEMANTIC = 0.7
                W_RECENCY = 0.3
                hybrid_score = (W_SEMANTIC * semantic_score) + (W_RECENCY * recency_bonus)
                
                # Store scores for verification
                doc.metadata['semantic_score'] = round(semantic_score, 3)
                doc.metadata['recency_bonus'] = round(recency_bonus, 3)
                doc.metadata['hybrid_score'] = round(hybrid_score, 3)

            results.append((hybrid_score, doc))

        # Sort by score (descending)
        results.sort(key=lambda x: x[0], reverse=True)
        
        return [doc for score, doc in results[:k]]

# --- Exercise 1: Adaptive Chunking Setup ---

class MockMarkdownHeaderTextSplitter:
    def __init__(self, headers_to_split_on: List[tuple]):
        self.headers_to_split_on = headers_to_split_on

    def split_text(self, text: str) -> List[MockDocument]:
        # Simplified implementation: split by top-level headers and capture metadata
        chunks = []
        current_metadata = {}
        current_content = ""
        
        lines = text.split('\n')
        for line in lines:
            is_header = False
            for level, key in self.headers_to_split_on:
                if line.startswith(level + ' '):
                    is_header = True
                    # If we have content, finalize the previous chunk
                    if current_content.strip():
                        chunks.append(MockDocument(page_content=current_content.strip(), metadata=current_metadata.copy()))
                    
                    # Start new chunk context
                    header_title = line[len(level) + 1:].strip()
                    current_metadata[key] = header_title
                    current_content = ""
                    break
            
            if not is_header:
                current_content += line + "\n"

        # Add final chunk
        if current_content.strip():
            chunks.append(MockDocument(page_content=current_content.strip(), metadata=current_metadata.copy()))
            
        return chunks

print("--- Exercise 1: Adaptive Chunking ---")
markdown_doc = """
(one hash) Project Overview: The Falcon System
This document outlines the core architecture of the Falcon system.

(2 hash) Authentication Module (Auth-V2)
The Auth-V2 module handles token generation and validation. It uses OAuth2 flows.

(3 hash) Token Refresh Logic
Tokens are refreshed every 60 minutes via a dedicated background service.

(3 backticks)python
def refresh_token(user_id):
    (one hash) Pseudocode for refresh logic
    new_token = generate_jwt(user_id, expiry=3600)
    return new_token
(3 backticks)
(2 hash) Data Persistence Layer
We use PostgreSQL for relational data and Redis for caching frequently accessed objects.
"""

splitter = MockMarkdownHeaderTextSplitter(headers_to_split_on=[
    ("#", "Main Section"),
    ("##", "Subsystem")
])

structured_chunks = splitter.split_text(markdown_doc)
for i, chunk in enumerate(structured_chunks):
    print(f"Chunk {i+1}: Metadata={chunk.metadata}, Content Length={len(chunk.page_content)}")

# --- Exercise 2 & 4: Hybrid Retrieval Setup ---

vector_store = MockVectorStore("ProjectMemory")
now = datetime.now()

# Ingesting data for Exercise 2 (Metadata) and Exercise 4 (Recency)
project_data = [
    # Document 1: Highly relevant, but OLD (Filter fail)
    ("API authentication failures are common in Alpha.", "Alpha", "Final", now - timedelta(days=300)),
    # Document 2: Moderately relevant, but WRONG PROJECT (Filter fail)
    ("Authentication errors in Beta often stem from expired session cookies.", "Beta", "Final", now - timedelta(days=10)),
    # Document 3: Relevant, CORRECT PROJECT, CORRECT DATE (Filter pass)
    ("The new Alpha API endpoint requires a specific header for authentication.", "Alpha", "Final", now - timedelta(days=50)),
    # Document 4: Relevant, CORRECT PROJECT, but DRAFT STATUS (Filter fail)
    ("Draft notes on Alpha API failure handling.", "Alpha", "Draft", now - timedelta(days=20)),
    # Document 5: Less relevant, but NEW (Recency test case)
    ("General notes on the recent deployment of Alpha.", "Alpha", "Final", now - timedelta(days=1)),
]

docs_to_ingest = []
for content, project, status, date in project_data:
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

print("\n--- Exercise 2: Metadata-Driven Context Filtering ---")
query_e2 = "Retrieve information about API authentication failures."
filter_constraints = {
    "project_name": "Alpha",
    "status": "Final",
    "submission_date": {"after_date": now - timedelta(days=180)} # Within the last 6 months
}

filtered_results = vector_store.search(query_e2, k=5, filter_metadata=filter_constraints)
print(f"Query: '{query_e2}' with filters: {json.dumps(filter_constraints, indent=2, default=str)}")
print("Retrieved Documents (Metadata Filtered):")
for doc in filtered_results:
    print(f"- {doc}")
    
# --- Exercise 4: Recency-Weighted Retrieval Demonstration ---
print("\n--- Exercise 4: Recency-Weighted Retrieval ---")
query_e4 = "Notes on Alpha deployment and API issues."

# Scenario: Doc 1 (Old) is semantically stronger than Doc 5 (New) in the mock setup.
# We expect the recency boost to elevate Doc 5.
# Note: Since the mock similarity is hash-based, we rely on the recency boost to dominate the ranking.

print("Searching WITHOUT Recency Boost:")
# We must manually mock the scores to illustrate the concept clearly, as hash similarity is random.
# Assume Doc 1 (Old, High Semantic) and Doc 5 (New, Moderate Semantic) are retrieved.
# In a real test, you'd verify the scores.

# For demonstration, we force the search to use the recency logic.
recency_results = vector_store.search(query_e4, k=5, filter_metadata={"project_name": "Alpha"}, use_recency_boost=True)

print("Retrieved Documents (Recency Boosted):")
for doc in recency_results:
    print(f"- {doc.page_content[:40]}... | Scores: Semantic={doc.metadata['semantic_score']}, Recency={doc.metadata['recency_bonus']}, Hybrid={doc.metadata['hybrid_score']}")

# Verification check: The document "General notes on the recent deployment of Alpha" (the newest one) 
# should appear near the top due to its high recency bonus.

# --- Exercise 3 & 5: Agent and Multi-Vector Setup (Conceptual) ---

# Mock LLM and Agent classes for Exercise 3 and 5

class MockLLM:
    def __init__(self, name="GPT-Mock"):
        self.name = name
        
    def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        # Simplified logic for agent decision making
        if "API authentication failures" in prompt and (not context or "insufficient" in context):
            # Simulation of LLM deciding to refine the search
            return json.dumps({
                "tool_call": "search_vector_store",
                "refined_query": "specific header requirements for Alpha API authentication"
            })
        elif "How is the handle_request function implemented" in prompt:
            # Simulation of LLM routing to CODE_QUERY (Exercise 5)
            return "ROUTE_CODE_STORE"
        elif "overall architecture" in prompt:
            # Simulation of LLM routing to DOCS_QUERY (Exercise 5)
            return "ROUTE_DOCS_STORE"
        else:
            return f"Final Answer based on context: {context if context else 'No context provided.'}"

class SelfRefiningAgent:
    def __init__(self, llm: MockLLM, vector_store: MockVectorStore):
        self.llm = llm
        self.vector_store = vector_store

    def run(self, user_query: str):
        print(f"\n--- Exercise 3: Self-Refining Agent Run ---")
        
        # Stage 1 RAG
        initial_context = self.vector_store.search(user_query, k=2)
        initial_context_str = "\n".join([doc.page_content for doc in initial_context])
        
        print(f"Stage 1 Retrieval Context: {initial_context_str[:50]}...")
        
        # Stage 1 LLM Decision
        prompt = f"User Query: {user_query}. Initial Context: {initial_context_str}. Is this sufficient? If not, output a refined search query."
        llm_output = self.llm.generate_response(prompt, initial_context_str)
        
        try:
            decision = json.loads(llm_output)
            if decision.get("tool_call") == "search_vector_store":
                refined_query = decision["refined_query"]
                print(f"Agent Decision: Refining search to '{refined_query}'")
                
                # Stage 2 RAG
                refined_context = self.vector_store.search(refined_query, k=3)
                refined_context_str = "\n".join([doc.page_content for doc in refined_context])
                
                # Final LLM Synthesis
                final_prompt = f"User Query: {user_query}. Refined Context: {refined_context_str}. Provide the final answer."
                final_answer = self.llm.generate_response(final_prompt, refined_context_str)
                print(f"Final Answer (Stage 2): {final_answer}")
                return final_answer
        except json.JSONDecodeError:
            # Final Answer was returned directly
            print(f"Agent Decision: Context sufficient. Final Answer (Stage 1): {llm_output}")
            return llm_output

# Run Exercise 3
agent = SelfRefiningAgent(MockLLM(), vector_store)
agent.run("Tell me about API authentication failures in Project Alpha.")


print("\n--- Exercise 5: Multi-Vector RAG Routing (Conceptual) ---")

# Setup dual stores
code_store = MockVectorStore("CodeStore")
docs_store = MockVectorStore("DocsStore")

# Ingest data
code_store.add_documents([
    MockDocument("def handle_request(req): return 200", {"type": "code"}),
    MockDocument("class User: def __init__(self): pass", {"type": "code"})
])
docs_store.add_documents([
    MockDocument("The microservice architecture is layered...", {"type": "docs"}),
    MockDocument("Deployment uses Kubernetes v1.25.", {"type": "docs"})
])

def multi_vector_router(query: str, llm: MockLLM, stores: Dict[str, MockVectorStore]):
    # Route decision based on LLM output
    route = llm.generate_response(query)
    
    if route == "ROUTE_CODE_STORE":
        print(f"Router selected: Code Store")
        return stores['code'].search(query, k=1)
    elif route == "ROUTE_DOCS_STORE":
        print(f"Router selected: Docs Store")
        return stores['docs'].search(query, k=1)
    else:
        print("Router failed to classify.")
        return []

# Test Routing
query_code = "How is the handle_request function implemented?"
retrieved_code = multi_vector_router(query_code, MockLLM(), {'code': code_store, 'docs': docs_store})
print(f"Code Retrieval Result: {retrieved_code}")

query_docs = "What is the overall architecture of the microservice?"
retrieved_docs = multi_vector_router(query_docs, MockLLM(), {'code': code_store, 'docs': docs_store})
print(f"Docs Retrieval Result: {retrieved_docs}")
