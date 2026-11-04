"""Harness for the basic RAG pipeline.

The listing builds real embedding and chat clients, so the harness swaps both
classes for fakes before importing it; the loader, the splitter, the vector store
and the retrieval chain are the listing's own.
"""
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

ANSWER = "The policy allows 50,000 tokens per hour per agent, and keys must be rotated every 30 days."


def main():
    h = Harness("example 1 (basic RAG)", FILES)
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
                "basic_rag", str(FILES / "01_context_window_rag.py"))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        printed = log.getvalue()

        h.contains(printed, "Original document split into", "the policy was loaded and chunked")
        h.contains(printed, "Vector store indexing complete", "the chunks were embedded and stored")
        h.contains(printed, "RAG Query", "a query was issued")
        h.contains(printed, "RAG Response", "the chain answered")
        h.contains(printed, "tokens per hour", "the answer is the scripted model's")
        h.check(isinstance(module.llm, FakeListChatModel),
                "the chat client is the fake, not a network client")

        h.write_json("result.json", {"answer": ANSWER, "chunks": printed.count("chunk")})
    finally:
        os.chdir(previous)
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 1 (basic RAG)", FILES).crash())
