import pickle
import os
import time
import sqlite3
import asyncio
from typing import List, Dict, Tuple

# --- Utility Functions for Exercise 10.4.3 (Semantic Memory) ---

def dot_product(vec_a: List[float], vec_b: List[float]) -> float:
    """Calculates the dot product of two vectors."""
    return sum(a * b for a, b in zip(vec_a, vec_b))

def magnitude(vec: List[float]) -> float:
    """Calculates the magnitude (L2 norm) of a vector."""
    return sum(x**2 for x in vec)**0.5

def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Calculates the cosine similarity between two vectors."""
    mag_a = magnitude(vec_a)
    mag_b = magnitude(vec_b)
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot_product(vec_a, vec_b) / (mag_a * mag_b)


# --- Exercise 10.4.1: Serializable Agent Configuration ---

class TaskAgent:
    """Agent class demonstrating state serialization via pickle."""
    
    def __init__(self, agent_id: str, operational_mode: str = "Standard"):
        self.agent_id = agent_id
        self.operational_mode = operational_mode
        self.tasks_completed = 0
        self.successful_tasks = 0
        self.total_tasks = 0

    def complete_task(self, success: bool):
        """Updates internal metrics based on task outcome."""
        self.tasks_completed += 1
        self.total_tasks += 1
        if success:
            self.successful_tasks += 1
        
        rate = (self.successful_tasks / self.total_tasks) * 100 if self.total_tasks > 0 else 0.0
        print(f"[{self.agent_id}] Task completed. Total: {self.tasks_completed}. Success Rate: {rate:.2f}%")

    def save_state(self, filepath: str):
        """Serializes the current agent instance using pickle."""
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(self, f)
            print(f"Configuration saved successfully to {filepath}")
        except Exception as e:
            print(f"Error saving state: {e}")

    @staticmethod
    def load_state(filepath: str) -> 'TaskAgent':
        """Deserializes an agent instance from a pickle file."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"State file not found at {filepath}")
        try:
            with open(filepath, 'rb') as f:
                agent = pickle.load(f)
            print(f"Configuration loaded for Agent ID: {agent.agent_id}")
            return agent
        except Exception as e:
            print(f"Error loading state: {e}")
            raise

# --- Exercise 10.4.2: Asynchronous History Manager (using asyncio.to_thread for standard sqlite3) ---

