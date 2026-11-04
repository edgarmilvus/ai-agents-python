import os
from pydantic import BaseModel
from crewai import Agent, Task, Crew, Process, LLM

# --- Configuration Setup ---
# Common LLM configuration for all agents
BASE_URL = os.environ.get("OPENAI_COMPATIBLE_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("OPENAI_COMPATIBLE_MODEL", "~deepseek/deepseek-flash-latest")
llm = LLM(model=f"openai/{MODEL}", base_url=BASE_URL, api_key=os.environ.get("OPENAI_COMPATIBLE_API_KEY"))

# --- EXERCISE 1: Sequential Content Writer Crew ---

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

    writing_task = Task(
        description=(
            "Using the research context provided, write a 500-word engaging article introduction. "
            "Focus on clarity, tone, and structuring the information for a professional audience. "
            "DO NOT perform new research; strictly use the provided context."
        ),
        agent=writer,
        context=[research_task],
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


# --- EXERCISE 2: Financial Analysis Crew (Delegation & Structured Output) ---

def run_exercise_2():
    print("\n--- Running Exercise 2: Financial Analysis Crew (Delegation & Structured Output) ---")

    # 1. Agent Definitions
    data_analyst = Agent(
        role='Quantitative Financial Analyst',
        goal='Analyze performance metrics and determine a preliminary numerical risk score.',
        backstory="Highly mathematical, focused on charts and statistics.",
        llm=llm,
        verbose=True,
        allow_delegation=True  # Must allow delegation for internal task handling
    )

    risk_assessor = Agent(
        role='Market Sentiment and Regulatory Expert',
        goal='Assess non-numerical risks, such as regulatory changes and market sentiment.',
        backstory="Focuses on narrative and external factors, providing context to the numbers.",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    # Define the required JSON structure
    # `output_json` takes a Pydantic model, not a map of field names to type
    # names: given a dict, CrewAI builds an empty model and rejects every field
    # the crew returns as "extra".
    class RiskAnalysis(BaseModel):
        company: str
        risk_score_1_to_10: int
        justification_quantitative: str
        justification_qualitative: str

    # 2. Task Structure (Delegation is handled implicitly via the prompt and allow_delegation=True)
    analysis_task = Task(
        description=(
            "Perform a comprehensive risk analysis for Tesla (TSLA). "
            "First, calculate an initial risk score based on general financial health. "
            "Crucially, delegate a sub-task to the Risk Assessor Agent to obtain qualitative market sentiment and regulatory risks. "
            "Finally, synthesize both quantitative and qualitative inputs into a unified risk assessment."
        ),
        agent=data_analyst,
        expected_output="A JSON object with exactly these keys: company, risk_score_1_to_10, justification_quantitative, justification_qualitative.",
        output_json=RiskAnalysis,  # Enforce structured output
        output_file="tesla_risk_report.json"
    )

    # The risk assessor is not explicitly assigned a task in the crew list, but is available for delegation.
    # The crew setup requires all agents to be listed.
    financial_crew = Crew(
        agents=[data_analyst, risk_assessor],
        tasks=[analysis_task],
        process=Process.sequential,
        verbose=True
    )

    result = financial_crew.kickoff()
    print("\n[EXERCISE 2 RESULT] Final Structured Risk Report (JSON):\n", result)


# --- EXERCISE 3: Global Product Launch Crew (Hierarchical Process) ---

def run_exercise_3():
    print("\n--- Running Exercise 3: Global Product Launch Crew (Hierarchical Process) ---")

    # 1. Agent Definitions
    manager = Agent(
        role='Chief Strategy Officer (CSO)',
        goal='Oversee the global launch strategy, resolve conflicts, and ensure compliance and market fit.',
        backstory="Experienced executive balancing risk and reward, focused on cohesive strategy.",
        llm=llm,
        verbose=True,
        allow_delegation=False  # Manager does not delegate, they coordinate
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

    # 2. Task Structure (Manager coordinates these)
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

    synthesis_task = Task(
        description=(
            "Synthesize the initial marketing strategy and the legal compliance review. "
            "Create the final, approved, compliant, and market-ready global launch strategy summary. "
            "This summary must explicitly resolve any conflicts identified by the Legal Agent."
        ),
        agent=manager, # The manager executes the final synthesis task
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
        manager_agent=manager,
        verbose=True
    )

    result = launch_crew.kickoff()
    print("\n[EXERCISE 3 RESULT] Final Global Launch Strategy:\n", result)


# --- EXERCISE 4: Interactive Challenge (Validation Gate) ---
# Assuming a prior content creation setup exists (simplified here for demonstration)

def run_exercise_4():
    print("\n--- Running Exercise 4: Interactive Challenge (Validation Gate) ---")

    # Existing Agents (Simplified)
    creator = Agent(
        role='Social Media Content Creator',
        goal='Generate engaging social media posts.',
        backstory="Loves using slang and emojis to connect with younger audiences.",
        llm=llm,
        verbose=True
    )
    scheduler = Agent(
        role='Deployment Scheduler',
        goal='Finalize the deployment plan based on approved content.',
        backstory="Focused on timing and logistical efficiency.",
        llm=llm,
        verbose=True
    )

    # 1. New Agent Definition
    validator = Agent(
        role='Corporate Brand Compliance Officer',
        goal='Review content for strict adherence to corporate tone, style, and messaging guidelines.',
        backstory="Highly protective of the brand image; demands professionalism.",
        llm=llm,
        verbose=True
    )

    # 2. Task Structure (New Flow: B -> D -> C)
    content_task = Task(
        description="Generate 3 short social media posts promoting a new B2B software product. Use a casual, slang-heavy tone and excessive emojis to test the validator.",
        agent=creator,
        expected_output="3 draft social media posts."
    )

    validation_task = Task(
        description=(
            "Review the provided social media content. If the tone is unprofessional, too casual, or uses excessive slang/emojis (failing corporate guidelines), rewrite the posts to be strictly professional, concise, and compliant. "
            "Your output must be the final, approved version of the 3 posts."
        ),
        agent=validator,
        context=[content_task],
        expected_output="The 3 final, professionally compliant social media posts."
    )

    scheduling_task = Task(
        description=(
            "Using the final, validated content provided in the context, create a deployment schedule (e.g., Post 1 on Monday 9am EST, Post 2 on Tuesday 1pm EST, etc.)."
        ),
        agent=scheduler,
        context=[validation_task],
        expected_output="A complete, date-and-time specific deployment schedule."
    )

    # 3. Crew Execution (New sequential order)
    validation_crew = Crew(
        agents=[creator, validator, scheduler],
        tasks=[content_task, validation_task, scheduling_task], # Enforcing the B -> D -> C order
        process=Process.sequential,
        verbose=True
    )

    result = validation_crew.kickoff()
    print("\n[EXERCISE 4 RESULT] Final Deployment Schedule and Validated Content:\n", result)


if __name__ == "__main__":
    # Check for API key existence before running
    if not os.getenv("OPENAI_COMPATIBLE_API_KEY"):
        print("ERROR: Please set the OPENAI_COMPATIBLE_API_KEY environment variable.")
    else:
        run_exercise_1()
        run_exercise_2()
        run_exercise_3()
        run_exercise_4()
