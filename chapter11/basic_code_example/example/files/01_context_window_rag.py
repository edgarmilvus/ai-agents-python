import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_classic.chains import RetrievalQA

# --- 0. Setup and Initialization ---
# The endpoint, model and key come from the environment.
BASE_URL = os.environ.get("OPENAI_COMPATIBLE_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("OPENAI_COMPATIBLE_MODEL", "~deepseek/deepseek-flash-latest")

# CRITICAL: Define the knowledge base (the Agent's "memory")
POLICY_TEXT = """
## Confidential Agent Policy Manual V1.2

Section 1: Operational Mandates. All agents must prioritize resource efficiency. 
The maximum allowable token usage per hour is 50,000. Any deviation requires 
Level 3 supervisor approval.

Section 2: Communication Protocols. Standard communication must use JSON format 
for structured data exchange. Unstructured text is reserved only for initial 
onboarding conversations.

Section 3: Memory Management. Long-term memory storage must utilize a 
Chroma-backed vector database, indexed using 'cosine' similarity. 
The agent's short-term context window is limited to 4096 tokens.
"""

# 1. Document Preparation (Simulating File Load)
# Create a temporary file to simulate a real document load from disk
temp_file_path = "agent_policy.txt"
with open(temp_file_path, "w") as f:
    f.write(POLICY_TEXT)

# Use a Document Loader to ingest the raw text
loader = TextLoader(temp_file_path)
documents = loader.load()

# 2. Chunking (Breaking down the document into manageable pieces)
# Initialize the text splitter to ensure chunks fit within the context window
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500, # Max size of each piece of text
    chunk_overlap=50, # Overlap between chunks to maintain context continuity
    length_function=len,
    is_separator_regex=False,
)
chunks = text_splitter.split_documents(documents)
print(f"Original document split into {len(chunks)} chunks.")

# 3. Embedding and Storage (Creating the Vector Store/Hippocampus)
# Initialize the embedding model (converts text into high-dimensional vectors)
# This model mathematically represents the meaning of the text
# Embeddings may live behind a different endpoint than the chat model: a gateway
# that serves chat does not necessarily serve embeddings.
EMBEDDING_BASE_URL = os.environ.get("EMBEDDING_BASE_URL", BASE_URL)
EMBEDDING_API_KEY = os.environ.get("EMBEDDING_API_KEY", os.environ.get("OPENAI_COMPATIBLE_API_KEY"))
embeddings_model = OpenAIEmbeddings(
    model=os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small"),
    base_url=EMBEDDING_BASE_URL,
    api_key=EMBEDDING_API_KEY,
    # Send raw strings, not token ids. Some embedding endpoints (Gemini, behind
    # its OpenAI-compatible layer) answer 501 to the token-array form.
    check_embedding_ctx_length=False,
)

# Create the in-memory vector store (Chroma DB) from the chunks and embeddings
# This is the indexing step: calculating and storing the vector for every chunk
vector_store = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings_model
)
print("Vector store indexing complete. Hippocampus initialized.")

# 4. Retrieval Chain Setup
# Define the retriever component, which handles the semantic search
retriever = vector_store.as_retriever(search_kwargs={"k": 1}) # Retrieve only the top 1 result

# Initialize the LLM (The "Brain")
llm = ChatOpenAI(
    model=MODEL,
    temperature=0.0,
    base_url=BASE_URL,
    api_key=os.environ.get("OPENAI_COMPATIBLE_API_KEY"),
)

# Create the Retrieval-Augmented Generation (RAG) chain
# This chain orchestrates the retrieval step and the LLM generation step
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff", # Simple method: stuffs retrieved docs into the prompt
    retriever=retriever
)

# 5. Execution (The Agent's Query)
query = "What is the maximum token usage limit per hour for an agent?"
print(f"\n--- RAG Query: {query} ---")

# Run the RAG chain
response = qa_chain.invoke({"query": query})

# 6. Output and Cleanup
print("\n--- RAG Response ---")
print(response['result'])

# Clean up the temporary file created for simulation
os.remove(temp_file_path)
