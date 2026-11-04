import os
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool

# --- Configuration and Setup ---
# The endpoint, model and key come from the environment.
BASE_URL = os.environ.get("OPENAI_COMPATIBLE_BASE_URL", "https://openrouter.ai/api/v1")
MODEL_NAME = os.environ.get("OPENAI_COMPATIBLE_MODEL", "~deepseek/deepseek-flash-latest")

if not os.getenv("OPENAI_COMPATIBLE_API_KEY"):
    raise EnvironmentError("OPENAI_COMPATIBLE_API_KEY is not set.")

llm = LLM(
    model=f"openai/{MODEL_NAME}",
    base_url=BASE_URL,
    api_key=os.environ.get("OPENAI_COMPATIBLE_API_KEY"),
)

# Initialize the research tool. A production crew would call a search API here
# (Serper, Tavily); the local corpus keeps the example runnable without a second
# provider, and the tool contract is the same.
class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = (
        "Searches a curated corpus of public material about a product. "
        "Input: the product and the aspect to research."
    )

    def _run(self, query: str) -> str:
        lowered = query.lower()
        if "pricing" in lowered or "tier" in lowered:
            return ("AuraFlow sells three tiers: Starter $29/user/month, Growth $79, "
                    "Enterprise custom. Annual billing gives two months free; a 14-day trial "
                    "is offered. Pricing sits below the two incumbents.")
        if "marketing" in lowered or "messaging" in lowered:
            return ("AuraFlow markets itself as 'the CRM that thinks ahead'. The tone is "
                    "confident and technical; the main channels are LinkedIn, developer "
                    "webinars and partner integrations.")
        return "No specific corpus entry; the material is thin on this aspect."

research_tool = WebSearchTool()

# --- 1. Agent Definitions (Roles and Specialization) ---

# The Strategy Manager Agent: Handles planning, delegation, and final synthesis.
strategy_manager = Agent(
    role='Strategy Manager',
    goal='Decompose the competitive analysis task, manage worker output, and synthesize a unified strategic report.',
    backstory=(
        "You are the Lead Strategist, responsible for high-level planning and final deliverable quality. "
        "You do not perform primary research; you coordinate specialized teams."
    ),
    verbose=True,
    allow_delegation=True, # Critical for the Manager role
    llm=llm
)

# Worker Agent 1: Specializes in pricing and financial models.
pricing_worker = Agent(
    role='Pricing Analyst',
    goal='Analyze the competitor\'s pricing structure, discounts, and subscription tiers.',
    backstory="Expert in market pricing dynamics and financial modeling.",
    tools=[research_tool],
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# Worker Agent 2: Specializes in marketing messaging and public perception.
marketing_worker = Agent(
    role='Marketing Specialist',
    goal='Analyze the competitor\'s messaging tone, target audience, and key marketing channels.',
    backstory="A seasoned digital marketing expert focusing on sentiment and communication strategy.",
    tools=[research_tool],
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# --- 2. Task Definitions (Decomposition) ---

COMPETITOR_PRODUCT = "New AI-powered CRM software called 'AuraFlow'"
ANALYSIS_GOAL = f"Perform a detailed competitive analysis on {COMPETITOR_PRODUCT}."

# Task 1: Pricing Research (Assigned to Worker 1)
pricing_task = Task(
    description=f"Conduct deep research on the pricing of {COMPETITOR_PRODUCT}. Include tiered structures, introductory offers, and comparison to industry benchmarks.",
    expected_output="A concise, bulleted report on pricing strategy and financial viability.",
    agent=pricing_worker
)

# Task 2: Marketing Research (Assigned to Worker 2)
marketing_task = Task(
    description=f"Analyze the public marketing materials for {COMPETITOR_PRODUCT}. Identify the core value proposition, emotional tone, and primary distribution channels used.",
    expected_output="A detailed summary covering messaging, target demographic, and promotional effectiveness.",
    agent=marketing_worker
)

# Task 3: Synthesis and Final Report (Assigned to Manager)
# NOTE: This task implicitly waits for the completion of the worker tasks.
synthesis_task = Task(
    description=(
        f"Using the reports from the Pricing Analyst and Marketing Specialist, synthesize a unified 500-word strategic brief. "
        f"The brief must clearly state the threat level of {COMPETITOR_PRODUCT} and recommend two immediate counter-strategies (one pricing, one marketing)."
    ),
    expected_output="A final, polished strategic brief ready for executive review.",
    agent=strategy_manager,
    context=[pricing_task, marketing_task] # Explicit dependency on worker outputs
)

# --- 3. Crew Setup and Execution (Manager-Worker Hierarchy) ---

# Define the crew with the Manager, Workers, and Tasks.
# Crucially, we use Process.hierarchical to enforce the Manager-Worker pattern.
competitive_crew = Crew(
    # The manager is named by `manager_agent`, not listed among the agents:
    # CrewAI 1.x rejects a crew that lists its own manager.
    agents=[pricing_worker, marketing_worker],
    tasks=[pricing_task, marketing_task, synthesis_task],
    process=Process.hierarchical, # Enforces Manager-Worker structure
    manager_agent=strategy_manager, # Explicitly defines the top-level orchestrator
    verbose=True
)

# Execute the workflow
print("--- Starting Competitive Analysis MAS Workflow ---")
result = competitive_crew.kickoff()
print("\n\n--- Final Strategic Brief ---")
print(result)
