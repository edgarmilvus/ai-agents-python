"""Harness for exercise 4: a planning layer in front of the RAG call.

The planner decides two things, and both are checkable: whether retrieval is
needed at all, and what query the retriever receives when it is.
"""
import contextlib
import io
import json
import pathlib
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402

SIMPLE = "What is the capital of France?"
COMPLEX = "What is the history of the early development of Python's GIL?"
UNKNOWN = "Compare and contrast event loops and threads."


def plan_with_capture(listing, query):
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        result = listing.simulate_llm_planning(query)
    return result, buffer.getvalue()


def run_with_capture(listing, query):
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        result = listing.run_planning_agent(query)
    return result, buffer.getvalue()


def main():
    h = Harness("exercise 4 (planning layer)", FILES)
    listing = load_listing(FILES / "01_planning_layer_rag.py", "planning_rag")

    simple, log = plan_with_capture(listing, SIMPLE)
    h.equal(set(simple), {"search_required", "refined_query"},
            "the planner returns exactly the two agreed keys")
    h.equal(simple["search_required"], False, "a direct question needs no retrieval")
    h.equal(simple["refined_query"], SIMPLE,
            "a query that needs no search is passed through unchanged")
    printed = json.loads(log.split("]: ", 1)[1].strip())
    h.equal(printed, simple, "what the planner prints is what it returns")

    complex_plan, _ = plan_with_capture(listing, COMPLEX)
    h.equal(complex_plan["search_required"], True, "a history question needs retrieval")
    h.equal(complex_plan["refined_query"], "the early development of Python's GIL?",
            "the refinement strips the conversational prefix")
    h.check(not complex_plan["refined_query"].lower().startswith("what is"),
            "the refined query carries no question boilerplate")
    h.check(len(complex_plan["refined_query"]) < len(COMPLEX),
            "refinement shortens the query")

    unknown, _ = plan_with_capture(listing, UNKNOWN)
    h.equal(unknown["search_required"], True, "an unrecognised query defaults to retrieval")

    direct, direct_log = run_with_capture(listing, SIMPLE)
    h.contains(direct, "Direct Answer Result", "the simple query bypasses RAG")
    h.contains(direct_log, "RAG NOT required", "the Decide phase says why RAG was skipped")

    grounded, grounded_log = run_with_capture(listing, COMPLEX)
    h.contains(grounded, "RAG Result", "the complex query goes through RAG")
    h.contains(grounded_log, "search using refined query: 'the early development",
               "the RAG call receives the refined query, not the raw one")
    h.check("vector store" in grounded_log, "the retriever is actually exercised")

    h.write_json("planning.json", {
        "simple": simple,
        "complex": complex_plan,
        "unknown": unknown,
        "direct_answer": direct,
        "rag_answer": grounded,
    })
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 4 (planning layer)", FILES).crash())
