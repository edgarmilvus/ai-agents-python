"""Harness for exercise 3: one tool instance, four prompts, one state.

The point of the exercise is that state lives on the tool, not in the agent, so
the harness reads the cart after each prompt instead of trusting the printed text.
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
    h = Harness("exercise 3 (state-aware tools)", FILES)
    ns, printed = compose(FILES / "01_state_aware_tools.py")

    h.contains(ns["response1"], "Added 2 x Apple", "the first prompt adds two apples")
    h.contains(ns["response2"], "Added 1 x Banana",
               "the second prompt adds a banana in different words")
    h.contains(ns["response3"], "2 x Apple", "the view prompt sees both items")
    h.contains(ns["response3"], "1 x Banana", "the view prompt is not limited to the last add")
    h.contains(ns["response4"], "3 items", "checkout counts the whole cart")
    h.equal(ns["persistent_cart"].items, [], "checkout clears the state that survived three prompts")
    h.equal(len([line for line in printed.splitlines() if "User:" in line]), 4,
            "four prompts were processed")

    h.write_json("result.json", {
        "responses": [ns["response1"], ns["response2"], ns["response3"], ns["response4"]],
        "cart_after_checkout": ns["persistent_cart"].items,
    })
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 3 (state-aware tools)", FILES).crash())
