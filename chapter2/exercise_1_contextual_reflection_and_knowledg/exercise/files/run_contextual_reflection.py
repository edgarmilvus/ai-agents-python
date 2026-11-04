"""Harness for exercise 1: reflection driven by retrieved best practices.

The book publishes this solution as a listing that assumes the chapter's
boilerplate, so the harness composes the two published blocks exactly as they
are, in the order the book describes, and asserts on the objects the demo leaves
behind.
"""
import contextlib
import io
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness  # noqa: E402

CHAPTER = ROOT / "chapter2"
BOILERPLATE = (CHAPTER / "boilerplate_code_for_exercises/example/files"
               / "01_boilerplate_code_for_exercises.py")


def compose(solution: pathlib.Path):
    source = BOILERPLATE.read_text() + "\n\n" + solution.read_text()
    namespace = {"__name__": "__main__"}
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        exec(compile(source, str(solution), "exec"), namespace)
    return namespace, log.getvalue()


def main():
    h = Harness("exercise 1 (contextual reflection)", FILES)
    ns, printed = compose(FILES / "01_contextual_reflection_agent.py")

    h.contains(ns["response1"], "80% complete", "a status question is answered directly")
    h.contains(ns["response2"], "80% complete", "a second plain turn is answered directly")
    h.check("risk" in ns["response3"].lower() or "practice" in ns["response3"].lower(),
            "the risk question is answered from retrieved practices")
    h.contains(printed, "Risk keywords detected", "the agent decided to call the reflector")
    h.contains(printed, "Retrieved Best Practices", "the tool returned retrieved documents")
    h.check(len(ns["memory"].history) <= 5, "short-term memory keeps at most five turns")
    h.equal(len(ns["memory"].history), 5, "the demo fills the window exactly")
    h.contains(ns["memory"].get_history(), "dependency hell",
               "the risk question is the newest remembered turn")

    h.write_json("result.json", {
        "responses": [ns["response1"], ns["response2"], ns["response3"]],
        "memory_turns": len(ns["memory"].history),
    })
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 1 (contextual reflection)", FILES).crash())
