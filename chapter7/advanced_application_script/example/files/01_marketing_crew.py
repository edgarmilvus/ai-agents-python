import os
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool

# --- 1. Environment and Tool Setup ---

BASE_URL = os.environ.get("OPENAI_COMPATIBLE_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("OPENAI_COMPATIBLE_MODEL", "~deepseek/deepseek-flash-latest")
llm = LLM(model=f"openai/{MODEL}", base_url=BASE_URL, api_key=os.environ.get("OPENAI_COMPATIBLE_API_KEY"))

# Initialize the search tool. The example ships a local corpus so the crew runs
# without a second provider; Serper or Tavily would replace this class wholesale.
class MarketSearchTool(BaseTool):
    name: str = "web_search"
    description: str = "Searches a curated corpus of market notes. Input: the topic to look up."

    def _run(self, query: str) -> str:
        return (
            f"Corpus results for '{query}':\n"
            "- Generative AI in medicine is moving from pilots to paid deployments.\n"
            "- Buyers cite evidence generation and data privacy as the two gating concerns.\n"
            "- Three platform vendors account for most reported revenue.\n"
        )

search_tool = MarketSearchTool()
    
# Define the core input topic for the entire project
PROJECT_TOPIC = "The rise of personalized medicine powered by generative AI and large language models."

# --- 2. Defining Specialized Agents (Role-Playing) ---

# Agent 1: The Researcher (Fact Gatherer)
research_analyst = Agent(
    role='Senior AI Trend Research Analyst',
    goal=f'Conduct comprehensive, up-to-date research on {PROJECT_TOPIC} and synthesize key findings.',
    backstory=(
        "You are a meticulous analyst working for a specialized tech marketing firm. "
        "Your expertise lies in quickly identifying emerging technologies, validating their market impact, "
        "and distilling complex technical white papers into digestible, strategic summaries. "
        "You always focus on the 'why it matters' for a non-technical audience."
    ),
    tools=[search_tool],
    verbose=True,
    allow_delegation=False, # Must complete the research independently
    llm=llm
)

# Agent 2: The Strategist (Creative Translator)
content_strategist = Agent(
    role='Social Media Content Strategist',
    goal='Translate complex research findings into three compelling, platform-specific social media campaign hooks.',
    backstory=(
        "You are a creative mastermind specializing in translating deep tech trends into viral content. "
        "You understand platform dynamics (Twitter, LinkedIn, Instagram) and know exactly how to frame "
        "a scientific finding as an engaging story or a provocative question. Your output must be actionable."
    ),
    verbose=True,
    allow_delegation=False, # Focus on creative synthesis based on provided facts
    llm=llm
)

# Agent 3: The Executive (Reviewer and Planner)
marketing_executive = Agent(
    role='Chief Marketing Officer (CMO) and Strategy Reviewer',
    goal='Review the content strategy and formulate a final, actionable deployment plan with target KPIs.',
    backstory=(
        "You are the CMO, responsible for budget and final execution. You review strategies for business "
        "viability, alignment with client goals, and measurable success metrics (KPIs). "
        "Your final output is the go/no-go decision and the deployment framework."
    ),
    verbose=True,
    allow_delegation=True, # Can delegate back to the researcher if facts are missing
    llm=llm
)

# --- 3. Defining Tasks and Sequential Delegation Flow ---

# Task 1: Research and Summary (Output feeds Agent 2)
research_task = Task(
    description=f"Using the search tool, find the top 5 recent developments (last 12 months) related to {PROJECT_TOPIC}. "
                "Summarize these findings into a concise 500-word report, highlighting the most disruptive aspect "
                "that would appeal to technology investors and healthcare professionals.",
    expected_output="A 500-word structured report detailing 5 key trends in AI personalized medicine.",
    agent=research_analyst
)

# Task 2: Strategy Generation (Input from Task 1, Output feeds Agent 3)
strategy_task = Task(
    description="Based *only* on the research report provided by the Research Analyst, "
                "generate three distinct social media hooks (one for LinkedIn, one for Twitter, one for Instagram). "
                "Each hook must include a suggested visual concept and a clear call-to-action (CTA).",
    expected_output="A structured list of 3 social media hooks (LinkedIn, Twitter, Instagram), including CTA and visual concepts.",
    agent=content_strategist,
    context=[research_task] # CRITICAL: Passes the output of Task 1 to Task 2
)

# Task 3: Final Review and Deployment Plan (Input from Task 2)
review_task = Task(
    description="Review the three proposed social media hooks. Evaluate their market suitability and assign a "
                "specific Key Performance Indicator (KPI) to each platform (e.g., LinkedIn: '15% CTR', Twitter: '500 impressions'). "
                "Produce a final Campaign Deployment Plan document.",
    expected_output="A final 'Campaign Deployment Plan' document detailing the reviewed strategy, platform-specific KPIs, and a launch timeline recommendation.",
    agent=marketing_executive,
    context=[strategy_task] # CRITICAL: Passes the output of Task 2 to Task 3
)

# --- 4. Forming and Running the Crew ---

# Define the crew using the sequential process model
project_crew = Crew(
    agents=[research_analyst, content_strategist, marketing_executive],
    tasks=[research_task, strategy_task, review_task],
    process=Process.sequential, # Tasks run strictly one after the other
    verbose=True # Verbosity level 2 shows the internal reasoning of the agents
)

print("--- Starting Collaborative Marketing Strategy Crew ---")
print(f"Project Topic: {PROJECT_TOPIC}\n")

# Execute the workflow and capture the final output
campaign_result = project_crew.kickoff()

# Output the final result
print("\n=======================================================")
print("              FINAL CAMPAIGN DEPLOYMENT PLAN           ")
print("=======================================================")
print(campaign_result)
