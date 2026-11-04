# Chapter 1 — Beyond the Prompt: What Are Autonomous Agents?

The chapter's code, one folder per listing. Every folder holds the listing exactly
as it appears in the book, a harness that drives it and asserts what happened, and
an `output/` folder for what the harness produced.

| folder | listing | what it shows |
| --- | --- | --- |
| `basic_code_example/example/` | `01_agentic_loop_research.py` | the OODA loop as a `while` loop over a JSON contract |
| `advanced_application_script/example/` | `01_self_correcting_validation_agent.py` | a failed validation feeding a correction that is validated again |
| `exercise_1_simulating_the_ooda_loop/exercise/` | `01_ooda_resource_collector.py` | four phases as four functions sharing one world state |
| `exercise_2_implementing_rudimentary_episodic/exercise/` | `01_episodic_memory_task_agent.py` | memory of the last outcome changing the next decision |
| `exercise_3_rule_based_tool_routing_and_execut/exercise/` | `01_rule_based_tool_router.py` | routing a query to a tool, then calling it |
| `exercise_4_interactive_challenge_introducing/exercise/` | `01_planning_layer_rag.py` | deciding *whether* to retrieve before retrieving |
| `worked_example_the_whole_chapter_in_one_scrip/example/` | `01_all_exercises_demo.py` | the four exercises as one runnable script |

## Run the chapter

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./chapter1/run_offline.sh
```

`run_offline.sh` runs the seven harnesses and prints one line per harness; the log is
written to `chapter1/output/run_1.log`. Any harness that fails makes the suite
exit 1. The harnesses need no API key and no network: the listing that talks to
OpenAI is driven through a scripted client installed by its harness.

A single listing can be run on its own:

```bash
export OPENAI_COMPATIBLE_API_KEY=sk-or-...
.venv/bin/python chapter1/basic_code_example/example/files/01_agentic_loop_research.py
```

That one calls a real model and therefore needs the key. Its harness does not:
it runs the same listing against a scripted client, so the suite is offline. The
endpoint and the model are environment variables too — see the repository
README.
