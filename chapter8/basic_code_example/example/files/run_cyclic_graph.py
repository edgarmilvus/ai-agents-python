"""Harness for the basic cyclic graph: generate, check, refine, stop."""
import contextlib
import io
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402


def main():
    h = Harness("example 1 (cyclic graph)", FILES)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        module = load_listing(FILES / "01_cyclic_graph.py", "cyclic_graph")
    printed = log.getvalue()

    h.equal(module.final_state["iterations"], 2, "the loop ran twice")
    h.equal(len(module.final_state["generation"].split()), 5, "the final title satisfies the constraint")
    h.contains(printed, "Constraint Failed", "the first title broke the constraint")
    h.contains(printed, "Constraint Met", "the second title satisfied it")
    h.contains(printed, "Looping back", "the conditional edge sent the flow back")
    h.equal(module.final_state["decision"], "end", "the graph stopped on the end branch")

    h.write_json("result.json", {
        "iterations": module.final_state["iterations"],
        "final_title": module.final_state["generation"],
    })
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 1 (cyclic graph)", FILES).crash())