class AsyncHistoryManager:
    """Asynchronous context manager for SQLite history logging."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._conn = None

    async def _execute(self, query: str, params: tuple = ()):
        """Wrapper to run blocking SQLite operations asynchronously."""
        # Note: In production, use a dedicated async library like aiosqlite.
        # This implementation uses asyncio.to_thread for educational purposes.
        if not self._conn:
            raise RuntimeError("Database connection not established.")
        
        def blocking_op():
            cursor = self._conn.cursor()
            cursor.execute(query, params)
            self._conn.commit()
            return cursor.fetchall()
            
        return await asyncio.to_thread(blocking_op)

    async def _connect_and_setup(self):
        """Establishes connection and ensures table existence."""
        # Connection establishment is also blocking, handled by to_thread
        self._conn = await asyncio.to_thread(sqlite3.connect, self.db_path)
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL
        );
        """
        await self._execute(create_table_sql)

    async def __aenter__(self):
        """Enters the asynchronous context, connecting to the DB."""
        await self._connect_and_setup()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exits the asynchronous context, closing the connection."""
        if self._conn:
            await asyncio.to_thread(self._conn.close)
            self._conn = None
            
        if exc_type is not None:
            # Handle exceptions here (e.g., logging)
            print(f"History Manager encountered an error: {exc_val}")
            
    async def log_message(self, role: str, content: str):
        """Logs a single message into the history table."""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
        insert_sql = "INSERT INTO history (timestamp, role, content) VALUES (?, ?, ?)"
        await self._execute(insert_sql, (timestamp, role, content))
        
    async def get_recent_history(self, limit: int) -> List[Dict[str, str]]:
        """Retrieves the most recent messages."""
        select_sql = "SELECT role, content FROM history ORDER BY id DESC LIMIT ?"
        
        def blocking_select():
            cursor = self._conn.cursor()
            cursor.execute(select_sql, (limit,))
            return cursor.fetchall()

        results = await asyncio.to_thread(blocking_select)
        
        # Format results for the agent context (oldest first)
        formatted_history = []
        for role, content in reversed(results):
            formatted_history.append({"role": role, "content": content})
            
        return formatted_history


# --- Exercise 10.4.3: Simplified Vector Store Simulation ---

class SemanticMemory:
    """Simulates a vector store using basic Python math and cosine similarity."""
    
    def __init__(self):
        # Store format: {doc_id: (text_content, vector)}
        self.store: Dict[str, Tuple[str, List[float]]] = {}
        self.doc_counter = 0

    def add_document(self, content: str, vector: List[float]):
        """Indexes a new document with its pre-calculated vector."""
        doc_id = f"doc_{self.doc_counter}"
        if len(vector) != 4:
            raise ValueError("Vectors must be 4-dimensional for this simulation.")
        self.store[doc_id] = (content, vector)
        self.doc_counter += 1
        print(f"Indexed document {doc_id}.")

    def retrieve_context(self, query_vector: List[float], k: int = 1) -> List[str]:
        """Retrieves the top k most semantically similar documents."""
        if not self.store:
            return []

        similarity_scores = []
        for doc_id, (content, vector) in self.store.items():
            score = cosine_similarity(query_vector, vector)
            similarity_scores.append((score, content))

        # Sort by score descending and take top k
        similarity_scores.sort(key=lambda x: x[0], reverse=True)
        
        top_k_results = [content for score, content in similarity_scores[:k]]
        return top_k_results

# --- Demonstration and Integration (Exercise 10.4.4 Setup) ---

class UnifiedPersistentAgent:
    """Integrates all persistence mechanisms."""
    
    def __init__(self, config_path: str, db_path: str, memory_store: SemanticMemory):
        self.config_path = config_path
        self.db_path = db_path
        self.memory_store = memory_store
        self.history_manager = AsyncHistoryManager(db_path)
        self.interaction_count = 0
        
        # Load or initialize agent configuration
        try:
            loaded_agent = TaskAgent.load_state(config_path)
            self.agent_state = loaded_agent
        except FileNotFoundError:
            print("No existing configuration found. Initializing new agent.")
            self.agent_state = TaskAgent("Unified-P-Agent")

    async def _simulate_llm_response(self, prompt_context: str) -> str:
        """Simulates LLM call based on the prompt content."""
        if "Python syntax" in prompt_context:
            return "Based on your query and the retrieved knowledge, Python uses 'def' for function definition."
        if "Session 1" in prompt_context:
            return "I remember our conversation about the database schema from Session 1."
        
        return f"Agent Response (Tasks Completed: {self.agent_state.tasks_completed}). Context length: {len(prompt_context)} chars."

    async def run_interaction(self, user_query: str):
        self.interaction_count += 1
        
        # 1. Simulate embedding the user query (for retrieval)
        # Assume 'database schema' query vector is [0.9, 0.1, 0.1, 0.1]
        # Assume 'basic syntax' query vector is [0.1, 0.9, 0.1, 0.1]
        
        if "schema" in user_query.lower():
            query_vec = [0.9, 0.1, 0.1, 0.1]
        elif "function" in user_query.lower():
            query_vec = [0.1, 0.9, 0.1, 0.1]
        else:
            query_vec = [0.0, 0.0, 0.0, 0.0] # Neutral query
            
        # A. Knowledge Retrieval (Semantic Memory)
        retrieved_context = self.memory_store.retrieve_context(query_vec, k=1)
        semantic_context = "\n---\nRetrieved Knowledge:\n" + "\n".join(retrieved_context) + "\n---" if retrieved_context else ""

        # B. History Retrieval (Short-Term Persistence)
        async with self.history_manager as hm:
            recent_history = await hm.get_recent_history(limit=5)
            
            history_str = "\n".join([f"[{msg['role'].upper()}]: {msg['content']}" for msg in recent_history])
            history_context = "\n\n--- Recent Conversation History ---\n" + history_str + "\n---"

            # C. Prompt Construction
            full_prompt = (
                f"SYSTEM INSTRUCTIONS: You are a persistent agent. Use the following context to answer.\n"
                f"{semantic_context}"
                f"{history_context}"
                f"\n\nUSER QUERY: {user_query}"
            )

            # D. Response Generation and Logging
            agent_response = await self._simulate_llm_response(full_prompt)
            
            # Log interaction
            await hm.log_message("user", user_query)
            await hm.log_message("agent", agent_response)

        # E. Checkpointing (Configuration Persistence)
        self.agent_state.complete_task(success=True) # Assume success for logging
        if self.agent_state.tasks_completed % 10 == 0:
            self.agent_state.save_state(self.config_path)

        print(f"\n[AGENT]: {agent_response}")
        print(f"--- Interaction {self.interaction_count} Complete ---")
        
        
async def main_demonstration():
    # --- Setup Paths ---
    CONFIG_FILE = "agent_config.pkl"
    DB_FILE = "agent_history.db"

    # Clean up previous runs for a fresh start simulation. On Windows a file
    # left behind by an interrupted run may still be locked: removing it is best
    # effort, and the demonstration continues either way.
    if os.path.exists(DB_FILE):
        try:
            os.remove(DB_FILE)
        except OSError:
            print(f"Could not remove {DB_FILE}; continuing with it in place.")
    if not os.path.exists(CONFIG_FILE):
        # Pre-seed the config for checkpointing test
        pre_agent = TaskAgent("Unified-P-Agent")
        for _ in range(8):
            pre_agent.complete_task(True)
        pre_agent.save_state(CONFIG_FILE)
        
    # --- Setup Semantic Memory ---
    memory = SemanticMemory()
    # Vector 1: Focus on Databases/Schema (High 1st dimension)
    memory.add_document("Database Schema: The agent stores conversation history in a relational SQLite table.", [0.9, 0.1, 0.1, 0.1])
    # Vector 2: Focus on Python/Syntax (High 2nd dimension)
    memory.add_document("Python Syntax: Functions are defined using the 'def' keyword and require indentation.", [0.1, 0.9, 0.1, 0.1])
    # Vector 3: Focus on Deployment/Web (Low relevance to current queries)
    memory.add_document("Web Deployment: Use Gunicorn and Nginx for production scaling of Flask applications.", [0.1, 0.1, 0.9, 0.1])

    print("\n--- Starting Session 1 ---")
    agent_s1 = UnifiedPersistentAgent(CONFIG_FILE, DB_FILE, memory)
    print(f"Agent State Loaded: Tasks Completed = {agent_s1.agent_state.tasks_completed}") # Should show 8

    # Interaction 1 (Test History Logging)
    await agent_s1.run_interaction("Hello agent, how do you manage persistence?")
    # Interaction 2 (Test Semantic Retrieval)
    await agent_s1.run_interaction("What is the primary key in the history table schema?")
    
    # Run 8 more interactions to trigger checkpoint at 10 (Total 8 + 10 = 18)
    for i in range(8):
        await agent_s1.run_interaction(f"Filler query {i+1}.")
        
    print("\n--- Simulating System Restart ---")
    # Agent S1 goes out of scope, connections close.

    print("\n--- Starting Session 2 ---")
    agent_s2 = UnifiedPersistentAgent(CONFIG_FILE, DB_FILE, memory)
    
    # Checkpoint verification (should show 18 tasks completed)
    print(f"Agent State Loaded: Tasks Completed = {agent_s2.agent_state.tasks_completed}") 

    # Interaction 11 (Test History and Semantic Retrieval)
    # The agent should retrieve the history from Session 1 and the semantic context.
    await agent_s2.run_interaction("Based on our last discussion, can you remind me how Python defines a function?")
    
    # Final cleanup (optional)
    # os.remove(CONFIG_FILE)
    # os.remove(DB_FILE)

if __name__ == "__main__":
    # This structure ensures the async main function runs correctly
    try:
        asyncio.run(main_demonstration())
    except FileNotFoundError as e:
        print(f"Setup Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
