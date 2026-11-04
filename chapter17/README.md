# Chapter 17 — Security for Agents: Preventing Prompt Injection and Rogue Loops

The chapter's code, one folder per section. Every folder holds the listing exactly
as it appears in the book, a harness that drives it, and an `output/` folder for
what the harness produced.

| folder | listing | what it shows |
| --- | --- | --- |
| `17_2_basic_code_example_implementing_a_keywor/example/` | `01_sanitization_layer.py` | a deny-list and the `\b` that keeps it honest |
| `advanced_application_script/example/` | `01_security_layers.py` | sanitise, budget, validate — in that order |
| `worked_example_consolidated_python_code_block/example/` | `01_exercise_scripts.py` | the four exercises, demonstrated |
| `unified_solution_block_for_the_four_exercises/example/` | `01_solutions.py` | the same four, complete |

## Run the chapter

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./chapter17/run_offline.sh
```

`run_offline.sh` runs the four harnesses and prints one line per harness; the log is
written to `chapter17/output/run_17.log`. Any harness that fails makes the suite
exit 1. Everything here is standard library and runs offline; the suite spends about
six seconds asleep, because two of the demos are about time budgets and one of them
is enforced by a real `SIGALRM`.

## What the harnesses caught

- **The consolidated block did not parse.** The exercise-1 demo was a single line of
  `$` padding with no closing quote — the file raised `SyntaxError` at import, so
  none of the four exercises ran. It now has four cases: safe, blacklisted, too
  short, and repetitive padding.
- **The budget could not stop anything.** `ExecutionBudget` checks the clock in
  `__exit__`, so it reports an overrun only after the block has finished; the demo
  claimed "This line should not be reached" and then reached it every time. The
  class and the label now say what it does, and example 2 shows the preemptive
  version that can interrupt.
- **The off-topic branch was never taken.** The worked example asked for the
  temperature in Tokyo; the classifier only knows `joke`, `poem`, `sing a song` and
  `weather today`, so the query passed as SAFE and was answered by the RAG. It now
  uses a joke, and all three classifications appear.
