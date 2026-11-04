import json
import os
from typing import Dict

from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_classic.memory import ConversationBufferWindowMemory
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

# --- 1. Setup and Configuration ---
# The endpoint, model and key come from the environment; nothing about the
# provider is hard-coded here.
BASE_URL = os.environ.get("OPENAI_COMPATIBLE_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("OPENAI_COMPATIBLE_MODEL", "~deepseek/deepseek-flash-latest")

try:
    # A low temperature keeps the planner close to the sequence it is given.
    llm = ChatOpenAI(
        temperature=0.1,
        model=MODEL,
        base_url=BASE_URL,
        api_key=os.environ.get("OPENAI_COMPATIBLE_API_KEY"),
    )
except Exception as e:
    print(f"FATAL ERROR: could not initialize the LLM client: {e}")
    print("Set OPENAI_COMPATIBLE_API_KEY before running this script.")
    raise SystemExit(1)


# --- 2. Long-Term Memory (RAG Simulation) ---
# In a real system, this would be a VectorStore query. Here, we simulate retrieval.
KNOWLEDGE_BASE: Dict[str, str] = {
    "Project Alpha": "Initial market reports showed high demand for sustainable, subscription-based services in Q4 2023.",
    "Project Beta": "Competitor analysis revealed that pricing above $19.99 significantly reduced conversion rates for niche software tools.",
    "Current Product Idea": "A personalized AI-driven recipe planner targeting busy professionals."
}

def retrieve_rag_context(query: str) -> str:
    """Simulates retrieving relevant long-term knowledge based on the query."""
    if "pricing" in query.lower() or "conversion" in query.lower():
        return KNOWLEDGE_BASE["Project Beta"]
    return KNOWLEDGE_BASE["Project Alpha"]

# --- 3. External Tool Definition (Function Calling) ---

@tool
def external_market_data_search(query: str) -> str:
    """
    Searches an external database for current market saturation and competitor features.
    Returns a JSON string containing key market data points.
    """
    if "recipe planner" in query.lower():
        return json.dumps({
            "market_saturation": "High (7/10)",
            "key_competitors": ["MealPrep AI", "ChefBot Pro"],
            "competitor_pricing_range": "$14.99 - $24.99",
            "unique_feature_gap": "Lack of integrated grocery delivery functionality."
        })
    return json.dumps({"status": "No specific data found."})

tools = [external_market_data_search]

# --- 4. The Cognitive Architecture Prompt (Planning & Reflection) ---

# This prompt forces the agent into a specific, structured thought process. The
# ReAct slots ({tools}, {tool_names}, {agent_scratchpad}, {chat_history}, {input})
# are what the executor fills on every step; the sequence below is the policy.
SYSTEM_PROMPT = """
You are the Strategic Analyst Agent. Your goal is to refine a product idea based on internal knowledge and external data.

Your thought process MUST adhere to the following strict sequence:

1. **RAG Retrieval:** First, retrieve relevant internal knowledge using the current product idea and any known constraints.
2. **Tool Execution:** Next, use the `external_market_data_search` tool to gather current competitor and saturation data.
3. **Reflection:** Analyze the retrieved internal knowledge (RAG) alongside the external market data (Tool Output). Identify conflicts, opportunities, and risks.
4. **Final Plan:** Based on your reflection, provide a refined strategic recommendation for the product idea, including pricing suggestions and feature adjustments.

Use the available tools only when instructed in the planning step.

You have access to the following tools:

{tools}

Stop writing as soon as you have written the Action Input line. Never write the
Observation line yourself: the system appends the real observation and then asks
you to continue.

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Previous conversation:
{chat_history}

Question: {input}
Thought:{agent_scratchpad}
"""

# --- 5. Agent Initialization and Execution ---

# Initialize short-term memory (stores conversation history). The prompt is a
# string template, so the history is injected as text.
memory = ConversationBufferWindowMemory(
    k=5,
    memory_key="chat_history",
    return_messages=False
)

# Define the input task
product_idea = "A personalized AI-driven recipe planner targeting busy professionals."
initial_task = f"""
Analyze the following product idea: '{product_idea}'.
Use all available resources (RAG and Tools) to generate a refined strategy.
"""

# Step 1: Inject RAG Context into the initial prompt before execution.
# This simulates the RAG step where context is retrieved and prepended to the user query.
rag_context = retrieve_rag_context(product_idea)
full_prompt_with_rag = f"--- INTERNAL KNOWLEDGE (RAG CONTEXT) ---\n{rag_context}\n\n--- USER TASK ---\n{initial_task}"

# Create the agent executor
prompt = PromptTemplate.from_template(SYSTEM_PROMPT)
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True,
)

print(f"Executing Agent with Initial Task:\n{full_prompt_with_rag}\n")

# Step 2: Run the agent
result = agent_executor.invoke({"input": full_prompt_with_rag})

print("\n--- FINAL STRATEGIC RECOMMENDATION ---")
print(result["output"])
