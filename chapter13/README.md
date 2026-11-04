# Chapter 13 — Human-in-the-Loop: Approval Steps and Interruption Patterns

The chapter's code, one folder per section. Every folder holds the listing exactly
as it appears in the book, a harness that drives it, and an `output/` folder for
what the harness produced. Three of the four listings wait for a human at a
terminal; the harness plays that human, which is what makes the chapter testable.

| folder | listing | what it shows |
| --- | --- | --- |
| `basic_code_example/example/` | `01_approval_gate.py` | a gate that does not block the event loop |
| `advanced_application_script/example/` | `01_state_machine_gate.py` | approval, rationale and override as states |
| `comprehensive_solution_structure/example/` | `01_solution_structure.py` | the four agents as a skeleton |
| `shared_boilerplate_for_the_solutions/example/` | `01_shared_solution_boilerplate.py` | the shared block: two exceptions and the state enum the four solutions use |
| `exercise_1_the_atomic_action_approval_gate/exercise/` | `01_atomic_approval_agent.py` | one change, one gate, and an execution state that cannot be reached without approval |
| `exercise_2_dynamic_interruption_and_redirecti/exercise/` | `01_interruption_agent.py` | a queue that stops on the flagged task and takes pause, skip or redirect |
| `exercise_3_contextual_state_reporting_and_ris/exercise/` | `01_risk_reporting_agent.py` | a risk score per task, with the gate reserved for the irreversible write |
| `exercise_4_interactive_challenge_multi_tier_s/exercise/` | `01_secure_deployment_agent.py` | two gates: a question to leave staging, a question plus a secret for production |

## Run the chapter

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./chapter13/run_offline.sh
```

`run_offline.sh` runs the four harnesses and prints one line per harness; the log is
written to `chapter13/output/run_13.log`. Any harness that fails makes the suite
exit 1. Everything here runs offline.

## What the harnesses caught

- **A gate that never fired.** Exercise 3 scored risk with `random.randint(1, 10)`
  and only asked for approval above 7, so in the runs that printed, both critical
  tasks passed with scores of 2 and 6 — the contextual-approval branch, the whole
  point of the exercise, never appeared. The score is now deterministic: an
  irreversible write is 9, heavy compute is 6. Every run shows both branches.
- **A count that came from another chapter.** The section introducing the
  solutions said "the five exercises"; this chapter has four.
