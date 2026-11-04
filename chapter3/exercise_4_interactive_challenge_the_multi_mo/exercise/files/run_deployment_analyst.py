"""Harness for exercise 4: a live status tool and a historical log tool."""
import contextlib
import io
import json
import os
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness  # noqa: E402

CHAPTER = ROOT / "chapter3"
SETUP = CHAPTER / "necessary_setup_code_block/example/files" / "01_mock_services.py"


def compose(solution: pathlib.Path):
    source = SETUP.read_text() + "\n\n" + solution.read_text()
    namespace = {"__name__": "__main__"}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(source, str(solution), "exec"), namespace)
    return namespace


def main():
    h = Harness("exercise 4 (deployment analyst)", FILES)
    output = FILES.parent / "output"
    output.mkdir(parents=True, exist_ok=True)
    previous = os.getcwd()
    os.chdir(output)
    try:
        ns = compose(FILES / "01_deployment_analyst_agent.py")
        status = ns["check_live_service_status"]("deployment_api")
        h.contains(status, "OK", "a healthy service is reported as OK")
        degraded = ns["check_live_service_status"]("log_aggregator")
        h.contains(degraded, "DEGRADED", "a degraded service keeps its state")
        h.contains(ns["check_live_service_status"]("nope"), "UNKNOWN",
                   "an unknown service is reported as unknown")

        report = ns["analyze_deployment_log"](ns["LOG_FILE_PATH"])
        h.contains(report, "ERROR", "the log report mentions errors")
        h.contains(report, "2", "the report counts the two errors")
        h.contains(report, "Memory limit exceeded", "the last critical error is quoted")
        h.contains(ns["analyze_deployment_log"](str(output / "missing.log")), "ERROR",
                   "a missing log file is reported, not raised")

        h.write_json("result.json", {
            "status": status,
            "degraded": degraded,
            "log_report": report,
        })
    finally:
        os.chdir(previous)
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 4 (deployment analyst)", FILES).crash())
