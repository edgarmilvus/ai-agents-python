"""Harness for exercise 2: context trimming by re-ranking."""
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
    h = Harness("exercise 2 (trimming)", FILES)
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        runpy.run_path(str(FILES / "01_rerank_trimming.py"), run_name="__main__")
    printed = stdout.getvalue() + stderr.getvalue()

    import re
    saving = float(re.search(r"Percentage Cost Saving for LLM Input: ([0-9.]+)%", printed).group(1))
    h.check(saving >= 60, f"the reduction reached {saving:.2f}% (the exercise asks for 60%)")
    h.contains(printed, "Retained 3 documents total", "two relevant docs and one supporting")
    h.contains(printed, "Final Context Size (3 documents)", "the trimmed context is measured")

    h.write_json("result.json", {"printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 2 (trimming)", FILES).crash())
