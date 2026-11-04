# Chapter 8 — Using LangGraph: Building Cyclic State Graphs

The chapter's code, one folder per section. Every folder holds the listing exactly
as it appears in the book, a harness that drives it and asserts what happened, and
an `output/` folder for what the harness produced.

| folder | listing | what it shows |
| --- | --- | --- |
| `basic_code_example/example/` | `01_cyclic_graph.py` | generate, check, refine, stop |
| `advanced_application_script/example/` | `01_research_graph.py` | verify, refine the query, search again |
| `exercise_1_the_iterative_research_and_confide/exercise/` | `01_research_confidence.py` | a loop that stops on confidence |
| `exercise_2_defining_robust_state_with_pydanti/exercise/` | `01_robust_state.py` | a Pydantic schema inside the state |
| `exercise_3_the_code_refinement_and_self_corre/exercise/` | `01_code_refinement.py` | generate, test, debug |
| `exercise_4_interactive_challenge_enhancing_th/exercise/` | `01_financial_analyst.py` | a mandatory risk section and a review gate |
| `exercise_5_the_interactive_chatbot_with_tool/exercise/` | `01_chatbot_retries.py` | a tool retry loop with a cap |

## Run the chapter

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./chapter8/run_offline.sh
```

`run_offline.sh` runs the seven harnesses and prints one line per harness; the log is
written to `chapter8/output/run_8.log`. Any harness that fails makes the suite
exit 1. Six of the seven run offline; the research graph is driven through a
scripted chat model.

## What the harnesses caught

- **A node used as its own router.** `check_constraints` returned `"refine"` or
  `"end"`; LangGraph requires a node to return a state update, so the graph died
  with `InvalidUpdateError: Expected dict, got refine`. The decision now goes into
  the state and a separate `decide_next` router reads it.
- **`output_map=`**, which current LangGraph spells `path_map=`.
- **`langchain_core.pydantic_v1`**, removed in langchain-core 1.x: the research
  graph now imports `pydantic` directly.
