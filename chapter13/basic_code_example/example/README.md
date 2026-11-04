# Example 1 — the asynchronous approval gate

## What it does

An asynchronous deployment workflow that stops at the one action it must not take
alone. The gate asks in a terminal, so the answer has to arrive without blocking
the event loop: `asyncio.to_thread` carries the blocking `input()` to a worker
thread and `await` gives control back to the loop. A `STATUS` answer is a
redirection — the agent reports, then asks again.

## The listings

| file | what it is |
| --- | --- |
| `01_approval_gate.py` | the listing: phases, the gate, the entry point |
| `run_approval_gate.py` | the harness: plays the human in both branches |

## Run it

```bash
cd chapter13/basic_code_example/example/files
python3 01_approval_gate.py
```

The listing waits at the gate: type `APPROVE` and the deployment runs, or `ABORT`
and the rollback path runs. `run_approval_gate.py` plays the human instead — a
`STATUS` request followed by `APPROVE`, then a second run that aborts — and exits
non-zero if either branch stops working.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | both branches marked as exercised |

## Notes

- Standard library only, offline. The listing spends about five seconds in
  `simulate_agent_task`; the harness keeps that wait.
- The point of the listing is that the *async* function never calls `input()`
  directly. `01_approval_gate.py` will hang the loop if the `to_thread` call is
  replaced by a bare `input()`, which is the pitfall the section describes.
