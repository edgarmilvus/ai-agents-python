import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence

# --- 1. Setup and Configuration ---
# The endpoint, model and key come from the environment, so the same chain runs
# against any OpenAI-compatible gateway.
BASE_URL = os.environ.get("OPENAI_COMPATIBLE_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("OPENAI_COMPATIBLE_MODEL", "~deepseek/deepseek-flash-latest")

# Initialize the LLM
# We use a lower temperature (closer to 0) to encourage deterministic,
# logical, and less creative reasoning, which is ideal for CoT.
try:
    llm = ChatOpenAI(
        temperature=0.1,
        model=MODEL,
        base_url=BASE_URL,
        api_key=os.environ.get("OPENAI_COMPATIBLE_API_KEY"),
    )
except Exception as e:
    print(f"Error initializing LLM. Ensure OPENAI_COMPATIBLE_API_KEY is set: {e}")
    raise SystemExit(1)

# --- 2. Define the Chain of Thought Prompt ---
# The template explicitly instructs the model to reason step-by-step.
COT_TEMPLATE = """
You are an expert scheduling and prioritization assistant. Your task is to analyze a list of conflicting tasks and produce an optimized schedule for the day, starting at 9:00 AM.

CRITICAL INSTRUCTION: Before providing the final schedule, you MUST first output your step-by-step reasoning process under the heading 'REASONING:'. This reasoning must detail how you handled time conflicts and priority levels.

INPUT TASKS:
{tasks}

REASONING:
"""

# Create the PromptTemplate object, defining the input variable 'tasks'
prompt = PromptTemplate(
    template=COT_TEMPLATE,
    input_variables=["tasks"]
)

# --- 3. Construct the Reasoning Chain (LCEL) ---
# Define the output parser to handle the raw string output
parser = StrOutputParser()

# Define the full runnable sequence: Prompt feeds to LLM, LLM output feeds to Parser
# This is the standard LCEL pipe structure (A | B | C)
cot_chain = prompt | llm | parser

# --- 4. Define the Complex Input ---
complex_tasks = """

1. Draft the Q3 financial report (High Priority, requires 3 hours, must be done before 3 PM).
2. Attend the mandatory team meeting (Fixed time: 10:00 AM - 11:00 AM).
3. Review John's code (Low Priority, requires 1 hour).
4. Lunch break (Mandatory, 12:00 PM - 1:00 PM).
"""

# --- 5. Execution and Output ---
print("--- Starting CoT Agent Execution ---")
print(f"Input Tasks:\n{complex_tasks}")

# Run the chain, passing the tasks dictionary as input
response = cot_chain.invoke({"tasks": complex_tasks})

# Print the result, which now includes the internal reasoning and the final schedule
print("\n" + "="*50)
print("[AGENT RESPONSE - INCLUDING CoT]")
print("="*50 + "\n")
print(response)

print("\n--- Execution Complete ---")
