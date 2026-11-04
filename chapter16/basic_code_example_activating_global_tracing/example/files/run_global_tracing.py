"""Harness for the basic LCEL chain.

The listing's whole point is the environment switch, so the harness sets the
LangSmith flag to false and checks that the chain still runs: tracing is an
observer, and its absence must not change the answer. The model is a fake.
"""
import contextlib
import io
import os
import pathlib
import runpy
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness  # noqa: E402

from fake_agents import text_model  # noqa: E402
import langchain_openai  # noqa: E402

ANSWER = "• Observability shortens the debug loop.\n• Traces make the loop visible."


def main():
    h = Harness("example 1 (global tracing)", FILES)
    os.environ["OPENAI_COMPATIBLE_API_KEY"] = "harness-placeholder"
    os.environ["LANGCHAIN_API_KEY"] = "harness-placeholder"
    os.environ["LANGCHAIN_TRACING_V2"] = "false"

    langchain_openai.ChatOpenAI = lambda **kwargs: text_model(ANSWER)

    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        runpy.run_path(str(FILES / "01_global_tracing.py"), run_name="__main__")
    printed = stdout.getvalue() + stderr.getvalue()

    h.contains(printed, "Starting Chain Execution", "the chain was invoked")
    h.contains(printed, "Tracing disabled for project: Book8_Ch16_BasicTracingExample",
               "the banner reports the switch it actually read")
    h.contains(printed, "--- Chain Output ---", "the chain returned")
    h.contains(printed, "Observability shortens the debug loop", "the answer is the model's")
    h.equal(os.environ["LANGCHAIN_TRACING_V2"], "false",
            "the listing did not force tracing back on")

    h.write_json("result.json", {"tracing": False})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 1 (global tracing)", FILES).crash())
