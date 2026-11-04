import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document

# --- 1. Environment and Setup ---
# Endpoint, model and key come from the environment; the model names below are
# the OpenAI-compatible identifiers the gateway expects.
BASE_URL = os.environ.get("OPENAI_COMPATIBLE_BASE_URL", "https://openrouter.ai/api/v1")
LLM_MODEL = os.environ.get("OPENAI_COMPATIBLE_MODEL", "~deepseek/deepseek-flash-latest")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
VECTOR_DB_PATH = "./chroma_db_hippocampus"

# Initialize components
llm = ChatOpenAI(
    model=LLM_MODEL,
    temperature=0.1,
    base_url=BASE_URL,
    api_key=os.environ.get("OPENAI_COMPATIBLE_API_KEY"),
)
# Embeddings may need their own endpoint and key: a chat gateway does not
# necessarily serve an embeddings API.
EMBEDDING_BASE_URL = os.environ.get("EMBEDDING_BASE_URL", BASE_URL)
EMBEDDING_API_KEY = os.environ.get("EMBEDDING_API_KEY", os.environ.get("OPENAI_COMPATIBLE_API_KEY"))
embeddings = OpenAIEmbeddings(
    model=EMBEDDING_MODEL,
    base_url=EMBEDDING_BASE_URL,
    api_key=EMBEDDING_API_KEY,
    # Send raw strings, not token ids: Gemini's compatible layer rejects tokens.
    check_embedding_ctx_length=False,
)

# --- 2. Simulated Knowledge Base (The Agent's Historical Records) ---
# We simulate loading documents by creating them in memory.
historical_records = [
    Document(page_content="Project Alpha Q1 2023: Focused on infrastructure migration. Budget overrun was 15%. Key dependency: Legacy API v2. Success metric: 85% uptime."),
    Document(page_content="Project Beta Q2 2023: Focused on new UI/UX design. Budget was exactly on target. Key dependency: Project Alpha completion. Success metric: 75% user engagement increase."),
    Document(page_content="Project Gamma Q3 2023: Focused on AI integration for customer support. Budget was 5% under target. Key dependency: High-performance GPU cluster acquisition. Success metric: 40% reduction in human support tickets."),
    Document(page_content="Project Delta Q4 2023: Focused on international market expansion. Budget overrun was 20%. Key dependency: Legal compliance sign-off. Success metric: 10% revenue increase in Asia region.")
]

# --- 3. Ingestion Pipeline (Creating the Hippocampus Index) ---

# 3a. Text Splitting (Chunking Strategy)
# Use RecursiveCharacterTextSplitter for robust, context-aware chunking.
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=20,
    separators=["\n\n", "\n", " ", ""]
)
split_documents = text_splitter.split_documents(historical_records)

# 3b. Vector Store Creation
# This step embeds the chunks and stores them in the vector database (Chroma).
print(f"Indexing {len(split_documents)} document chunks into the Vector Store...")
vector_store = Chroma.from_documents(
    documents=split_documents,
    embedding=embeddings,
    persist_directory=VECTOR_DB_PATH
)

# --- 4. Agent Retrieval Configuration ---

# 4a. Define the Retriever
# The retriever is the interface to the vector store, configured for similarity search.
retriever = vector_store.as_retriever(search_kwargs={"k": 2}) # Retrieve the top 2 most relevant chunks.

# 4b. Define the Agent's Prompt Template
# This prompt instructs the agent (LLM) how to use the retrieved context.
RAG_PROMPT_TEMPLATE = """
You are a Corporate Strategy Analyst Agent. Your task is to synthesize the provided context 
to answer the user's strategic query. Base your analysis ONLY on the context provided.
If the context does not contain the answer, state that clearly.

Context:

{context}


Query: {question}
"""
custom_prompt = PromptTemplate(
    template=RAG_PROMPT_TEMPLATE,
    input_variables=["context", "question"]
)

# --- 5. RAG Chain Assembly (The Agent's Memory Lookup Mechanism) ---
# Combine the LLM, the retriever, and the custom prompt into a single QA chain.
strategy_agent_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff", # 'Stuff' combines all retrieved documents into one prompt.
    retriever=retriever,
    chain_type_kwargs={"prompt": custom_prompt},
    return_source_documents=True # Useful for debugging and verification
)

# --- 6. Execution: Querying the Agent's Memory ---
strategic_query = (
    "Based on historical project data, which project had the largest budget overrun percentage, "
    "and what was its key technical dependency? Provide a concise summary."
)

print("\n--- Agent Query ---")
print(f"Query: {strategic_query}")

# Execute the chain, which handles retrieval and generation automatically.
result = strategy_agent_chain.invoke({"query": strategic_query})

# --- 7. Output and Analysis ---
print("\n--- Agent Response ---")
print(result["result"])

print("\n--- Retrieved Sources (Memory Recall) ---")
for i, doc in enumerate(result["source_documents"]):
    print(f"Source {i+1}: {doc.page_content}")

# Cleanup (optional, but good practice for persistent stores)
if os.path.exists(VECTOR_DB_PATH):
    import shutil
    # Windows refuses to delete the store while the client still holds a handle;
    # this cleanup is best effort, and the folder lives under output/.
    shutil.rmtree(VECTOR_DB_PATH, ignore_errors=True)
    print(f"\nCleaned up vector store at {VECTOR_DB_PATH}")
