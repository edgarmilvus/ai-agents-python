# Chapter 4 — Reasoning Loops: Chain of Thought (CoT) and ReAct

The chapter's code, one folder per section. Every folder holds the listing exactly
as it appears in the book, a harness that drives it and asserts what happened, and
an `output/` folder for what the harness produced.

| folder | listing | what it shows |
| --- | --- | --- |
| `basic_code_example/example/` | `01_cot_chain.py` | a reasoning prompt piped through model and parser |
| `advanced_application_script/example/` | `01_react_agent.py` | two tools behind a Thought/Action/Observation loop |
| `exercise_1_enforcing_structured_cot_for_audit/exercise/` | `01_structured_cot.py` | fixed section headers for an auditable answer |
| `exercise_2_implementing_a_minimalist_iterativ/exercise/` | `02_react_agent.py` | a hand-written loop that stops on a condition |
| `exercise_3_interactive_challenge_dynamic_reac/exercise/` | `01_dynamic_react.py` | refinement driven by the quality of an observation |
| `exercise_4_structured_react_output_via_pydant/exercise/` | `02_schema_agent.py` | a Pydantic schema with range validation |
| `exercise_5_comparative_analysis_cot_vs_react/exercise/` | `01_cot_vs_react.py` | the same question answered by both loops |

## Run the chapter

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./chapter4/run_offline.sh
```

`run_offline.sh` runs the seven harnesses and prints one line per harness; the log is
written to `chapter4/output/run_4.log`. Any harness that fails makes the suite
exit 1. The two listings that call a model are driven through a scripted chat
model, so no key and no network are needed.

## Starters and solutions

Exercises 2 and 4 publish a starter and a solution in the same folder. The
`How to run it` block runs the solution (or its harness); the starter is the
skeleton the exercise begins from and runs nothing.

## Five fragments stay in the book

The five blocks under *Detailed Code Breakdown* are sections of
`01_cot_chain.py`, and the block under *Understanding the Power of the Prompt
Anchor* is prose. They are illustrations, not listings: they have no file and no
harness, and the sync check skips them.
