import os
import uuid
from typing import Any, Dict, List
from langsmith import traceable, Client
from langchain_core.tools import tool
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_classic.agents import AgentExecutor, create_openai_tools_agent

# The endpoint, model and key come from the environment: the same listing runs
# against any OpenAI-compatible gateway. `MODEL_ECONOMY` is the second model in
# the cost comparison, and defaults to the first so the code runs with one model.
BASE_URL = os.environ.get("OPENAI_COMPATIBLE_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("OPENAI_COMPATIBLE_MODEL", "~deepseek/deepseek-flash-latest")
MODEL_ECONOMY = os.environ.get("OPENAI_COMPATIBLE_MODEL_ECONOMY", MODEL)
OPENAI_COMPATIBLE_API_KEY = os.getenv("OPENAI_COMPATIBLE_API_KEY")

# --- Setup ---
# Initialize clients and LLM
# CRITICAL: Ensure environment variables are set before running.
try:
    client = Client()
    llm = ChatOpenAI(temperature=0.0, model=MODEL,
                     base_url=BASE_URL, api_key=OPENAI_COMPATIBLE_API_KEY)
except Exception as e:
    print(f"Error initializing LangSmith client or LLM: {e}. Check API keys.")

# ----------------------------------------------------------------------
# #### Exercise 1: Tracing Custom Chains and Attaching Metadata
# ----------------------------------------------------------------------

def run_financial_analysis(request: str) -> Dict[str, Any]:
    """
    Simulates a financial extraction task, tracing the process 
    and attaching custom metadata to the root run using the LangSmith Client.
    """
    
    session_id = str(uuid.uuid4())
    
    # Define the custom metadata and tags for the root run
    root_config = {
        "project_name": "Financial-Auditor-V1",
        "tags": ["finance", "extraction", "custom-trace"],
        "metadata": {
            "user_id": session_id,
            "environment": "production",
            "request_type": "tax_calculation"
        }
    }

    # Define the extraction chain
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert financial extractor. Given a request, extract the percentage (as a float) and the base amount (as a float). Respond only with a JSON object {{'percentage': float, 'base_amount': float}}."),
        ("human", "{request}")
    ])
    
    # Use a low-temp model for reliable JSON output
    extraction_chain = prompt | ChatOpenAI(temperature=0.0, model=MODEL,
                                            base_url=BASE_URL,
                                            api_key=OPENAI_COMPATIBLE_API_KEY) | StrOutputParser()
    
    print(f"Starting trace for session: {session_id}")
    
    # Use the client context manager to start the root run
    with client.create_run(
        name="Financial Analysis Root Run",
        run_type="chain",
        inputs={"request": request},
        **root_config
    ) as root_run:
        
        # Execute the extraction chain within the context
        result = extraction_chain.invoke({"request": request})
        
        # Update the root run with the output
        root_run.outputs = {"extracted_data": result}
        client.update_run(root_run)
        
        print(f"Trace completed. View run ID: {root_run.id}")
        return result

# Example invocation for Exercise 1:
print("\n--- Running Exercise 1: Custom Tracing and Metadata ---")
try:
    run_financial_analysis("Calculate 15.5% of $12,500 for tax purposes.")
except Exception as e:
    print(f"Exercise 1 failed: {e}")


# ----------------------------------------------------------------------
# #### Exercise 2: Debugging Non-Deterministic Tool Input Validation
# ----------------------------------------------------------------------

@tool
def inventory_checker(amount: str) -> str:
    """
    Checks the inventory level for a required amount. 
    Requires the input 'amount' to be a string that can be converted directly 
    into a positive integer.
    """
    cleaned_amount = amount.strip().replace('"', '').replace("'", '')
    try:
        # The whole string has to be the number: "150 units" is exactly the
        # non-determinism this exercise is about, so it must not be cleaned away.
        required_int = int(cleaned_amount)
        
        if required_int <= 0:
            raise ValueError("Amount must be positive.")
            
        if required_int > 500:
            return f"Inventory check successful. {required_int} units are available."
        else:
            return f"Inventory check successful. Only {required_int} units are needed."
            
    except ValueError as e:
        # This is the exception we aim to trace in LangSmith
        raise ValueError(f"Tool input validation failed. Input '{amount}' (cleaned: '{cleaned_amount}') is not a valid positive integer. Error: {e}")

