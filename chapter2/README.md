# Chapter 2 — The Cognitive Architecture: Memory, Planning, and Tools

The chapter's code, one folder per section. Every folder holds the listing exactly
as it appears in the book, a harness that drives it and asserts what happened, and
an `output/` folder for what the harness produced.

| folder | listing | what it shows |
| --- | --- | --- |
| `basic_code_example/example/` | `01_contextual_calculator.py` | ReAct with one tool and a memory window |
| `basic_code_example/example/` | `02_tool_description.py` | the docstring a model reads before calling a tool |
| `advanced_application_script/example/` | `01_strategic_analyst.py` | RAG context, one tool, a four-stage prompt |
| `boilerplate_code_for_exercises/example/` | `01_boilerplate_code_for_exercises.py` | the mocks the four solutions assume |
| `exercise_1_contextual_reflection_and_knowledg/exercise/` | `01_contextual_reflection_agent.py` | reflection triggered by risk keywords |
| `exercise_2_hierarchical_planning_and_decompos/exercise/` | `01_hierarchical_planner.py` | a JSON plan executed step by step |
| `exercise_3_state_aware_tool_integration/exercise/` | `01_state_aware_tools.py` | state that lives on the tool |
| `exercise_4_interactive_challenge_integrating/exercise/` | `01_constrained_planner.py` | a plan that breaks its limit and is rewritten |

## Run the chapter

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./chapter2/run_offline.sh
```

`run_offline.sh` runs the eight harnesses and prints one line per harness; the log is
written to `chapter2/output/run_2.log`. Any harness that fails makes the suite
exit 1. No API key and no network are needed: the two listings that build a client
are driven through a scripted chat model.

## The exercise solutions are composed

The four solutions assume the chapter's boilerplate (`MockLLM`, `BaseTool`, the
tools), as the book says. Their harnesses concatenate the two published blocks and
run the result, so neither file is copied or edited to make the pair work:

```
boilerplate + 01_contextual_reflection_agent.py -> one program, run in process
```
