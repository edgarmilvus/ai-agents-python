"""Harness for exercise 3: research runs persisted to SQLite.

The listing writes to a file, so the harness runs it from `output/` and then reads
the database back — the same thing the script's own verification does, but as an
assertion.
"""
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
    h = Harness("exercise 3 (persistent logging)", FILES)
    output = FILES.parent / "output"
    output.mkdir(parents=True, exist_ok=True)
    previous = os.getcwd()
    os.chdir(output)
    try:
        # The script appends to its database, so each harness run starts fresh;
        # the engine must be disposed before the file is reopened.
        stale = output / "agent_runs.db"
        if stale.exists():
            stale.unlink()
        log = io.StringIO()
        with contextlib.redirect_stdout(log):
            module = load_listing(FILES / "02_exercise_3_persistent_logging.py", "persistent")
            for topic, role in [
                ("Future of Quantum Computing in Finance", "Senior Market Analyst"),
                ("Ethical Implications of Large Language Models", "AI Ethics Researcher"),
                ("Global Supply Chain Resilience Post-2024", "Logistics Strategist"),
            ]:
                module.persist_research_log(topic, role, f"# Research Report on {topic}\n\nBody.")
        printed = log.getvalue()

        h.contains(printed, "Successfully logged research run",
                   "each run reports a successful write")
        h.check("Database error" not in printed, "no insert failed")

        session = module.SessionLocal()
        try:
            rows = session.query(module.ResearchLog).all()
            h.equal(len(rows), 3, "three runs are stored")
            h.check(all(row.summary_snippet for row in rows), "every row keeps a snippet")
            h.contains(rows[0].query_topic, "Quantum", "the topic is persisted")
        finally:
            session.close()

        h.write_json("result.json", {"rows": 3, "database": module.DATABASE_FILE})
    finally:
        os.chdir(previous)
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("exercise 3 (persistent logging)", FILES).crash())
