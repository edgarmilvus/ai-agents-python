import os
from crewai import Agent, Task, Crew, Process, LLM


# Common LLM configuration for all agents
BASE_URL = os.environ.get("OPENAI_COMPATIBLE_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("OPENAI_COMPATIBLE_MODEL", "~deepseek/deepseek-flash-latest")
llm = LLM(model=f"openai/{MODEL}", base_url=BASE_URL, api_key=os.environ.get("OPENAI_COMPATIBLE_API_KEY"))

def run_exercise_1():
    print("\n--- Running Exercise 1: Sequential Content Writer Crew ---")

    # 1. Agent Definitions
    researcher = Agent(
        role='Senior Technical Researcher',
        goal='Gather exhaustive, accurate facts about Python context managers and asyncio.',
        backstory="Meticulous and detail-oriented, produces dry, factual reports.",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    writer = Agent(
        role='Technical Content Strategist',
        goal='Transform raw research data into an engaging, clear article introduction.',
        backstory="Highly creative, focuses on readability and tone.",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    # 2. Task Structure
    research_task = Task(
        description="Gather all necessary technical facts, code snippets, and explanations for a 500-word introduction on 'Pythonic Context Managers and their use in asyncio'.",
        agent=researcher,
        expected_output="A detailed, factual report suitable as a source document."
    )

    # Task 2 uses the output of Task 1 as context
    writing_task = Task(
        description=(
            "Using the research context provided, write a 500-word engaging article introduction. "
            "Focus on clarity, tone, and structuring the information for a professional audience. "
            "DO NOT perform new research; strictly use the provided context."
        ),
        agent=writer,
        context=[research_task], # Critical context passing
        expected_output="The final, polished 500-word article introduction."
    )

    # 3. Crew Execution
    content_crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        process=Process.sequential,
        verbose=True
    )

    result = content_crew.kickoff()
    print("\n[EXERCISE 1 RESULT] Final Article Introduction:\n", result)

# Note: The actual execution of this function is deferred to the main block.
