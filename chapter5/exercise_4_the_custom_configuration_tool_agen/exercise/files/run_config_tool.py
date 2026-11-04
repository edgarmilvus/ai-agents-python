"""Harness for exercise 4: a custom tool that reads a configuration file."""
import contextlib
import io
import os
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402


def main():
    h = Harness("exercise 4 (custom config tool)", FILES)
    output = FILES.parent / "output"
    output.mkdir(parents=True, exist_ok=True)
    previous = os.getcwd()
    os.chdir(output)
    try:
        log = io.StringIO()
        with contextlib.redirect_stdout(log):
            module = load_listing(FILES / "02_exercise_4_custom_tool_agent.py", "config_agent")
            module.setup_config_file()
            tool = module.ConfigFileReaderTool()
            answer = module.run_config_analyst_agent(
                "Our logging is set to DEBUG in production. Is that safe?", tool)
        printed = log.getvalue()

        h.check(pathlib.Path(module.CONFIG_FILE_NAME).exists(), "the tool creates its config file")
        content = tool.run("SYSTEM", "LOG_LEVEL")
        h.contains(content, "SYSTEM.LOG_LEVEL", "the tool answers with section and key")
        h.contains(content, "INFO", "the tool returns the configured level")
        h.contains(tool.run("NOPE", "X"), "not found", "a missing section is reported")

        h.contains(answer, "INFO", "the recommendation names the safer level")
        h.check("DEBUG" in answer, "the answer addresses the current setting")
        h.check(len(answer) > 100, "the answer is a reasoned recommendation")
        h.contains(printed, "Agent", "the simulated run reports its steps")

        h.write_json("result.json", {"answer": answer[:400]})
    finally:
        os.chdir(previous)
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 4 (custom config tool)", FILES).crash())
