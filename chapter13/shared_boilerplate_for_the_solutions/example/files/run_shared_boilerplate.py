"""Harness for the shared block: the names the four solutions import.

The block is a library, so there is nothing to drive: the harness executes it and
checks that every name the listings rely on exists and has the right kind.
"""
import contextlib
import io
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness  # noqa: E402


def main():
    h = Harness("shared solution boilerplate", FILES)
    namespace = {"__name__": "shared"}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(FILES.joinpath("01_shared_solution_boilerplate.py").read_text(),
                     "boilerplate", "exec"), namespace)

    for name in ("AgentStateViolationError", "AuthorizationFailure"):
        h.check(issubclass(namespace.get(name, type), Exception), f"{name} is an exception")
    state = namespace.get("AgentState")
    h.check(state is not None, "AgentState is defined")
    for member in ("PLANNING", "GENERATING_PROPOSAL", "AWAITING_APPROVAL", "EXECUTING", "TERMINATED"):
        h.check(member in state.__members__, f"AgentState.{member} exists")
    h.write_json("result.json", {"states": [m for m in state.__members__]})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("shared solution boilerplate", FILES).crash())
