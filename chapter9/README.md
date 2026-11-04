# Chapter 9 — Consensus and Critique: How Agents Review Each Other's Work

The chapter's code, one folder per section. Every folder holds the listing exactly
as it appears in the book, a harness that drives it and asserts what happened, and
an `output/` folder for what the harness produced.

| folder | listing | what it shows |
| --- | --- | --- |
| `basic_code_example/example/` | `01_structured_critique.py` | four reviewers, one schema, one rejected score |
| `advanced_application_script/example/` | `01_critique_loop.py` | weighted consensus feeding the next revision |
| `unified_code_block_for_exercises_scaffold/example/` | `01_exercise_scaffold.py` | the mocks the exercises compose |
| `unified_code_block_for_exercises_complete/example/` | `01_exercise_complete.py` | the whole pipeline, end to end |
| `exercise_1_enforcing_structured_feedback_with/exercise/` | `01_pydantic_validators.py` | one valid payload, two rejections |
| `exercise_2_implementing_a_weighted_consensus/exercise/` | `01_weighted_consensus.py` | weights and a veto |
| `exercise_3_designing_the_iterative_refinement/exercise/` | `01_refinement_loop.py` | a loop that stops on a score |
| `exercise_4_interactive_challenge_semantic_rev/exercise/` | `01_semantic_review.py` | similarity boosting a critic's weight |
| `exercise_5_auditability_and_persistence_of_cr/exercise/` | `01_critique_audit.py` | every critique persisted and read back |

## Run the chapter

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./chapter9/run_offline.sh
```

`run_offline.sh` runs the nine harnesses and prints one line per harness; the log is
written to `chapter9/output/run_9.log`. Any harness that fails makes the suite
exit 1. Everything here runs offline; the two examples and exercise 1 are executed
as scripts, the other four are composed with the chapter's scaffold.

## The scaffold the exercises compose

Exercises 2 to 5 have no imports of their own: they assume the
`Unified Code Block for Exercises`. Their harnesses concatenate the scaffold and
the solution and run the result, exactly as the book presents the pair.

## What the harnesses caught

- **A mock that raised the wrong error.** `AgentCritique` required every field in
  its constructor, so a payload missing `suggested_refinement_steps` died with a
  `TypeError` before validation could report it. The mock now stores only the
  fields it receives, as Pydantic does — in the scaffold and in exercise 1.
- **A typo in the coercion path** (`score_out_out_of_10`), which turned every
  string score into "must be an integer".
- **A parameter the scaffold did not have.** Exercise 4 passes `task_vector=`;
  the consensus function only knew the module constant.
- **A diagram hidden in a code fence.** The DOT "requirement" was an empty
  `dot` fence wrapping the rendered image, so the image could not render; the
  fence is gone and the diagram is published as a figure.
