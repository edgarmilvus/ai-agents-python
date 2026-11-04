"""Harness for the two-stage optimised pipeline.

The listing calls a real endpoint twice: once for compressing the feedback, once for
the structured extraction. The harness replaces `OpenAI` with a fake that answers
both calls with fixed usage numbers, so the accounting and the schema handling are
exercised without a key.
"""
import contextlib
import io
import json
import os
import pathlib
import runpy
import sys

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness  # noqa: E402

import openai  # noqa: E402


class Usage:
    def __init__(self, prompt_tokens, completion_tokens):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens


class Message:
    def __init__(self, content=None, parsed=None):
        self.content = content
        self.parsed = parsed


class Choice:
    def __init__(self, message):
        self.message = message


class Response:
    def __init__(self, message, usage):
        self.choices = [Choice(message)]
        self.usage = usage


EXTRACTED = {
    "key_sentiment": "Mixed",
    "top_pain_point": "The interface is confusing and the search returns nothing useful.",
    "actionable_recommendations": ["Simplify the settings menu", "Fix peak-hour latency",
                                   "Repair mobile uploads"],
    "token_optimization_status": True,
}


class Completions:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(("create", kwargs))
        if kwargs.get("response_format") == {"type": "json_object"}:
            # The extraction step: a JSON object, validated by the listing.
            return Response(Message(content=json.dumps(EXTRACTED)), Usage(180, 60))
        return Response(
            Message(content="Users find the interface confusing, latency is high, "
                            "mobile uploads crash, but support is excellent."),
            Usage(1000, 120),
        )


class Chat:
    def __init__(self, completions):
        self.completions = completions


class FakeOpenAI:
    instances = []

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.completions = Completions()
        self.chat = Chat(self.completions)
        FakeOpenAI.instances.append(self)


def main():
    h = Harness("example 2 (optimized pipeline)", FILES)
    # The assertion below is about the *default* endpoint, so the listing has to
    # be read with a clean environment: a caller who exported the three variables
    # — which is how the live run is invoked — would otherwise hide the default.
    for name in ("OPENAI_COMPATIBLE_BASE_URL", "OPENAI_COMPATIBLE_MODEL",
                 "OPENAI_COMPATIBLE_API_KEY"):
        os.environ.pop(name, None)
    os.environ["OPENAI_COMPATIBLE_API_KEY"] = "harness-placeholder"
    openai.OpenAI = FakeOpenAI

    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        runpy.run_path(str(FILES / "01_optimized_pipeline.py"), run_name="__main__")
    printed = stdout.getvalue() + stderr.getvalue()

    client = FakeOpenAI.instances[0]
    h.equal(client.kwargs["base_url"].startswith("https://openrouter.ai"), True,
            "the client points at the OpenAI-compatible gateway")
    h.equal([name for name, _ in client.completions.calls], ["create", "create"],
            "one compression call, then one JSON call")

    h.contains(printed, "Context Compression Phase", "the compression step ran")
    h.contains(printed, "Initial Raw Context Tokens: 1000", "the compression usage is reported")
    h.contains(printed, "Compressed Summary Tokens Used: 120", "the compressed length is reported")
    h.contains(printed, "Structured Extraction Phase", "the extraction step ran")
    h.contains(printed, "Extraction Prompt Tokens (Optimized Context): 180",
               "the extraction ran on the shorter context")
    h.contains(printed, "key_sentiment", "the structured output is printed")
    h.contains(printed, "token_optimization_status", "the schema's marker field is present")
    h.contains(printed, "Total Prompt Tokens (Input Cost): 1180", "usage accumulates across steps")
    h.contains(printed, "Total Completion Tokens (Output Cost): 180", "completion tokens accumulate")

    h.write_json("result.json", {"calls": len(client.completions.calls)})
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 2 (optimized pipeline)", FILES).crash())
