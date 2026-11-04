"""Harness for exercise 1: the timeout-bound sandbox.

Four snippets go through the function: a success, a runtime error, an explicit
non-zero exit, and one that outlives the timeout. The timeout costs the listing's
own five seconds, which is the point of the exercise.
"""
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402


def main():
    h = Harness("exercise 1 (sandbox)", FILES)
    module = load_listing(FILES / "01_sandbox.py", "sandbox")
    run = module.execute_sandboxed_code

    ok = run("print('hello from the sandbox')")
    h.equal(ok["success"], True, "a clean snippet succeeds")
    h.equal(ok["stdout"], "hello from the sandbox", "stdout comes back")
    h.equal(ok["exit_code"], 0, "the exit code is zero")

    broken = run("x = 1 / 0")
    h.equal(broken["success"], False, "a runtime error fails")
    h.contains(broken["reason"], "ZeroDivisionError", "the reason names the exception")
    h.equal(broken["exit_code"], 1, "the non-zero exit is reported")

    exited = run("import sys; sys.exit(3)")
    h.equal(exited["exit_code"], 3, "an explicit exit code is preserved")
    h.equal(exited["success"], False, "an explicit non-zero exit is a failure")

    slow = run("import time; time.sleep(6)")
    h.equal(slow["success"], False, "a timeout is a failure")
    h.contains(slow["reason"], "Timeout Error", "the timeout is named")
    h.contains(slow["stderr"], "timed out after 5 seconds", "the limit is reported")
    h.equal(slow["stdout"], "", "nothing is collected from a killed process")

    h.write_json("result.json", {"cases": 4, "timeout_limit": module.TIMEOUT_LIMIT})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 1 (sandbox)", FILES).crash())
