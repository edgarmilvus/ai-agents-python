# Example 1 — the sandbox runner

## What it does

`execute_code` writes a snippet to a temporary file, runs it with the current interpreter in a subprocess, and returns `(exit_code, stdout, stderr)`. The demo pushes three snippets through it: a success, a division by zero, and a file that will not parse.

## The listings

| file | what it is |
| --- | --- |
| `01_sandbox_runner.py` | the listing: the executor and its three cases |
| `run_sandbox_runner.py` | the harness: checks that each case lands in its branch |

## Run it

```bash
cd chapter15/basic_code_example/example/files
python3 01_sandbox_runner.py
```

The listing is the run: three snippets go through the sandbox and each prints its exit code and both streams. The harness asserts the three branches and exits non-zero if a case lands in the wrong one.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the number of cases it checked |

## Notes

- `sys.executable`, not `python`: the listing has to find an interpreter on a machine where `python` is not on `PATH`.
- The third case is a syntax error on purpose, and it exits 1 — the same code as a runtime error. The exit code alone cannot tell them apart, which is what the traceback is for.
- Every snippet runs in its own file, so the parent process only ever sees text.
