import os
from crewai import Agent, Task, Crew, Process, LLM

# The endpoint, model and key come from the environment.
BASE_URL = os.environ.get("OPENAI_COMPATIBLE_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("OPENAI_COMPATIBLE_MODEL", "~deepseek/deepseek-flash-latest")
llm = LLM(model=f"openai/{MODEL}", base_url=BASE_URL, api_key=os.environ.get("OPENAI_COMPATIBLE_API_KEY"))


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

    # 2. Task Structure (New Flow: Content -> Validation -> Scheduling)
    content_task = Task(
        description="Generate 3 short social media posts promoting a new B2B software product. Use a casual, slang-heavy tone and excessive emojis (e.g., 'OMG! This software is fire 🔥🔥🔥').",
        agent=creator,
        expected_output="3 draft social media posts."
    )

    # The Validation Gate
    validation_task = Task(
        description=(
            "Review the provided social media content. If the tone is unprofessional, too casual, or uses excessive slang/emojis (failing corporate guidelines), rewrite the posts to be strictly professional, concise, and compliant. "
            "Your output must be the final, approved version of the 3 posts."
        ),
        agent=validator,
        context=[content_task], # Takes draft content
        expected_output="The 3 final, professionally compliant social media posts."
    )

    # The Scheduler uses the VALIDATED content
    scheduling_task = Task(
        description=(
            "Using the final, validated content provided in the context, create a deployment schedule (e.g., Post 1 on Monday 9am EST, Post 2 on Tuesday 1pm EST, etc.)."
        ),
        agent=scheduler,
        context=[validation_task], # Takes validated content
        expected_output="A complete, date-and-time specific deployment schedule."
    )

    # 3. Crew Execution (Enforcing the sequential order with the new gate)
    validation_crew = Crew(
        agents=[creator, validator, scheduler],
        tasks=[content_task, validation_task, scheduling_task], 
        process=Process.sequential,
        verbose=True
    )

    result = validation_crew.kickoff()
    print("\n[EXERCISE 4 RESULT] Final Deployment Schedule and Validated Content:\n", result)

# --- Main Execution Block ---

if __name__ == "__main__":
    # This file defines exercise 4 only: the other three belong to their own
    # listings, and calling them here was a copy of the combined template.
    if not os.getenv("OPENAI_COMPATIBLE_API_KEY"):
        print("ERROR: Please set the OPENAI_COMPATIBLE_API_KEY environment variable.")
    else:
        run_exercise_4()
