import os
from pydantic import BaseModel
from crewai import Agent, Task, Crew, Process, LLM

# The endpoint, model and key come from the environment.
BASE_URL = os.environ.get("OPENAI_COMPATIBLE_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("OPENAI_COMPATIBLE_MODEL", "~deepseek/deepseek-flash-latest")
llm = LLM(model=f"openai/{MODEL}", base_url=BASE_URL, api_key=os.environ.get("OPENAI_COMPATIBLE_API_KEY"))


def run_exercise_2():
    print("\n--- Running Exercise 2: Financial Analysis Crew (Delegation & Structured Output) ---")

    # 1. Agent Definitions
    data_analyst = Agent(
        role='Quantitative Financial Analyst',
        goal='Analyze performance metrics and determine a preliminary numerical risk score.',
        backstory="Highly mathematical, focused on charts and statistics.",
        llm=llm,
        verbose=True,
        allow_delegation=True  # Essential for delegating the sub-task
    )

    risk_assessor = Agent(
        role='Market Sentiment and Regulatory Expert',
        goal='Assess non-numerical risks, such as regulatory changes and market sentiment.',
        backstory="Focuses on narrative and external factors, providing context to the numbers.",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    # Define the required JSON structure. `output_json` takes a Pydantic model:
    # given a dict of names to type names, CrewAI builds an empty model and
    # rejects every field the crew returns.
    class RiskAnalysis(BaseModel):
        company: str
        risk_score_1_to_10: int
        justification_quantitative: str
        justification_qualitative: str

    # 2. Task Structure (Delegation is handled implicitly via the prompt)
    analysis_task = Task(
        description=(
            "Perform a comprehensive risk analysis for Tesla (TSLA). "
            "First, calculate an initial risk score based on general financial health. "
            "Crucially, delegate a sub-task to the Risk Assessor Agent to obtain qualitative market sentiment and regulatory risks. "
            "Finally, synthesize both quantitative and qualitative inputs into a unified risk assessment and output the result in the required JSON format."
        ),
        agent=data_analyst,
        expected_output="A final, unified risk assessment report in JSON format.",
        output_json=RiskAnalysis,  # Enforce structured output
        output_file="tesla_risk_report.json"
    )

    # 3. Crew Execution
    financial_crew = Crew(
        agents=[data_analyst, risk_assessor],
        tasks=[analysis_task],
        process=Process.sequential, # Delegation occurs within the single task execution
        verbose=True
    )

    result = financial_crew.kickoff()
    print("\n[EXERCISE 2 RESULT] Final Structured Risk Report (JSON):\n", result)
