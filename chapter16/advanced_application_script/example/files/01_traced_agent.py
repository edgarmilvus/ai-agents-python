import os
from typing import List, Union
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_classic.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 1. Environment Configuration for LangSmith Tracing
# CRITICAL: LangSmith tracing is automatically enabled by these variables.
# The 'LANGCHAIN_PROJECT' defines the specific project workspace in LangSmith.
# Defaulted on, because tracing is what this chapter is about; set it to "false"
# to run the agent without a LangSmith account.
os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
os.environ["LANGCHAIN_PROJECT"] = "Financial Agent Observability Demo"
# Note: OPENAI_COMPATIBLE_API_KEY and LANGCHAIN_API_KEY must be set in your actual environment.
# The endpoint, model and key come from the environment: the same listing runs
# against any OpenAI-compatible gateway. Tracing goes to LangSmith when its key
# is set, and stays off when it is not.
BASE_URL = os.environ.get("OPENAI_COMPATIBLE_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("OPENAI_COMPATIBLE_MODEL", "~deepseek/deepseek-flash-latest")
MODEL_ECONOMY = os.environ.get("OPENAI_COMPATIBLE_MODEL_ECONOMY", MODEL)
OPENAI_COMPATIBLE_API_KEY = os.getenv("OPENAI_COMPATIBLE_API_KEY")

# --- 2. Define Custom Tools for the Agent ---
# These tools represent the external capabilities the agent can access.

@tool
def search_financial_news(query: str) -> str:
    """Searches recent financial news headlines for a given company or topic. 
    Use this for questions about current market events or company updates."""
    print(f"--- TOOL CALL: Searching news for '{query}' ---")
    if "Tesla" in query:
        return "Tesla stock is up 5% following news of a new battery factory opening in Texas."
    elif "Inflation" in query:
        return "The Federal Reserve announced interest rates will remain steady for Q4."
    else:
        return f"No specific recent news found for {query}. The market is quiet."

@tool
def calculate_simple_growth(initial_value: Union[int, float], growth_rate: Union[int, float]) -> float:
    """Calculates the final value after one period of simple growth. 
    Requires two numerical inputs: initial_value (e.g., 5000) and growth_rate (e.g., 12 for 12%)."""
    print(f"--- TOOL CALL: Calculating growth: {initial_value} * (1 + {growth_rate/100}) ---")
    # Assuming growth_rate is provided as a percentage (e.g., 10 for 10%)
    return float(initial_value) * (1 + (float(growth_rate) / 100))

tools: List = [search_financial_news, calculate_simple_growth]

# --- 3. Agent Setup (ReAct Framework) ---

# Define the LLM (Low temperature ensures consistent decision-making for debugging)
llm = ChatOpenAI(temperature=0, model=MODEL,
                 base_url=BASE_URL, api_key=OPENAI_COMPATIBLE_API_KEY)

# Define the Prompt Template
# The system message is crucial for guiding the agent's tool selection logic.
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a specialized financial research assistant. Use the provided tools to answer questions. If the question involves market events, use the search tool. If it involves future value projection, use the calculation tool. Always provide a clear final answer."),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)

# Create the Agent (ReAct logic)
agent = create_openai_tools_agent(llm, tools, prompt)

# Create the Executor
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True, 
    handle_parsing_errors=True
)

# --- 4. Execution and Tracing Demonstration ---

print("\n=======================================================")
print("RUN 1: Tool Usage - Search (External Dependency Path)")
print("=======================================================")
# Query 1 forces the agent down the search_financial_news path.
result_1 = agent_executor.invoke({"input": "What is the latest news affecting Tesla stock?"})
print(f"\nFINAL ANSWER 1: {result_1['output']}")

print("\n=======================================================")
print("RUN 2: Tool Usage - Calculation (Internal Logic Path)")
print("=======================================================")
# Query 2 forces the agent down the calculate_simple_growth path.
result_2 = agent_executor.invoke({"input": "If I invest $5000 and expect a 12% return this year, what is the projected value?"})
print(f"\nFINAL ANSWER 2: {result_2['output']}")

# LangSmith automatically provides a URL in the verbose output for each run.
print("\n--- TRACING COMPLETE ---")
print(f"Check your LangSmith project '{os.environ['LANGCHAIN_PROJECT']}' for detailed traces of both runs.")
