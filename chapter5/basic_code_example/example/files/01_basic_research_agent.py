# basic_research_agent.py

import os
from crewai import Agent, Task, Crew, LLM

# 1. Configuration and Environment Setup
# The endpoint, model and key come from the environment; nothing about the
# provider is hard-coded, so the same crew runs against any compatible gateway.
BASE_URL = os.environ.get("OPENAI_COMPATIBLE_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("OPENAI_COMPATIBLE_MODEL", "~deepseek/deepseek-flash-latest")

# CRITICAL: Check for the required API key
if not os.getenv("OPENAI_COMPATIBLE_API_KEY"):
    # In a production environment, this check prevents runtime errors later
    raise EnvironmentError(
        "OPENAI_COMPATIBLE_API_KEY environment variable not set. "
        "Please export it before running the crew."
    )

# CrewAI's LLM wraps an OpenAI-compatible endpoint; the openai/ prefix selects
# that provider while base_url points it at the gateway.
llm = LLM(
    model=f"openai/{MODEL}",
    base_url=BASE_URL,
    api_key=os.environ.get("OPENAI_COMPATIBLE_API_KEY"),
)

# --- Agent Definition: Defining Persona and Expertise ---

# 2. Define the Agent's Core Identity
research_analyst_agent = Agent(
    # The 'role' defines the persona and expertise, influencing tone and knowledge base.
    role='Senior Market Research Analyst',
    
    # The 'goal' is the agent's long-term objective, guiding its overall decision-making.
    goal='Synthesize complex technological trends into concise, actionable summaries for executive briefing.',
    
    # The 'backstory' provides detailed context, acting as a sophisticated system prompt injection.
    backstory=(
        "You are a meticulous analyst with 15 years of experience specializing "
        "in emerging cloud technologies. Your specialty is distilling vast amounts "
        "of information into precise, structured reports, adhering strictly to the DRY principle."
    ),
    
    # Setting verbose=True allows us to see the agent's internal thought process (Tool usage, reasoning).
    verbose=True, 
    
    # Since this is a single agent, delegation is disabled to maintain focus.
    allow_delegation=False,

    # The reasoning engine configured above
    llm=llm
)

# --- Task Definition: Defining Action and Output Structure ---

# 3. Define the Specific Task and Desired Output
research_task = Task(
    # The 'description' is the specific instruction for the current job.
    description=(
        "Analyze the current state and future trajectory of 'Serverless Computing'. "
        "Focus specifically on the shift from traditional Virtual Machines (VMs) to Function-as-a-Service (FaaS) models."
    ),
    
    # The 'expected_output' is a crucial prompt engineering step, ensuring structure and quality.
    expected_output="A structured, three-paragraph executive summary report formatted in Markdown. "
                    "Paragraph 1: Definition and Current Market Adoption. "
                    "Paragraph 2: Key Benefits (Cost efficiency and scaling potential). "
                    "Paragraph 3: Future Challenges and Predictions (Focus on vendor lock-in risk).",
    
    # Assign the task to the defined agent
    agent=research_analyst_agent 
)

# --- Execution Orchestration ---

# 4. Initialize the Crew
# The Crew class is the orchestrator, managing agents and tasks.
single_agent_crew = Crew(
    agents=[research_analyst_agent], # List of agents involved
    tasks=[research_task],           # List of tasks to be executed
    verbose=True                        # Higher verbosity for detailed execution logs and crew status
)

# 5. Run the Execution
print("\n" + "="*50)
print("--- Starting Single Agent Research Execution ---")
print("="*50 + "\n")

# The kickoff() method starts the sequential processing of the tasks.
result = single_agent_crew.kickoff()

# 6. Output Result
print("\n\n" + "#"*50)
print("        FINAL RESEARCH SUMMARY REPORT")
print("#"*50 + "\n")
print(result)
