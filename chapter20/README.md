# Chapter 20 — The Capstone: A 'Software Development Agency' Swarm

The chapter's code, one folder per section. Every folder holds the listing exactly
as it appears in the book, a harness that drives it, and an `output/` folder for
what the harness produced.

| folder | listing | what it shows |
| --- | --- | --- |
| `basic_code_example/example/` | `01_sequential_swarm.py` | two roles, one handoff, one halt |
| `advanced_application_script/example/` | `01_iterative_swarm.py` | fail, feed back, refine, deliver |
| `worked_example_solution_shell_and_setup/example/` | `01_swarm_shell.py` | every class the exercises extend |
| `shared_boilerplate_models_and_base_agent/example/` | `01_swarm_boilerplate.py` | the models and the base agent |
| `exercise_1_centralized_asynchronous_state_man/exercise/` | `01_state_hub.py` | a future per status |
| `exercise_2_dynamic_role_assignment_middleware/exercise/` | `01_role_router.py` | least-busy routing |
| `exercise_3_formalizing_the_qa_and_iterative_r/exercise/` | `01_qa_loop.py` | a bug report as feedback |
| `exercise_4_interactive_challenge_integrating/exercise/` | `01_security_auditor.py` | a fourth gate before QA |
| `exercise_5_building_the_self_healing_swarm_re/exercise/` | `01_self_healing.py` | replace a hung agent |

## Run the chapter

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./chapter20/run_offline.sh
```

`run_offline.sh` runs the nine harnesses and prints one line per harness; the log is
written to `chapter20/output/run_20.log`. Any harness that fails makes the suite
exit 1. Everything runs offline: the model calls are mocked, and the swarm is
asynchronous but local.

**The five exercise sections are one program.** The book prints the shared models
and `BaseAgent` once, then one section per exercise, so `01_state_hub.py` on its own
does not have `ProjectState`, and `01_qa_loop.py` needs the developer defined by
exercise 2. Each harness loads the sections its file depends on, in book order,
before running it. Read the Solutions section top to bottom and this is exactly what
you are doing by hand.

## What the harnesses caught

- **The iterative swarm never iterated.** The mock dispatched on the prompt for
  things it kept in `role` ("QualityAssurance/execute_test"), so every QA call
  returned its error branch: three identical failures, `Failed tests: None`, no
  refinement. It now dispatches on the role and reads the code's state from the
  prompt.
- **The developer never refined.** Its branch tested for `"refinement"` while the
  prompt said `"Refinement"`, so iteration 2 re-sent the first draft. The demo now
  fails once and passes on the second attempt, which is what the prose describes.
- **`submit_task` was awaited twice.** It returns a future, so
  `await agent.submit_task(x)` gives you the future, not the result; the loop then
  indexed it and raised `'Future' object is not subscriptable`. `BaseAgent` now has
  `run_task`, which awaits both, and the sections that want a result use it.
- **The QA verdict was a coin flip.** `random.random() < 0.6` meant the refinement
  demo sometimes passed on the first try; QA now fails the first artifact and passes
  the second.
- **Pydantic 2 deprecated `copy`.** The state hub used `ProjectState.copy(update=...)`;
  it now uses `model_copy`.
