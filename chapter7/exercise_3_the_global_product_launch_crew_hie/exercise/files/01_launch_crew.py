import os
from crewai import Agent, Task, Crew, Process, LLM

# The endpoint, model and key come from the environment.
BASE_URL = os.environ.get("OPENAI_COMPATIBLE_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("OPENAI_COMPATIBLE_MODEL", "~deepseek/deepseek-flash-latest")
llm = LLM(model=f"openai/{MODEL}", base_url=BASE_URL, api_key=os.environ.get("OPENAI_COMPATIBLE_API_KEY"))


def run_exercise_3():
    print("\n--- Running Exercise 3: Global Product Launch Crew (Hierarchical Process) ---")

    # 1. Agent Definitions
    manager = Agent(
        role='Chief Strategy Officer (CSO)',
        goal='Oversee the global launch strategy, resolve conflicts, and ensure compliance and market fit.',
        backstory="Experienced executive balancing risk and reward, focused on cohesive strategy.",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    marketing = Agent(
        role='Global Marketing Strategist',
        goal='Develop aggressive, persuasive marketing copy and target demographics for a new software product.',
        backstory="Creative, driven by sales metrics, often uses aggressive claims.",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    legal = Agent(
        role='International Compliance Officer',
        goal='Vet all marketing claims for strict regulatory compliance in US and EU jurisdictions.',
        backstory="Cautious, focused solely on minimizing legal exposure.",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    # 2. Task Structure
    marketing_task = Task(
        description="Develop an aggressive marketing strategy and initial copy for the new software product, using strong claims like 'The fastest, most secure software ever built'.",
        agent=marketing,
        expected_output="Initial marketing strategy document and aggressive copy."
    )

    compliance_task = Task(
        description="Review the marketing strategy and copy provided in the context. Identify all regulatory risks (US/EU) and propose compliant modifications.",
        agent=legal,
        context=[marketing_task],
        expected_output="A compliance review report with mandatory revisions for the marketing copy."
    )

    # The Manager Agent executes the final synthesis task
    synthesis_task = Task(
        description=(
            "Synthesize the initial marketing strategy and the legal compliance review. "
            "Create the final, approved, compliant, and market-ready global launch strategy summary. "
            "This summary must explicitly resolve any conflicts identified by the Legal Agent, moderating aggressive claims."
        ),
        agent=manager,
        context=[compliance_task],
        expected_output="The final, cohesive, and compliant global launch strategy document."
    )

    # 3. Crew Configuration (Hierarchical)
    launch_crew = Crew(
        # The manager is named by `manager_agent`; CrewAI 1.x rejects a crew that
        # also lists it among the agents.
        agents=[marketing, legal],
        tasks=[marketing_task, compliance_task, synthesis_task],
        process=Process.hierarchical,
        manager_agent=manager, # Assign the designated manager
        verbose=True
    )

    result = launch_crew.kickoff()
    print("\n[EXERCISE 3 RESULT] Final Global Launch Strategy:\n", result)
