"""Harness for exercise 4: structured output instead of free-form text."""
import contextlib
import io
import pathlib
import runpy
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness  # noqa: E402


def main():
    h = Harness("exercise 4 (structured output)", FILES)
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        runpy.run_path(str(FILES / "01_structured_output.py"), run_name="__main__")
    printed = stdout.getvalue() + stderr.getvalue()

    h.contains(printed, "Token Cost Comparison", "the two formats are compared")
    h.contains(printed, "Validation SUCCESS", "the structured answer parsed")
    h.contains(printed, "Tool: FlightSearchTool", "the tool name came from the schema")
    h.contains(printed, '"departure": "NYC"', "the arguments survived validation")

    h.write_json("result.json", {"printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 4 (structured output)", FILES).crash())
