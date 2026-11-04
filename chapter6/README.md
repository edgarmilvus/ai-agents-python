# Chapter 6 — Introduction to Multi-Agent Systems (MAS): Manager vs. Worker

The chapter's code, one folder per section. Every folder holds the listing exactly
as it appears in the book, a harness that drives it and asserts what happened, and
an `output/` folder for what the harness produced.

| folder | listing | what it shows |
| --- | --- | --- |
| `basic_code_example/example/` | `01_manager_worker_simulation.py` | a manager gathering four coroutines |
| `advanced_application_script/example/` | `01_hierarchical_crew.py` | a CrewAI manager, two workers, a synthesis task |
| `python_implementation_template_for_reference/example/` | `01_scaling_template.py` | the dynamic worker pool, end to end |
| `exercise_1_asynchronous_task_distribution_and/exercise/` | `01_async_distribution.py` | distribution with a parallelism check |
| `exercise_2_specialized_workers_and_asynchrono/exercise/` | `02_specialized_workers.py` | two workers sharing one async client |
| `exercise_3_advanced_result_aggregation_and_co/exercise/` | `01_result_aggregation.py` | conflict resolution with an explicit rule |
| `exercise_4_interactive_challenge_dynamic_work/exercise/` | `02_dynamic_scaling.py` | a pool that grows and shrinks |

## Run the chapter

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./chapter6/run_offline.sh
```

`run_offline.sh` runs the seven harnesses and prints one line per harness; the log is
written to `chapter6/output/run_6.log`. Any harness that fails makes the suite
exit 1. The CrewAI listing is driven through a scripted CrewAI model, so no key
and no network are needed.

The two scaling scenarios (the template and exercise 4) take about 40 seconds each
because their waits are real; the other five finish in a few seconds.

## What the harnesses caught

- **A deadlock in the worker pool.** The monitor only retired workers while the
  pool was above its floor, so the last idle worker ended and was still counted
  as active; the next burst was never picked up. Both the template and the
  exercise solution now retire finished workers and refill to the floor.
- **A crew shape CrewAI 1.x rejects.** `manager_agent` must not appear in
  `agents`; the listing now lists only the workers.
- **A constructor mismatch** in exercise 2 (`id=` against `agent_id=`).
