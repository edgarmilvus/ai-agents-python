import os
import json
import sqlite3
from typing import List, Dict, Any

# LangChain imports for memory and simulation
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.embeddings import FakeEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_classic.memory import VectorStoreRetrieverMemory, ConversationBufferWindowMemory
from langchain_classic.chains import LLMChain
from langchain_core.prompts import PromptTemplate

# --- 1. PERSISTENCE CONFIGURATION ---
DB_PATH = "agent_history.db"
CONFIG_PATH = "agent_config.json"
CHROMA_DIR = "agent_semantic_memory"

# --- 2. AGENT CLASS DEFINITION ---

class PersistentResearchAgent:
    """
    An agent that manages its state across three persistence layers: 
    JSON (config), SQLite (history), and Chroma (semantic memory).
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.llm = FakeListChatModel(
            responses=["Acknowledged.", "That is interesting.", "Based on our past conversation, I remember that fact.", "The capital of the persistent country is Persistence City."]
        )
        self.session_count = 0
        
        # Initialize persistence components
        self._load_config_state()
        self._setup_history_db()
        self._setup_vector_store()
        self._setup_agent_chain()

    def _load_config_state(self):
        """Loads simple state (session count) from JSON or initializes if not found."""
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                data = json.load(f)
                # Increment session counter on load
                self.session_count = data.get("session_count", 0) + 1
            print(f"--- Loaded Config: Starting Session {self.session_count} for User {self.user_id} ---")
        else:
            self.session_count = 1
            print(f"--- Initializing New Config: Starting Session {self.session_count} ---")

    def _setup_history_db(self):
        """Sets up SQLite connection and ensures history table exists."""
        self.conn = sqlite3.connect(DB_PATH)
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY, 
                user_id TEXT,
                turn INTEGER,
                user_input TEXT, 
                agent_response TEXT
            )
        """)
        self.conn.commit()
        
        # Load existing history for the current user into a LangChain buffer memory
        history_rows = cursor.execute(
            "SELECT user_input, agent_response FROM history WHERE user_id = ? ORDER BY turn ASC", 
            (self.user_id,)
        ).fetchall()
        
        # Convert raw SQL data into LangChain message format
        messages = []
        for user_msg, ai_msg in history_rows:
            messages.append(HumanMessage(content=user_msg))
            messages.append(AIMessage(content=ai_msg))
            
        # Initialize short-term memory buffer with loaded history
        self.chat_history = ConversationBufferWindowMemory(
            k=5, 
            memory_key="history", 
            return_messages=True,
            # The chain also receives `semantic_context`, so the memory has to be
            # told which input is the user's turn; otherwise saving the context
            # cannot tell the two inputs apart.
            input_key="input",
        )
        self.chat_history.chat_memory.messages = messages
        print(f"History Loaded: {len(history_rows)} previous turns retrieved.")

    def _setup_vector_store(self):
        """Initializes or loads the persistent Chroma vector store for semantic memory."""
        # Use a dummy embedding function since we are simulating the LLM
        embeddings = FakeEmbeddings(size=5) 
        
        # Initialize Chroma, which automatically loads if the directory exists
        self.vectorstore = Chroma(
            persist_directory=CHROMA_DIR, 
            embedding_function=embeddings
        )
        
        # Create a retriever memory component
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
        self.semantic_memory = VectorStoreRetrieverMemory(
            retriever=retriever, 
            memory_key="semantic_context"
        )
        print(f"Semantic Store Initialized/Loaded from {CHROMA_DIR}.")

    def _setup_agent_chain(self):
        """Establishes the core prompt and chain, integrating all memory components."""
        template = (
            "You are a Persistent Research Agent. Your goal is to provide concise answers. "
            "Use the following context and history to inform your response. \n\n"
            "Semantic Context (Long-term Facts):\n{semantic_context}\n"
            "Conversation History (Short-term):\n{history}\n"
            "User Query: {input}"
        )
        prompt = PromptTemplate.from_template(template)
        
        # Combine all memory components into the chain
        self.chain = LLMChain(
            llm=self.llm,
            prompt=prompt,
            verbose=False,
            memory=self.chat_history # Note: VectorStoreRetrieverMemory is often implicitly added via the prompt template
        )

    def run_query(self, query: str):
        """Executes a query and updates history."""
        # 1. Retrieve semantic context first (handled implicitly by the chain or manually injected)
        # For simplicity with FakeLLM, we rely on the prompt template to pass the context.
        
        # 2. Execute the chain
        response = self.chain.run(
            input=query, 
            semantic_context=self.semantic_memory.load_memory_variables({"query": query})['semantic_context']
        )
        
        # 3. Persist the turn to SQLite
        cursor = self.conn.cursor()
        turn_number = len(self.chat_history.chat_memory.messages) // 2 + 1
        cursor.execute(
            "INSERT INTO history (user_id, turn, user_input, agent_response) VALUES (?, ?, ?, ?)",
            (self.user_id, turn_number, query, response)
        )
        self.conn.commit()
        
        return response

    def teach_fact(self, fact: str):
        """Adds a fact directly to the persistent vector store."""
        # LangChain's VectorStoreRetrieverMemory uses add_documents under the hood.
        self.vectorstore.add_texts([fact])
        print(f"\n[Knowledge Added]: Fact '{fact}' successfully persisted to Chroma.")

    def save_state(self):
        """Commits all three persistence layers."""
        # 1. Save Config (JSON)
        with open(CONFIG_PATH, 'w') as f:
            json.dump({"user_id": self.user_id, "session_count": self.session_count}, f)
        
        # 2. Save History (SQLite is saved implicitly via self.conn.commit() in run_query)
        # We perform one final commit just in case.
        self.conn.commit()
        self.conn.close()
        
        # 3. Save Semantic Memory (Chroma persistence)
        self.vectorstore.persist()
        print("\n[State Saved]: All persistence layers committed successfully. Agent shut down.")

