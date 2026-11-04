"""Harness for exercise 3: the caching wrapper."""
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
    h = Harness("exercise 3 (persistent cache)", FILES)
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        runpy.run_path(str(FILES / "01_persistent_cache.py"), run_name="__main__")
    printed = stdout.getvalue() + stderr.getvalue()

    h.equal(printed.count("[Cache MISS]"), 2, "each distinct call executed once")
    h.equal(printed.count("[Cache HIT]"), 2, "each repeated call was served from the cache")
    import re
    results = dict(re.findall(r"([A-D])=([0-9.]+)", printed.split("Results:")[1]))
    h.equal(results["A"], results["B"], "the repeated call came from the cache")
    h.equal(results["C"], results["D"], "the other repeated call came from the cache")
    h.check(results["A"] != results["C"], "a different key produced a different value")

    h.write_json("result.json", {"printed_lines": len(printed.splitlines())})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 3 (persistent cache)", FILES).crash())