def build_inventory_prompt():
    """The prompt both inventory configurations share."""
    return ChatPromptTemplate.from_messages([
        ("system", "You are a precise inventory management assistant. Use the 'inventory_checker' tool. Be descriptive in your thoughts, but ensure the final input to the tool is only the numerical amount."),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad")
    ])

def setup_inventory_agent(model_name: str = MODEL):
    """Sets up the agent for Exercise 2/3."""
    tools = [inventory_checker]
    
    # Prompt designed to be ambiguous, encouraging failure
    prompt = build_inventory_prompt()
    
    agent_llm = ChatOpenAI(model=model_name, temperature=0.0,
                           base_url=BASE_URL, api_key=OPENAI_COMPATIBLE_API_KEY)
    agent = create_openai_tools_agent(agent_llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True,
        handle_parsing_errors=True,
        # Set a common project for all runs
        config={"project_name": "Inventory-Agent-Debugging"}
    )
    return agent_executor

# Example invocation for Exercise 2 (designed to fail):
agent_executor = setup_inventory_agent()
print("\n--- Running Exercise 2: Debugging Tool Failure (Expected Failure) ---")
failure_query = "I need to check the stock level for item X. The required amount is 150 units, please confirm."
try:
    # This input often causes the LLM to output "150 units" or similar non-integer strings
    agent_executor.invoke({"input": failure_query})
except Exception as e:
    print(f"Agent execution failed as expected. Check LangSmith trace for root cause.")


# --- Analysis for Exercise 2: Debugging Non-Deterministic Tool Input Validation ---
"""
**Trace Analysis in LangSmith UI:**


1.  **Root Run:** The top-level run (AgentExecutor) will show a status of `Error`.
2.  **Agent Step (LLM Call):** Navigate into the `ChatOpenAI` span where the agent decides on the tool call. The output of this span (the LLM's response) will contain the `tool_calls` block.
3.  **Tool Call Input:** Inspect the input arguments provided by the LLM to the `inventory_checker` tool. For the failure query, the LLM often incorrectly provides an input like `"150 units"` or `"150, please confirm"`.
4.  **Tool Span Failure:** The subsequent span for the `inventory_checker` tool will also show an `Error` status.
5.  **Exception Details:** Within the tool's span, the traceback and error message will be visible: `ValueError: Tool input validation failed. Input '150 units' is not a valid positive integer...`.

**Conclusion based on Trace Data:**
The agent failed because the LLM, despite the system prompt, included extraneous text (`units`) in the argument passed to the `inventory_checker` tool. The Python code for the tool is strict and cannot convert the string `"150 units"` directly to an integer, leading to a `ValueError`. The trace clearly identifies the exact string output by the LLM that caused the downstream Python exception, allowing the developer to immediately refine the system prompt or, preferably, harden the tool's input parsing logic.
"""


# ----------------------------------------------------------------------
# #### Exercise 3: Run Management, Tagging, and Cost Analysis
# ----------------------------------------------------------------------

