# Exercise 1 — contextual reflection

## What it does

A project-management agent with a memory window and a reflection tool. The tool is called only when the question mentions risk, and the answer is grounded in the retrieved best practices.

## The listings

| file | what it is |
| --- | --- |
| `01_contextual_reflection_agent.py` | the solution from the chapter |
| `run_contextual_reflection.py` | the harness: composes the boilerplate with this listing and asserts the result |

## Run it

```bash
cd chapter2/exercise_1_contextual_reflection_and_knowledg/exercise/files
python3 run_contextual_reflection.py
```

`01_contextual_reflection_agent.py` assumes the chapter's boilerplate, so the harness composes the two published blocks and runs the result. It writes `output/result.json` and exits non-zero if the reflection never fires or memory overflows its window.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the three answers and the number of remembered turns |

## Notes

- Runs offline and deterministically: the boilerplate's `MockLLM` answers, no key is read.
- The harness runs the two published blocks exactly as the book publishes them; neither file is copied or edited.
