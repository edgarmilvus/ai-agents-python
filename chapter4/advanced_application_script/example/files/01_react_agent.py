import os
import json
from typing import Dict, Any

# LangChain imports for Agent construction
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_classic.agents import create_react_agent, AgentExecutor

# --- 1. Define External Tools for the Agent ---

@tool
def get_stock_price(ticker: str) -> str:
    """
    Retrieves the current market price for a given stock ticker symbol.
    Simulates an API call to a financial data service.
    """
    print(f"\n[TOOL CALLED] Fetching price for: {ticker}")
    
    # Mock data for deterministic execution
    data = {
        "TSLA": 185.50,
        "GOOGL": 170.25,
        "MSFT": 420.00
    }
    
    price = data.get(ticker.upper())
    if price:
        return f"The current price of {ticker.upper()} is ${price:.2f}."
    else:
        return f"Error: Ticker {ticker.upper()} not found in mock database."

@tool
def calculate_momentum_score(payload: str) -> str:
    """
    Calculates a simple relative momentum score from a JSON object with the keys
    "price" and "historical_avg" (e.g. {"price": 185.5, "historical_avg": 175.0}).
    Returns a score and analysis.
    """
    print(f"\n[TOOL CALLED] Calculating momentum score...")

    # A ReAct loop hands a tool one string, so the two numbers travel as JSON.
    try:
        data = json.loads(payload)
        price = float(data["price"])
        historical_avg = float(data["historical_avg"])
    except (TypeError, ValueError, KeyError):
        return 'Error: input must be JSON like {"price": 185.5, "historical_avg": 175.0}.'

    if historical_avg == 0:
        return "Error: Historical average cannot be zero for calculation."

    # Simple momentum calculation: (Current Price / Historical Avg) - 1
    score = ((price / historical_avg) - 1) * 100
    
    analysis = ""
    if score > 5.0:
        analysis = "Strong positive momentum (Buy signal)."
    elif score > 0:
        analysis = "Weak positive momentum (Hold signal)."
    else:
        analysis = "Negative momentum (Sell signal)."
        
    return json.dumps({
        "score": round(score, 2),
        "analysis": analysis
    })

# List of tools available to the agent
tools = [get_stock_price, calculate_momentum_score]

# --- 2. Configure LLM and ReAct Prompt Template ---

# Initialize the LLM; endpoint, model and key come from the environment.
BASE_URL = os.environ.get("OPENAI_COMPATIBLE_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("OPENAI_COMPATIBLE_MODEL", "~deepseek/deepseek-flash-latest")

try:
    llm = ChatOpenAI(
        temperature=0.0,
        model=MODEL,
        base_url=BASE_URL,
        api_key=os.environ.get("OPENAI_COMPATIBLE_API_KEY"),
    )
except Exception as e:
    print(f"FATAL ERROR: could not initialize the LLM client: {e}")
    print("Set OPENAI_COMPATIBLE_API_KEY before running this script.")
    raise SystemExit(1)

# CRITICAL: Define the ReAct prompt template. This is where the Chain of Thought (CoT)
# structure (Thought, Action, Observation) is explicitly enforced.
REACT_PROMPT_TEMPLATE = """
You are an expert Market Analyst Agent. Your goal is to analyze a stock and provide a recommendation.
You have access to the following tools:

{tools}

Use one of the following tool names: [{tool_names}]

Use the following format:
Question: the input question you must answer
Thought: your internal reasoning and plan to solve the problem. This is where you use Chain of Thought.
Action: the exact name of the tool to use, strictly from the list of available tools.
Action Input: the input to the tool.
Observation: the result of the tool.
... (repeat Thought/Action/Observation until the final answer is reached)
Thought: I have gathered all necessary information and can now provide the final answer.
Final Answer: the comprehensive recommendation.

Begin!

Previous work:
{agent_scratchpad}

Question: {input}
Thought:
"""

prompt = ChatPromptTemplate.from_template(REACT_PROMPT_TEMPLATE)

# --- 3. Assemble and Execute the ReAct Agent ---

# Create the ReAct agent using the defined tools, LLM, and prompt structure
agent = create_react_agent(llm, tools, prompt)

# Create the Agent Executor, which manages the iterative loop
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True, 
    handle_parsing_errors=True
)

# Define the complex query requiring multiple steps
query = (
    "Analyze TSLA. First, retrieve its current price. "
    "Then, calculate its momentum score assuming a historical average of $175.00. "
    "Finally, provide a clear investment recommendation (Buy/Hold/Sell)."
)

print("-" * 80)
print(f"AGENT STARTING: {query}")
print("-" * 80)

# Run the agent executor
result = agent_executor.invoke({"input": query})

print("\n" + "=" * 80)
print("FINAL AGENT OUTPUT:")
print(result['output'])
print("=" * 80)
