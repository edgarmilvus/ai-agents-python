# Example 2 — the three-layer pipeline

## What it does

Sanitisation, a `SIGALRM` time budget and an output validator, applied in sequence by one entry point. Four cases show each layer doing its job: a policy answer, a neutralised injection, a killed rogue loop and a rejected output.

## The listings

| file | what it is |
| --- | --- |
| `01_security_layers.py` | the listing: three layers, the agent and four cases |
| `run_security_layers.py` | the harness: asserts each layer's branch |

## Run it

```bash
cd chapter17/advanced_application_script/example/files
python3 01_security_layers.py
```

The listing is the run: a benign request, an injection, a rogue loop and a faulty output each reach their own branch. The harness asserts all four; the rogue loop really waits out the five-second budget, because the signal is the defence being shown.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the number of layers it verified |

## Notes

- The budget is preemptive here (`signal.SIGALRM`), unlike the cooperative context manager in exercise 3: this one can stop a loop that never returns.
- The injection is replaced by `[FILTERED_INSTRUCTION]` rather than deleted, so the sentence keeps its grammar and the model still has a task.
- `validate_output` returns a `[VALIDATION_FAIL]` string instead of raising; the pipeline passes that string to the caller.
