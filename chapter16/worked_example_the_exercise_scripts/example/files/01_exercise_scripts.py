import os
import uuid
from typing import Any, Dict
from langsmith import traceable, Client
from langchain_core.tools import tool
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_classic.agents import AgentExecutor, create_openai_tools_agent

# --- Setup ---
# Ensure environment variables are set:
# os.environ["LANGCHAIN_API_KEY"] = "..."
# os.environ["OPENAI_COMPATIBLE_API_KEY"] = "..."
# os.environ["LANGCHAIN_TRACING_V2"] = "true"

# The endpoint, model and key come from the environment: the same listing runs
# against any OpenAI-compatible gateway. `MODEL_ECONOMY` is the second model in
# the cost comparison, and defaults to the first so the code runs with one model.
BASE_URL = os.environ.get("OPENAI_COMPATIBLE_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("OPENAI_COMPATIBLE_MODEL", "~deepseek/deepseek-flash-latest")
MODEL_ECONOMY = os.environ.get("OPENAI_COMPATIBLE_MODEL_ECONOMY", MODEL)
OPENAI_COMPATIBLE_API_KEY = os.getenv("OPENAI_COMPATIBLE_API_KEY")

client = Client()
llm = ChatOpenAI(temperature=0.0, model=MODEL,
                 base_url=BASE_URL, api_key=OPENAI_COMPATIBLE_API_KEY)

# --- Exercise 1 Code ---

def run_financial_analysis(request: str) -> Dict[str, Any]:
    """
    Simulates a financial extraction task, tracing the process.
    This function uses the 'client.create_run' context manager 
    to manually control the root span and attach custom metadata.
    """
    
    # Generate unique ID for simulation
    session_id = str(uuid.uuid4())
    
    # Define the custom metadata and tags for the root run
    root_config = {
        "project_name": "Financial-Auditor-V1",
        "tags": ["finance", "extraction"],
        "metadata": {
            "user_id": session_id,
            "environment": "production"
        }
    }

    # Define the extraction chain
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert financial extractor. Given a request, extract the percentage (as a float) and the base amount (as a float). Respond only with a JSON object {{'percentage': float, 'base_amount': float}}."),
        ("human", "{request}")
    ])
    
    extraction_chain = prompt | llm | StrOutputParser()
    
    # Use the client context manager to start the root run
    with client.create_run(
        name="Financial Analysis Run",
        run_type="chain",
        inputs={"request": request},
        **root_config
    ) as root_run:
        
        # Execute the extraction chain within the context
        result = extraction_chain.invoke({"request": request})
        
        # Update the root run with the output
        root_run.outputs = {"extracted_data": result}
        client.update_run(root_run)
        
        return result

# Example invocation for Exercise 1:
# print("--- Running Exercise 1: Custom Tracing ---")
# run_financial_analysis("Calculate 15.5% of $12,500 for tax purposes.")


# --- Exercise 2 Code ---

@tool
def inventory_checker(amount: str) -> str:
    """
    Checks the inventory level for a required amount. 
    Requires the input 'amount' to be a string that can be converted directly 
    into a positive integer.
    """
    try:
        # CRITICAL VALIDATION: Must be an integer (int)
        required_int = int(amount.strip().replace('"', '').replace("'", ''))
        
        if required_int <= 0:
            raise ValueError("Amount must be positive.")
            
        if required_int > 500:
            return f"Inventory check successful. {required_int} units are available."
        else:
            return f"Inventory check successful. Only {required_int} units are needed."
            
    except ValueError as e:
        # This is the exception we aim to trace in LangSmith
        raise ValueError(f"Tool input validation failed. Input '{amount}' is not a valid positive integer. Error: {e}")

def build_inventory_prompt():
    """The prompt both inventory configurations share."""
    return ChatPromptTemplate.from_messages([
        ("system", "You are a precise inventory management assistant. Use the 'inventory_checker' tool to determine stock levels. When responding to the tool, ensure your input is ONLY the numerical value."),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad")
    ])

def setup_inventory_agent():
    """Sets up the agent for Exercise 2."""
    tools = [inventory_checker]
    
    # A generic prompt that often leads to non-compliant tool inputs
    prompt = build_inventory_prompt()
    
    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor

# Example invocation for Exercise 2 (designed to fail):
# agent_executor = setup_inventory_agent()
# print("\n--- Running Exercise 2: Debugging Tool Failure ---")
# try:
#     # This input often causes the LLM to output "150 units" or "The amount is 150"
#     agent_executor.invoke({"input": "I need to check the inventory for 150 items. Please confirm stock availability."})
# except Exception as e:
#     print(f"Agent execution failed as expected. Check LangSmith trace for root cause.")