# --- 3. EXECUTION SIMULATION ---

USER_ID = "User_A42"

def cleanup():
    """Removes persistence files for a clean start."""
    if os.path.exists(DB_PATH): os.remove(DB_PATH)
    if os.path.exists(CONFIG_PATH): os.remove(CONFIG_PATH)
    if os.path.exists(CHROMA_DIR): 
        import shutil
        # Windows refuses to delete the store while Chroma still holds a handle;
        # this cleanup is best effort, and the folder lives under output/.
        shutil.rmtree(CHROMA_DIR, ignore_errors=True)
    print("\n--- Persistence Files Cleaned Up ---")

if __name__ == "__main__":
    cleanup()
    
    # --- SESSION 1: Establishing State and Knowledge ---
    print("\n[START] --- SESSION 1 ---")
    agent1 = PersistentResearchAgent(USER_ID)
    
    # 1. Initial Query (History and Semantic Memory are empty)
    agent1.run_query("Hello, I am setting up my persistent agent.")
    
    # 2. Teaching a new fact (Persists to Chroma)
    fact_to_learn = "The primary focus of this project is long-term persistence."
    agent1.teach_fact(fact_to_learn)
    
    # 3. Another query to create history
    agent1.run_query("What did I just say about setting up the agent?")
    
    agent1.save_state()
    del agent1 # Simulate system shutdown

    # --- SESSION 2: Retrieving Persisted State and Knowledge ---
    print("\n[START] --- SESSION 2 (New Process) ---")
    agent2 = PersistentResearchAgent(USER_ID) # Loads history, config, and semantic memory
    
    # 4. History Check (Uses SQLite history to answer contextually)
    # The agent should remember the previous turn's context ("What did I just say...?")
    response_history = agent2.run_query("Based on the last thing I asked, what was the agent's response?")
    print(f"\n[History Retrieval Test]: Response -> {response_history}")
    
    # 5. Semantic Memory Check (Uses Chroma to retrieve the taught fact)
    response_semantic = agent2.run_query("What is the primary focus of this project?")
    print(f"\n[Semantic Retrieval Test]: Response -> {response_semantic}")
    
    agent2.save_state()
    cleanup()
