import os
from crewai import Agent, Task, Crew, Process, LLM
# The endpoint, model and key come from the environment; nothing about the
# provider is hard-coded.
BASE_URL = os.environ.get("OPENAI_COMPATIBLE_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("OPENAI_COMPATIBLE_MODEL", "~deepseek/deepseek-flash-latest")
llm = LLM(model=f"openai/{MODEL}", base_url=BASE_URL, api_key=os.environ.get("OPENAI_COMPATIBLE_API_KEY"))

# --- 1. Define Agents (The Specialized Roles) ---
# Agents are the core actors, defined by their expertise and personality.

# Agent 1: The Researcher
researcher = Agent(
    role='Senior Research Analyst',
    goal='Identify three compelling and little-known facts about the history of Python.',
    backstory=(
        "You are a meticulous, detail-oriented analyst specializing in technology history. "
        "Your primary function is to provide accurate, verified information, free of embellishment. "
        "You always output numbered lists."
    ),
    verbose=True, # Logs the agent's internal monologue (useful for debugging)
    allow_delegation=False, # This agent must complete its own task
    llm=llm
)

# Agent 2: The Writer
writer = Agent(
    role='Creative Content Strategist',
    goal='Draft an engaging 4-sentence social media post based on the researched facts.',
    backstory=(
        "You are a master of concise, viral content. Your job is to take raw data "
        "and transform it into easily digestible, highly shareable material, including engaging hashtags."
    ),
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# --- 2. Define Tasks (The Workflow Steps) ---
# Tasks define the specific actions and expected outputs.

# Task 1: Research the core topic. Assigned to the Researcher.
research_task = Task(
    description=(
        "Conduct thorough research on the origin and initial design philosophy of the Python language. "
        "The final output must be three distinct, numbered, verified facts."
    ),
    expected_output="A list of three numbered, verified facts about Python's history, suitable for direct input into a prompt.",
    agent=researcher
)

# Task 2: Write the final content. Assigned to the Writer.
writing_task = Task(
    description=(
        "Using the facts provided in the context, craft a short, punchy social media post. "
        "The post must be under 100 words and include a call-to-action question and three relevant hashtags."
    ),
    expected_output="A single, cohesive social media post formatted for Twitter/X or LinkedIn.",
    agent=writer,
    context=[research_task] # CRITICAL: This links the workflow, injecting Task 1's output here
)

# --- 3. Form the Crew (The Management Structure) ---

# Initialize the Crew with the defined agents and tasks
project_crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.sequential, # Ensures Task 1 completes before Task 2 begins
    verbose=True # Logs the crew's execution flow and agent thoughts
)

# --- 4. Execute the Workflow ---

print("### Starting the Content Creation Crew ###")
# The kickoff method starts the execution process
result = project_crew.kickoff()

# --- 5. Display Final Output ---
print("\n\n########################################")
print("## CREW EXECUTION COMPLETED ##")
print("########################################")
print(f"\nFinal Social Media Post:\n{result}")
