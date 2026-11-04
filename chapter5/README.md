# Chapter 5 — Building Your First Single Agent: A Research Assistant

The chapter's code, one folder per section. Every folder holds the listing exactly
as it appears in the book, a harness that drives it and asserts what happened, and
an `output/` folder for what the harness produced.

| folder | listing | what it shows |
| --- | --- | --- |
| `basic_code_example/example/` | `01_basic_research_agent.py` | one CrewAI agent, one task, one crew |
| `advanced_application_script/example/` | `01_advanced_application_script.py` | a tool, a task contract and a Markdown brief on disk |
| `exercise_1_the_constrained_auditor_agent/exercise/` | `01_exercise_1_auditor_agent.py` | a role that forbids external access |
| `exercise_2_dynamic_goal_setting_and_structure/exercise/` | `02_exercise_2_dynamic_structured_agent.py` | a Pydantic report with a cutoff date |
| `exercise_3_persistent_research_logging_intera/exercise/` | `02_exercise_3_persistent_logging.py` | runs persisted to SQLite and read back |
| `exercise_4_the_custom_configuration_tool_agen/exercise/` | `02_exercise_4_custom_tool_agent.py` | a custom tool with an input schema |

## Run the chapter

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./chapter5/run_offline.sh
```

`run_offline.sh` runs the six harnesses and prints one line per harness; the log is
written to `chapter5/output/run_5.log`. Any harness that fails makes the suite
exit 1. The two CrewAI listings are driven through a scripted CrewAI model, so no
key and no network are needed.

## The model and the tool

- The crew's LLM is `crewai.LLM(model="openai/<model>", base_url=..., api_key=...)`,
  configured from `OPENAI_COMPATIBLE_*`; the `openai/` prefix selects the provider.
- The harness substitutes `crewai.LLM` with a `BaseLLM` subclass, so `kickoff()`
  still runs through CrewAI's orchestration.
- The advanced example's search is a local `BaseTool` over a curated corpus. A
  production agent would call Tavily, which needs a second provider key and the
  network; the tool contract is the same.
