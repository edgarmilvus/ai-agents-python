# Example 2 — the iterative swarm

## What it does

Product owner, developer and QA in an asynchronous loop. The first draft fails one test case, the failure goes back as structured feedback, and the refined implementation passes on iteration 2.

## The listings

| file | what it is |
| --- | --- |
| `01_iterative_swarm.py` | the listing: mock model, three roles, the coordinator |
| `run_iterative_swarm.py` | the harness: checks the loop converges |

## Run it

```bash
cd chapter20/advanced_application_script/example/files
python3 01_iterative_swarm.py
```

The listing is the run: iteration 1 fails its tests, the feedback reaches the developer, and iteration 2 delivers the refined code. The harness checks that the loop converges instead of exhausting its attempts.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the number of iterations |

## Notes

- The mock used to dispatch on the prompt for things it kept in the role, so every QA call returned its error branch and the loop failed three times with "Failed tests: None". It now dispatches on `role` and reads the code's state from the prompt.
- The developer's refinement branch was matched with a lowercase `refinement`, but the prompt says `Refinement`; the first draft was returned forever.
- Both roles run on `asyncio.sleep`, so the coordinator's `await` is what sequences them.