# --- Exercise 3 Code (Setup only, execution is conceptual) ---

# We use the same setup_inventory_agent function for complexity, 
# but focus on configuration details during invocation.

def run_cost_comparison(agent_executor: AgentExecutor, input_query: str):
    """
    Runs the agent with different configurations to compare costs via tracing.
    """
    
    # Configuration 1: the premium model
    print("Running Configuration 1: High Cost Model")
    llm_high_cost = ChatOpenAI(model=MODEL, temperature=0.1,
                               base_url=BASE_URL, api_key=OPENAI_COMPATIBLE_API_KEY)
    
    # Re-create agent with high cost model for accurate token calculation
    high_cost_agent = AgentExecutor(
        agent=create_openai_tools_agent(llm_high_cost, agent_executor.tools, build_inventory_prompt()),
        tools=agent_executor.tools
    )
    
    high_cost_agent.invoke(
        {"input": input_query},
        config={
            "tags": ["cost-test", "high-cost-model"],
            "metadata": {"model_version": MODEL, "budget_tier": "premium"},
            "project_name": "Agent-Cost-Analysis"
        }
    )

    # Configuration 2: the economy model
    print("Running Configuration 2: Low Cost Model")
    llm_low_cost = ChatOpenAI(model=MODEL_ECONOMY, temperature=0.1,
                              base_url=BASE_URL, api_key=OPENAI_COMPATIBLE_API_KEY)
    
    low_cost_agent = AgentExecutor(
        agent=create_openai_tools_agent(llm_low_cost, agent_executor.tools, build_inventory_prompt()),
        tools=agent_executor.tools
    )
    
    low_cost_agent.invoke(
        {"input": input_query},
        config={
            "tags": ["cost-test", "low-cost-model"],
            "metadata": {"model_version": MODEL_ECONOMY, "budget_tier": "standard"},
            "project_name": "Agent-Cost-Analysis"
        }
    )

# Example invocation for Exercise 3:
# agent_for_cost = setup_inventory_agent()
# print("\n--- Running Exercise 3: Cost Comparison ---")
# run_cost_comparison(agent_for_cost, "I need to confirm the stock for 350 items. Is this feasible?")


# --- Exercise 4 Code (Partial setup for modification) ---

# Assume the previous advanced script defined a complex agent setup function:
def setup_research_agent(model_temp: float, policy_tag: str):
    """
    A foundational function that sets up a complex research agent 
    with multiple tools (e.g., search, code execution). 
    This adheres to the DRY principle by factoring out common setup logic.
    """
    
    # Placeholder for complex tools defined in previous subsections
    # tools = [google_search_tool, code_interpreter_tool] 
    
    # For this exercise, we use simple placeholders
    @tool
    def search_tool(query: str) -> str:
        """Searches the web for relevant information."""
        return f"Search results for: {query}"
        
    @tool
    def calculator_tool(expression: str) -> str:
        """Performs simple mathematical calculations."""
        try:
            return str(eval(expression))
        except:
            return "Error calculating expression."

    tools = [search_tool, calculator_tool]
    
    llm_modified = ChatOpenAI(temperature=model_temp, model=MODEL,
                              base_url=BASE_URL, api_key=OPENAI_COMPATIBLE_API_KEY)
    
    # The prompt defines the policy
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"You are a meticulous research assistant operating under the '{policy_tag}' policy. Always prioritize using the 'search_tool' first, regardless of the simplicity of the query."),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad")
    ])
    
    agent = create_openai_tools_agent(llm_modified, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=False,
        handle_parsing_errors=True
    )
    return agent_executor

# Example invocation for Exercise 4 (Policy A):
# agent_A = setup_research_agent(model_temp=0.1, policy_tag="Policy A - Search First")
# print("\n--- Running Exercise 4: Policy A ---")
# agent_A.invoke(
#     {"input": "What is the square root of 144 plus the current year?"},
#     config={"tags": ["policy-A", "comparison"], "project_name": "Agent-Policy-Drift"}
# )

# Example invocation for Exercise 4 (Policy B):
# agent_B = setup_research_agent(model_temp=0.9, policy_tag="Policy B - Calculator First")
# print("\n--- Running Exercise 4: Policy B ---")
# agent_B.invoke(
#     {"input": "What is the square root of 144 plus the current year?"},
#     config={"tags": ["policy-B", "comparison"], "project_name": "Agent-Policy-Drift"}
# )
