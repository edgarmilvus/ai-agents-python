"""Harness for the corporate strategy analyst: retrieval over project history."""
import contextlib
import io
import os
import pathlib
import sys
import warnings

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness  # noqa: E402

import langchain_openai  # noqa: E402
import langchain_classic.memory  # noqa: E402,F401
from langchain_core.embeddings import FakeEmbeddings  # noqa: E402
from langchain_core.language_models.fake_chat_models import FakeListChatModel  # noqa: E402

ANSWER = "Project Gamma had the largest overrun; its key dependency was the GPU cluster."


def main():
    h = Harness("example 2 (strategy analyst)", FILES)
    warnings.simplefilter("ignore")
    os.environ.setdefault("OPENAI_COMPATIBLE_API_KEY", "harness-placeholder")
    langchain_openai.OpenAIEmbeddings = lambda **kwargs: FakeEmbeddings(size=8)
    langchain_openai.ChatOpenAI = lambda **kwargs: FakeListChatModel(responses=[ANSWER])

    output = FILES.parent / "output"
    output.mkdir(parents=True, exist_ok=True)
    previous = os.getcwd()
    os.chdir(output)
    try:
        log = io.StringIO()
        with contextlib.redirect_stdout(log), contextlib.redirect_stderr(io.StringIO()):
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "strategy_rag", str(FILES / "01_strategy_analyst_rag.py"))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        printed = log.getvalue()

        h.contains(printed, "Indexing 5 document chunks", "the project history was indexed")
        h.contains(printed, "Agent Query", "a query was issued")
        h.contains(printed, "Agent Response", "the agent answered")
        h.contains(printed, "Retrieved Sources", "the retrieved chunks are shown")
        h.contains(printed, "Project Gamma", "a retrieved source is quoted")
        h.contains(printed, "Cleaned up vector store", "the demo cleans its vector store")
        leftover = output / "chroma_db_hippocampus"
        h.check(not leftover.exists() or os.name == "nt",
                "no vector store is left behind (Windows keeps the handles open)")

        h.write_json("result.json", {"answer": ANSWER})
    finally:
        os.chdir(previous)
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 2 (strategy analyst)", FILES).crash())
