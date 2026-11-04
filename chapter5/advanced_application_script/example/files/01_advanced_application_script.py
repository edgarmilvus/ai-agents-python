import os
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool

# ----------------------------------------------------------------------
# 1. Environment and Tool Configuration
# ----------------------------------------------------------------------
# The endpoint, model and key come from the environment.
BASE_URL = os.environ.get("OPENAI_COMPATIBLE_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("OPENAI_COMPATIBLE_MODEL", "~deepseek/deepseek-flash-latest")

# Check for necessary environment variables
if not os.getenv("OPENAI_COMPATIBLE_API_KEY"):
    raise ValueError("OPENAI_COMPATIBLE_API_KEY must be set in the environment.")

llm = LLM(
    model=f"openai/{MODEL}",
    base_url=BASE_URL,
    api_key=os.environ.get("OPENAI_COMPATIBLE_API_KEY"),
)

# Initialize the primary tool. A production agent would call a search API here
# (Tavily is the usual choice); the example keeps a local corpus so it can run
# without a second provider, and the tool contract is identical.
class MarketSearchTool(BaseTool):
    name: str = "market_search"
    description: str = (
        "Searches a curated corpus of market notes and recent announcements. "
        "Input: the technology or market to look up."
    )

    def _run(self, query: str) -> str:
        return (
            f"Corpus results for '{query}':\n"
            "- Adoption grew 32% year over year across the last four quarters.\n"
            "- Three platform vendors hold most of the market; two are investing in custom silicon.\n"
            "- The main barrier reported by buyers is vendor lock-in and data portability.\n"
            "- Analysts expect consolidation among tooling vendors within eighteen months."
        )

internet_search_tool = MarketSearchTool()

# ----------------------------------------------------------------------
# 2. Agent Definition (The Persona and Cognitive Core)
# ----------------------------------------------------------------------
# Define the single autonomous agent: Market Research Analyst
market_analyst_agent = Agent(
    role='Senior Market Research Analyst',
    goal='Produce a concise, structured executive brief on a specified emerging technology.',
    backstory=(
        "You are an expert analyst with a decade of experience in competitive intelligence. "
        "Your specialty is synthesizing vast amounts of real-time data into actionable, "
        "highly structured reports suitable for C-suite executives. You prioritize "
        "accuracy, brevity, and clear identification of key market players."
    ),
    tools=[internet_search_tool],
    verbose=True,  # Enables detailed logging of agent thought process
    allow_delegation=False, # Essential for single-agent architecture
    llm=llm
)

# ----------------------------------------------------------------------
# 3. Task Definition (The Mission and Output Specification)
# ----------------------------------------------------------------------
# Define the specific research query
research_topic = "Current trends and major innovations in personalized cancer vaccines"

# Define the task, emphasizing prompt engineering for structured output
research_task = Task(
    description=(
        f"Conduct a comprehensive internet search on the topic: '{research_topic}'. "
        "Synthesize the search results into a formal executive brief. "
        "The output MUST be in Markdown format and strictly adhere to the following structure: "
        "\n\n# Executive Brief: Personalized Cancer Vaccines"
        "\n\n## 1. Market Overview and Current State (Max 250 words)"
        "\n\n## 2. Key Technological Innovations (List 3-5 specific breakthroughs)"
        "\n\n## 3. Top 3 Companies/Research Groups (Identify leaders and summarize their approach)"
        "\n\n## 4. Market Challenges (Identify 2-3 major hurdles to widespread adoption)"
        "\n\n---\n\n"
        "Ensure all data is current (post-2022) and cite sources implicitly by referencing company names or specific research initiatives."
    ),
    expected_output="A single, complete Markdown file following the strict section structure provided.",
    agent=market_analyst_agent
)

# ----------------------------------------------------------------------
# 4. Crew Configuration and Execution
# ----------------------------------------------------------------------
# Initialize the Crew (the orchestration layer)
research_crew = Crew(
    agents=[market_analyst_agent],
    tasks=[research_task],
    process=Process.sequential, # Sequential process is standard for a single agent
    verbose=True, # Highest verbosity for debugging and observation
)

# Execute the research process
print("--- Starting the Autonomous Research Agent ---")
try:
    result = research_crew.kickoff()
    # kickoff() returns a CrewOutput object, not a string: convert once, then
    # print and write the same text.
    brief_text = str(result)

    # ------------------------------------------------------------------
    # 5. Output Handling
    # ------------------------------------------------------------------
    print("\n\n################################################")
    print("## Research Complete: Final Executive Brief ##")
    print("################################################\n")
    print(brief_text)

    # Optional: Save the output to a file
    with open("executive_brief.md", "w", encoding="utf-8") as f:
        f.write(brief_text)
    print("\n\nOutput saved to executive_brief.md")

except Exception as e:
    print(f"\nAn error occurred during execution: {e}")