def run_cost_comparison(input_query: str):
    """
    Runs the agent with different configurations to compare costs via tracing.
    """
    
    # Configuration 1: the premium model
    print(f"\nRunning Configuration 1: premium model ({MODEL})")
    llm_high_cost = ChatOpenAI(model=MODEL, temperature=0.1,
                               base_url=BASE_URL, api_key=OPENAI_COMPATIBLE_API_KEY)
    
    high_cost_agent = AgentExecutor(
        agent=create_openai_tools_agent(llm_high_cost, [inventory_checker], build_inventory_prompt()),
        tools=[inventory_checker],
        verbose=False
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
    print(f"Running Configuration 2: economy model ({MODEL_ECONOMY})")
    llm_low_cost = ChatOpenAI(model=MODEL_ECONOMY, temperature=0.1,
                              base_url=BASE_URL, api_key=OPENAI_COMPATIBLE_API_KEY)
    
    low_cost_agent = AgentExecutor(
        agent=create_openai_tools_agent(llm_low_cost, [inventory_checker], build_inventory_prompt()),
        tools=[inventory_checker],
        verbose=False
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
query_for_cost = "I need to confirm the stock for exactly 350 items. Is this feasible?"
run_cost_comparison(query_for_cost)


# --- Analysis for Exercise 3: Run Management, Tagging, and Cost Analysis ---
"""
**LangSmith UI Analysis (Agent-Cost-Analysis Project):**


1.  **Filter:** Filter the project by `tag:high-cost-model` and separately by `tag:low-cost-model`.
2.  **Metrics Comparison:** Compare the two root runs (AgentExecutor spans) under the "Metrics" tab.

| Metric | Premium model | Economy model |
| :--- | :--- | :--- |
| Prompt Tokens | ~150-200 | ~150-200 |
| Completion Tokens | ~50-100 | ~50-100 |
| **Total Cost (Estimated)** | Higher (e.g., $0.005 - $0.01) | Significantly Lower (e.g., $0.0001 - $0.0005) |

**Conclusion:**
For the identical inventory query, the premium run consumed similar token counts but resulted in an estimated cost that is substantially higher (often 10x to 20x more) than the economy run. Since the task (simple tool call) is straightforward, the performance benefit of the higher-cost model is negligible, making the economy configuration the clear choice for cost-effectiveness in this specific workflow. LangSmith tracing provides the immediate, quantitative cost data needed to make this optimization decision.
"""


# ----------------------------------------------------------------------
# #### Exercise 4: Interactive Challenge - Policy Drift Observation
# ----------------------------------------------------------------------

@tool
def search_tool(query: str) -> str:
    """Searches the web for relevant information."""
    return f"Search result: The current year is 2024. Information found for: {query}"
    
@tool
def calculator_tool(expression: str) -> str:
    """Performs simple mathematical calculations."""
    try:
        # Simple evaluation for demonstration
        result = eval(expression.replace('sqrt', 'math.sqrt').replace('^', '**'))
        return str(result)
    except:
        return "Error calculating expression."

def setup_research_agent(model_temp: float, policy_tag: str):
    """
    Sets up a research agent with different policy prompts and temperature settings.
    """
    tools = [search_tool, calculator_tool]
    
    llm_modified = ChatOpenAI(temperature=model_temp, model=MODEL,
                              base_url=BASE_URL, api_key=OPENAI_COMPATIBLE_API_KEY)
    
    # Policy definition in the system prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"You are a meticulous research assistant operating under the '{policy_tag}' policy. Always prioritize using the 'search_tool' first, regardless of the simplicity of the query. Be detailed in your reasoning."),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad")
    ])
    
    if "Calculator First" in policy_tag:
        # Override prompt for Policy B
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"You are a fast research assistant operating under the '{policy_tag}' policy. If the query contains any mathematical operation, immediately use the 'calculator_tool' before searching. Be brief in your reasoning."),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad")
        ])
    
    agent = create_openai_tools_agent(llm_modified, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True,
        handle_parsing_errors=True
    )
    return agent_executor

# Define the common query
mixed_query = "What is the square root of 144 plus the current year?"

# Execute Policy A (Meticulous Search, Low Temp)
agent_A = setup_research_agent(model_temp=0.1, policy_tag="Policy A - Search First")
print("\n--- Running Exercise 4: Policy A (Search First, Low Temp) ---")
try:
    agent_A.invoke(
        {"input": mixed_query},
        config={"tags": ["policy-A", "comparison"], "project_name": "Agent-Policy-Drift"}
    )
except Exception as e:
    print(f"Policy A run completed with potential error (check trace): {e}")


# Execute Policy B (Fast Calculation, High Temp)
agent_B = setup_research_agent(model_temp=0.9, policy_tag="Policy B - Calculator First")
print("\n--- Running Exercise 4: Policy B (Calculator First, High Temp) ---")
try:
    agent_B.invoke(
        {"input": mixed_query},
        config={"tags": ["policy-B", "comparison"], "project_name": "Agent-Policy-Drift"}
    )
