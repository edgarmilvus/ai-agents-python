# Chapter 15 — Coding Agents: Building an Agent That Writes and Tests Code

The chapter's code, one folder per section. Every folder holds the listing exactly
as it appears in the book, a harness that drives it, and an `output/` folder for
what the harness produced.

| folder | listing | what it shows |
| --- | --- | --- |
| `basic_code_example/example/` | `01_sandbox_runner.py` | a snippet in a subprocess, with its exit code |
| `advanced_application_script/example/` | `01_refinement_agent.py` | fail, package the failure, refine, pass |
| `exercise_1_implementing_a_secure_timeout_boun/exercise/` | `01_sandbox.py` | the timeout that turns a hang into feedback |
| `exercise_2_defining_structured_output_for_age/exercise/` | `01_structured_output.py` | the shape of a model answer, validated |
| `exercise_3_implementing_the_iterative_refinem/exercise/` | `01_orchestrator.py` | the loop, and the payload that drives it |
| `exercise_4_interactive_challenge_integrating/exercise/` | `01_static_analysis.py` | a linter that costs no subprocess |

The chapter prints four `#### Implementation Sketch` blocks — the exercise's
reference code. They stay in the book and have no file here: each one assumes the
classes defined in the exercise above it, so it is a sketch to read, not a program
to run. The runnable solutions are the listings above.

## Run the chapter

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./chapter15/run_offline.sh
```

`run_offline.sh` runs the six harnesses and prints one line per harness; the log is
written to `chapter15/output/run_15.log`. Any harness that fails makes the suite
exit 1. Everything here runs offline.

## What the harnesses caught

This chapter is about sandboxes, and every defect was in the boundary between a
process and its caller.

- **The feedback never arrived.** The generated `run_tests.py` printed
  `json.dumps(feedback)` without importing `json`, so the parent's parse failed and
  the loop fell back to `EXECUTION_ERROR`. The example ended with
  "Unexpected execution error" instead of refining the code.
- **Half the output was captured.** The wrapper redirected `sys.stdout` only;
  `unittest` reports to stderr, so the captured buffer was empty and every run was
  labelled `UNKNOWN_ERROR`. Both streams are redirected now, and success is checked
  before failure so `OK` is not shadowed by a stray "Error".
- **The interpreter did not exist.** Exercise 1 ran `["python", path]`; macOS and
  the container have `python3` and `sys.executable`. The chapter's own basic
  example already explained why `sys.executable` is the right answer.
- **The prose blamed the wrong exception.** The breakdown said the first attempt
  failed with a `TypeError` while sorting strings. Strings sort fine: the test
  failed with `AssertionError: ValueError not raised`, and the text now says so.
- **The exit-code table had a row that cannot happen.** Python exits 1 for a file
  it cannot parse, not 2; the table now says so and explains what the traceback is
  for.
