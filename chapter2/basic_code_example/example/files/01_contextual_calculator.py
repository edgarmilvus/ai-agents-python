import os

from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_classic.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

# --- 1. Define the External Tool (The Agent's Capability) ---
@tool
def calculate_square(number: int) -> int:
    """Calculates the square of an integer. Useful for math operations."""
    # The ReAct loop hands the tool the text after "Action Input:", so the value
    # arrives as a string; convert it before doing arithmetic.
    number = int(number)
    # This print statement shows us when the external function is genuinely executed.
    print(f"\n[TOOL CALLED] Calculating {number} squared...")
    return number * number

# --- 2. Setup Environment and LLM (The Agent's Brain) ---
# The client speaks the OpenAI wire format; the endpoint, model and key come
# from the environment, so the same listing runs against any compatible gateway.
BASE_URL = os.environ.get("OPENAI_COMPATIBLE_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("OPENAI_COMPATIBLE_MODEL", "~deepseek/deepseek-flash-latest")

try:
    # Temperature 0: the planner should reason, not improvise.
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

# --- 3. Define the Agent's Cognitive Components ---
tools = [calculate_square]

# Setup Memory (Short-Term Context)
# This component stores the conversational history between turns. The ReAct
# prompt below is a string template, so memory returns text, not messages.
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=False
)

# Define the System Prompt (The Agent's Persona and Instructions)
# create_react_agent requires a template with these slots: the tool list, the
# tool names, the scratchpad the loop appends to, the user input and the history.
system_template = """
You are a sophisticated Personal Assistant Agent.
Your primary goal is to assist the user by answering questions and performing calculations.
You must use your memory to recall past inputs and the 'calculate_square' tool
whenever a squaring operation is requested.

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

# --- 4. Create the Agent Prompt and Executor ---
# The Prompt combines the system instructions with the conversational history slot.
prompt = PromptTemplate.from_template(system_template)

# Create the core Agent using the ReAct framework (The Planning Engine)
# ReAct (Reasoning and Acting) is the mechanism that allows the agent to decide
# whether to use a tool or just respond.
agent = create_react_agent(llm, tools, prompt)

# Create the Executor (The Agent's Body/Execution Engine)
# This object manages the overall loop: input -> LLM -> tool call -> result -> LLM -> output.
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True, # CRITICAL: Displays the internal Reasoning (Thought/Action/Observation)
    handle_parsing_errors=True
)

# --- 5. Execution Sequence: Testing Memory and Tools ---
print("--- Agent Execution Start ---")

# Step A: Establish Context (Memory Test)
# The agent must store the number 12 in its memory buffer.
print("\n--- TEST A: Establishing Context ---")
prompt_a = "I have two favorite numbers: 12 and 7. Remember 12."
response_a = agent_executor.invoke({"input": prompt_a})
print(f"\n[User Prompt A]: {prompt_a}")
print(f"[Agent Response A]: {response_a['output']}")

# Step B: Tool Usage Test
# The agent must identify that squaring 7 requires the external tool.
print("\n--- TEST B: Direct Tool Usage ---")
prompt_b = "What is the square of 7?"
response_b = agent_executor.invoke({"input": prompt_b})
print(f"\n[User Prompt B]: {prompt_b}")
print(f"[Agent Response B]: {response_b['output']}")

# Step C: Combined Memory and Tool Test
# The agent must recall '12' from memory, then use the tool on it.
print("\n--- TEST C: Memory-Informed Tool Usage ---")
prompt_c = "Now, what is the square of the number I asked you to remember?"
response_c = agent_executor.invoke({"input": prompt_c})
print(f"\n[User Prompt C]: {prompt_c}")
print(f"[Agent Response C]: {response_c['output']}")

print("\n--- Agent Execution Complete ---")