except Exception as e:
    print(f"Policy B run completed with potential error (check trace): {e}")


# --- Analysis for Exercise 4: Interactive Challenge - Policy Drift Observation ---
"""
**Trace Comparison Analysis (Agent-Policy-Drift Project):**

| Feature | Policy A (Low Temp, Search First) | Policy B (High Temp, Calculator First) |
| :--- | :--- | :--- |
| **Execution Path (Sequence of Spans)** | Agent -> LLM Thought (Detailed) -> `search_tool` -> LLM Thought (Detailed) -> `calculator_tool` -> Final Answer. | Agent -> LLM Thought (Brief) -> `calculator_tool` -> LLM Thought (Brief) -> `search_tool` -> Final Answer. |
| **Depth/Steps** | Deeper (Likely 5-7 spans), as the agent follows the explicit instruction to search first, requiring an extra step to find the current year. | Shallower (Likely 4-6 spans), as the agent immediately handles the calculation part. |
| **Tool Execution Order** | `search_tool` executes first. | `calculator_tool` executes first. |
| **Temperature Manifestation (Agent Thought Spans)** | Thoughts are highly deterministic, logical, and verbose, strictly adhering to the system prompt's priority. | Thoughts are non-deterministic, potentially shorter, and prioritize speed, leading to immediate tool use based on pattern matching (math operation). |

This comparison highlights that the combination of prompt engineering (policy) and temperature (non-determinism) fundamentally changes the agent's internal reasoning process, which is only observable and quantifiable through detailed traces.
"""

# ----------------------------------------------------------------------
# #### Exercise 5: Creating Evaluation Datasets from Successful Runs
# ----------------------------------------------------------------------

def create_dataset_from_successful_runs(project_name: str, dataset_name: str, required_tags: List[str]):
    """
    Fetches successful runs from a project and converts them into a LangSmith dataset.
    """
    print(f"\n--- Running Exercise 5: Creating Dataset from Runs in {project_name} ---")
    
    # Construct filter string to find completed agent runs with required tags
    tag_filters = [f'any(tags, "{tag}")' for tag in required_tags]
    filter_str = f'and(eq(status, "completed"), {"and".join(tag_filters)})'
    
    # 1. Fetch successful runs. On a fresh account the project may not exist at
    # all, and `list_runs` raises rather than returning an empty list.
    try:
        successful_runs = list(client.list_runs(
            project_name=project_name,
            run_type="agent",  # Filter for root agent runs
            filter=filter_str
        ))
    except Exception as exc:
        print(f"Project '{project_name}' has no runs yet ({exc}). "
              f"Run Exercise 4 first, then retry.")
        return
    
    if not successful_runs:
        print(f"No completed runs found in project '{project_name}' with tags {required_tags}. Please ensure Exercise 4 runs completed successfully.")
        return

    # 2. Create the new dataset
    try:
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description="Gold standard examples derived from successful operational traces of the Research Agent."
        )
        print(f"Created Dataset: {dataset.id} - {dataset.name}")
    except Exception:
        # Attempt to read existing dataset if creation fails (e.g., already exists)
        dataset = client.read_dataset(dataset_name=dataset_name)
        print(f"Using existing Dataset: {dataset.id} - {dataset.name}")


    # 3. Iterate and add examples
    examples_added = 0
    for run in successful_runs:
        # Ensure run data integrity
        if run.inputs and run.outputs and 'input' in run.inputs and run.outputs:
            
            input_data = run.inputs['input']
            output_data = run.outputs
            
            # Extract the final output string from the agent's output dictionary
            final_answer = output_data.get('output', str(output_data))
            
            client.create_example(
                dataset_id=dataset.id,
                inputs={"question": input_data},
                outputs={"answer": final_answer}
            )
            examples_added += 1
            
    print(f"Successfully added {examples_added} examples to dataset '{dataset_name}'.")

# Example invocation for Exercise 5:
create_dataset_from_successful_runs(
    project_name="Agent-Policy-Drift", 
    dataset_name="Research-Agent-Gold-Standard-V1",
    required_tags=["policy-A"] # Only capture runs adhering to Policy A
)
