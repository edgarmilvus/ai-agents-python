import os
import json
import requests
from datetime import datetime
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_classic.agents import AgentExecutor, create_structured_chat_agent
from langchain_core.tools import StructuredTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# --- Configuration and Environment Setup ---
# The endpoint, model and key come from the environment (see the setup at the top
# of the book); DATA_FILE is relative to the folder the script runs in.
DATA_FILE = "market_history.json"

# --- 1. Tool Input Schemas (Pydantic) ---

class StockFetchInput(BaseModel):
    """Input schema for fetching stock data."""
    ticker: str = Field(description="The stock ticker symbol (e.g., 'GOOG', 'MSFT').")

class DataLogInput(BaseModel):
    """Input schema for logging data to the file."""
    ticker: str = Field(description="The stock ticker symbol.")
    price: float = Field(description="The current price of the stock.")
    volume: int = Field(description="The current trading volume.")

# --- 2. Tool Implementations (The External Connectors) ---

def fetch_stock_price(ticker: str) -> str:
    """
    Simulates fetching real-time stock price and volume from an external API.
    In a real application, this would use a library like yfinance or a paid API.
    """
    print(f"--- [TOOL CALL] Fetching data for {ticker} via simulated API...")
    
    # Dummy API simulation based on the ticker
    if ticker.upper() == "GOOG":
        price = 175.50
        volume = 2500000
    elif ticker.upper() == "MSFT":
        price = 420.15
        volume = 1500000
    else:
        return json.dumps({"error": f"Ticker {ticker} not found in simulated data."})

    data = {
        "ticker": ticker.upper(),
        "price": price,
        "volume": volume,
        "timestamp": datetime.now().isoformat()
    }
    
    # The agent receives the result as a string
    return json.dumps(data)

def log_market_data(ticker: str, price: float, volume: int) -> str:
    """
    Logs the fetched market data into a persistent local JSON file.
    This demonstrates file I/O capabilities for state management.
    """
    print(f"--- [TOOL CALL] Logging data for {ticker} to {DATA_FILE}...")
    
    new_entry = {
        "ticker": ticker,
        "price": price,
        "volume": volume,
        "timestamp": datetime.now().isoformat()
    }
    
    # Read existing data or initialize
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []
    else:
        history = []

    history.append(new_entry)
    
    # Write updated data back to the file
    with open(DATA_FILE, 'w') as f:
        json.dump(history, f, indent=4)
        
    return f"Successfully logged {ticker} price {price} and volume {volume} to the history file."

# --- 3. Agent Setup ---

# Define the LLM. The endpoint, model and key come from the environment, so the
# same listing runs against any OpenAI-compatible gateway.
BASE_URL = os.environ.get("OPENAI_COMPATIBLE_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("OPENAI_COMPATIBLE_MODEL", "~deepseek/deepseek-flash-latest")

try:
    llm = ChatOpenAI(
        temperature=0,
        model=MODEL,
        base_url=BASE_URL,
        api_key=os.environ.get("OPENAI_COMPATIBLE_API_KEY"),
    )
except Exception as e:
    print(f"FATAL ERROR: could not initialize the LLM client: {e}")
    print("Set OPENAI_COMPATIBLE_API_KEY before running this script.")
    raise SystemExit(1)

# Structure the Python functions as tools for the LLM
tools = [
    StructuredTool.from_function(
        func=fetch_stock_price,
        name="fetch_stock_price",
        description="Retrieves the current stock price and trading volume for a given ticker.",
        args_schema=StockFetchInput
    ),
    StructuredTool.from_function(
        func=log_market_data,
        name="log_market_data",
        description="Persistently saves market data (ticker, price, volume) to the local history file.",
        args_schema=DataLogInput
    )
]

# Define the prompt template. The system message carries the tool list and the
# JSON contract; `agent_scratchpad` is interpolated as text, because that is what
# the executor passes (a message placeholder would receive a string and fail).
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a diligent Market Research Agent. Your goal is to fetch real-time market data using the available tools, log the transaction for persistence, and then summarize the findings for the user.

You have access to the following tools:

{tools}

Respond with a single JSON blob naming one action:
{{"action": $TOOL_NAME, "action_input": $INPUT}}

Valid "action" values: "Final Answer" or [{tool_names}]."""),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}\n\n{agent_scratchpad}\n\n(reminder: respond with one JSON blob)"),
])

# Create the agent
agent = create_structured_chat_agent(llm, tools, prompt)

# Create the executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# --- 4. Execution ---

user_query = "Please find the current price and volume for MSFT, and ensure this data is logged for historical tracking. Then tell me the price."

print(f"\n[USER INPUT]: {user_query}")
result = agent_executor.invoke({"input": user_query})

print("\n[FINAL AGENT RESPONSE]:")
print(result["output"])

# Optional: Display the contents of the generated file
print(f"\n[FILE CHECK]: Contents of {DATA_FILE} after execution:")
with open(DATA_FILE, 'r') as f:
    print(json.dumps(json.load(f), indent=2))
