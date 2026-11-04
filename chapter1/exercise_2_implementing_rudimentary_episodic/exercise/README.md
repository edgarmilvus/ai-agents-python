# Exercise 2 — rudimentary episodic memory

## What it does

An agent that runs three tasks in sequence and remembers the outcome of the last one. A failure is not retried immediately: memory forces a review step first, and only a review that succeeds allows the task to be attempted again.

## The listings

| file | what it is |
| --- | --- |
| `01_episodic_memory_task_agent.py` | the solution: `EpisodicMemory` plus an Orient/Decide that reads it |
| `run_episodic_memory.py` | the harness: a seed that forces failures, and the review/retry checks |

## Run it

```bash
cd chapter1/exercise_2_implementing_rudimentary_episodic/exercise/files
python3 01_episodic_memory_task_agent.py
```

The listing is the run: it prints the three tasks as the agent works through them. The harness drives seed 1, which produces two failures, and exits non-zero if a failure is not followed by a review and a retry of the same task.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the seed, the number of failures and reviews, and the full episode log |

## Notes

- The 30% failure rate is simulated with `random`; the harness seeds it, so the episode is reproducible.
- The review never advances `task_index`: that is what makes the retry a retry.
- Running the listing directly uses the unseeded generator; a run without failures never exercises the review branch.
