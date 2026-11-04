# Exercise 3 — state-aware tools

## What it does

An agent whose state lives on the tool, not in the agent: one cart instance survives four prompts, so a second request is added to the first and checkout clears the state.

## The listings

| file | what it is |
| --- | --- |
| `01_state_aware_tools.py` | the solution from the chapter |
| `run_state_aware_tools.py` | the harness: composes the boilerplate with this listing and asserts the result |

## Run it

```bash
cd chapter2/exercise_3_state_aware_tool_integration/exercise/files
python3 run_state_aware_tools.py
```

`01_state_aware_tools.py` assumes the chapter's boilerplate, so the harness composes the two published blocks and runs the result. It writes `output/result.json` and exits non-zero if the cart loses the state that has to survive between prompts.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the four responses and the cart after checkout |

## Notes

- Runs offline and deterministically: the boilerplate's `MockLLM` answers, no key is read.
- The harness runs the two published blocks exactly as the book publishes them; neither file is copied or edited.
