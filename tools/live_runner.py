#!/usr/bin/env python3
"""Run the volume's model-calling listings against a real API.

The offline suite proves the code paths; this proves the prompts. It runs one or two
example listings per chapter that instantiate a model, each in its project's `output/`
so nothing is written into the tree.

There is no provider to choose. The listings read three variables and the runner
passes them through unchanged:

    OPENAI_COMPATIBLE_BASE_URL   default https://openrouter.ai/api/v1
    OPENAI_COMPATIBLE_MODEL      default ~deepseek/deepseek-flash-latest
    OPENAI_COMPATIBLE_API_KEY    required

Chapters 11 and 16 need two more, for embeddings and tracing, and only when they run.

    python3 tools/live_runner.py --list
    python3 tools/live_runner.py --only 1 4
    python3 tools/live_runner.py
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import time
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "output" / "live"

BASE_URL_DEFAULT = "https://openrouter.ai/api/v1"
MODEL_DEFAULT = "~deepseek/deepseek-flash-latest"

# chapter, project, listing, timeout (s), notes
ROWS = [
    (1, "basic_code_example/example", "01_agentic_loop_research.py", 240, "agent loop with tools"),
    (2, "basic_code_example/example", "01_contextual_calculator.py", 180, "ReAct + memory"),
    (2, "advanced_application_script/example", "01_strategic_analyst.py", 240, "multi-turn analyst"),
    (3, "advanced_application_script/example", "01_market_analyst.py", 240, "tools writing a file"),
    (4, "basic_code_example/example", "01_cot_chain.py", 120, "chain of thought"),
    (4, "advanced_application_script/example", "01_react_agent.py", 240, "ReAct over two tools"),
    (5, "basic_code_example/example", "01_basic_research_agent.py", 360, "CrewAI, two agents"),
    (5, "advanced_application_script/example", "01_advanced_application_script.py", 480, "CrewAI, writes a brief"),
    (6, "advanced_application_script/example", "01_hierarchical_crew.py", 900, "CrewAI, manager"),
    (7, "basic_code_example/example", "01_sequential_crew.py", 420, "CrewAI, sequential"),
    (7, "advanced_application_script/example", "01_marketing_crew.py", 480, "CrewAI, marketing campaign"),
    (7, "exercise_1_the_technical_content_writer_crew/exercise", "01_content_crew.py", 300, "CrewAI, exercise 1"),
    (7, "exercise_2_the_financial_analysis_crew_delega/exercise", "01_financial_crew.py", 420, "CrewAI, exercise 2, delegation"),
    (7, "exercise_4_interactive_challenge_integrating/exercise", "01_validation_crew.py", 480, "CrewAI, validation crew"),
    (7, "exercise_3_the_global_product_launch_crew_hie/exercise", "01_launch_crew.py", 900, "CrewAI, exercise 3, hierarchical", "slow"),
    (7, "solution_template_and_code_structure/example", "01_solution_template.py", 1200, "four crews in one run", "slow"),
    (8, "advanced_application_script/example", "01_research_graph.py", 300, "LangGraph cycle"),
    (11, "basic_code_example/example", "01_context_window_rag.py", 240, "RAG over a policy"),
    (11, "advanced_application_script/example", "01_strategy_analyst_rag.py", 300, "RAG over project history"),
    (16, "basic_code_example_activating_global_tracing/example", "01_global_tracing.py", 180, "trace to LangSmith"),
    (16, "advanced_application_script/example", "01_traced_agent.py", 240, "traced tool-calling agent"),
    (16, "unified_solution_block_for_the_five_exercises/example", "01_solutions.py", 420, "five solutions + dataset"),
    (19, "advanced_application_script/example", "01_optimized_pipeline.py", 240, "structured output via parse"),
]
# Rows with a sixth element are slow: `--slow` includes them.

# A few rows need a second service, not just the chat gateway. Without it the row is
# reported as skipped, not failed: nothing is broken, the variable is simply unset.
NEEDS = {
    11: ("EMBEDDING_API_KEY", "embeddings need EMBEDDING_API_KEY (see the setup)"),
}

# A few exercise listings define a driver function and leave the call to the reader
# ("deferred to the main block"). The live run executes the function as well, so the
# same listing faces the real model instead of only its harness.
DRIVERS = {
    "01_content_crew.py": "run_exercise_1",
    "01_financial_crew.py": "run_exercise_2",
    "01_launch_crew.py": "run_exercise_3",
}

BAD_MARKERS = (
    "Traceback (most recent call last)",
    "FATAL ERROR",
    "environment variable not set",
    "AuthenticationError",
    "ConnectionError",
    "Insufficient Balance",
    "ToolExecutionFailedError",
    "repeated_tool_call",
)


def langsmith_runs() -> int | None:
    key = os.environ.get("LANGCHAIN_API_KEY")
    if not key:
        return None
    try:
        from langsmith import Client
        client = Client(api_url="https://api.smith.langchain.com", api_key=key)
        return len(list(client.list_runs(project_name="Book8_Ch16_BasicTracingExample", limit=100)))
    except Exception:
        return None


def env_for() -> dict[str, str]:
    """The child process gets this shell's environment, plus the two defaults.

    Nothing is read from a file: chapter 11's EMBEDDING_* and chapter 16's
    LANGCHAIN_API_KEY arrive the same way, exported by whoever runs the live run.
    """
    env = dict(os.environ)
    env.setdefault("OPENAI_COMPATIBLE_BASE_URL", BASE_URL_DEFAULT)
    env.setdefault("OPENAI_COMPATIBLE_MODEL", MODEL_DEFAULT)
    env["PYTHONUNBUFFERED"] = "1"
    return env


def run_one(chapter: int, project: str, listing: str, timeout: int) -> tuple[str, float, str]:
    folder = ROOT / f"chapter{chapter}" / project
    script = folder / "files" / listing
    workdir = folder / "output"
    workdir.mkdir(parents=True, exist_ok=True)
    started = time.time()
    driver = DRIVERS.get(listing)
    if driver:
        code_arg = ("import runpy; ns = runpy.run_path(%r); ns[%r]()" % (str(script), driver))
        command = [sys.executable, "-c", code_arg]
    else:
        command = [sys.executable, str(script)]
    try:
        result = subprocess.run(
            command,
            cwd=workdir, env=env_for(), capture_output=True, text=True,
            # No terminal: a listing that would offer to prompt for a key must see
            # a closed stdin and take its non-interactive branch, not hang.
            stdin=subprocess.DEVNULL,
            timeout=timeout,
        )
        output = result.stdout + result.stderr
        code = result.returncode
    except subprocess.TimeoutExpired as exc:
        partial = exc.stdout or ""
        if isinstance(partial, bytes):
            partial = partial.decode(errors="ignore")
        output = partial + "\n[TIMEOUT] exceeded %ds" % timeout
        code = 124
    duration = time.time() - started
    OUT.mkdir(parents=True, exist_ok=True)
    log = OUT / f"ch{chapter:02d}-{listing.replace('.py', '')}.log"
    log.write_text(output)
    (OUT / "last.log").write_text(output)

    status = "PASS" if code == 0 else ("TIMEOUT" if code == 124 else "FAIL")
    if status == "PASS" and any(marker in output for marker in BAD_MARKERS):
        status = "FAIL"
    if status == "PASS" and len(output.strip()) < 40:
        status = "FAIL (silent)"
    return status, duration, output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", nargs="*", type=int, help="chapters to run")
    parser.add_argument("--list", action="store_true", help="print the rows and exit")
    parser.add_argument("--slow", action="store_true",
                        help="include the hierarchical crews, which take 7-20 minutes")
    args = parser.parse_args()

    rows = [row for row in ROWS
            if (not args.only or row[0] in args.only) and (args.slow or len(row) == 5)]
    if args.list:
        for chapter, project, listing, timeout, note, *_ in rows:
            print(f"ch{chapter:<3} {listing:<45} {note}")
        return 0

    base = os.environ.get("OPENAI_COMPATIBLE_BASE_URL", BASE_URL_DEFAULT)
    model = os.environ.get("OPENAI_COMPATIBLE_MODEL", MODEL_DEFAULT)
    if not os.environ.get("OPENAI_COMPATIBLE_API_KEY"):
        print("missing OPENAI_COMPATIBLE_API_KEY", file=sys.stderr)
        print('  export OPENAI_COMPATIBLE_API_KEY="..."', file=sys.stderr)
        return 2

    print(f"endpoint: {base}  model: {model}")
    ls_before = langsmith_runs()

    print(f"{'chapter':<8}{'listing':<45}{'status':<14}{'time':>7}")
    print("-" * 74)
    failures = 0
    ran = 0
    skipped = 0
    started = time.time()
    for chapter, project, listing, timeout, note, *_ in rows:
        need = NEEDS.get(chapter)
        if need and not os.environ.get(need[0]):
            skipped += 1
            print(f"ch{chapter:<6}{listing:<45}{'SKIP':<14}{'-':>7}")
            # A key that is already on the disk is worth naming: the runner does
            # not read it (nothing is read from a file), but the reader can.
            key_file = pathlib.Path.home() / ".config" / "gemini" / "key"
            hint = ""
            if need[0] == "EMBEDDING_API_KEY" and key_file.exists():
                hint = f" — the key is already in {key_file}"
            print(f"        {need[1]}{hint}")
            continue
        status, duration, output = run_one(chapter, project, listing, timeout)
        ran += 1
        print(f"ch{chapter:<6}{listing:<45}{status:<14}{duration:>6.1f}s")
        if status != "PASS":
            failures += 1
            tail = [line for line in output.strip().splitlines() if line.strip()][-4:]
            for line in tail:
                print(f"        {line[:110]}")
    total = time.time() - started

    print("-" * 74)
    tail = f", {skipped} skipped" if skipped else ""
    print(f"{ran} of {len(rows)} listings ran{tail}, {total:.1f}s total, {failures} failure(s)")
    after_ls = langsmith_runs()
    if ls_before is not None and after_ls is not None:
        print(f"LangSmith runs in Book8_Ch16_BasicTracingExample: {ls_before} -> {after_ls}")
    print(f"logs: {OUT.relative_to(ROOT)}/")
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
