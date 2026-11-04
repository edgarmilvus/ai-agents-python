"""Harness for the basic agentic loop.

The listing talks to the OpenAI API, so the harness stands a scripted client in
front of it: nothing leaves the machine, the decisions are known in advance, and
the assertions can check what the loop actually sent back to the model on each
turn.
"""
import json
import os
import pathlib
import sys
import types
from types import SimpleNamespace

FILES = pathlib.Path(__file__).resolve().parent
ROOT = FILES.parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from harness import Harness, load_listing  # noqa: E402

DECISIONS = [
    {"next_action": "Search the capital city of Brazil", "goal_achieved": False},
    {"next_action": "Search the year Brasília was officially founded", "goal_achieved": False},
    {
        "next_action": "Brasília, the capital city of Brazil, was officially founded on April 21, 1960.",
        "goal_achieved": True,
    },
]
EXECUTIONS = [
    "The capital city of Brazil is Brasília.",
    "Brasília was officially founded on April 21, 1960.",
]


class FakeCompletions:
    """Records every call and answers from a script instead of the network."""

    def __init__(self):
        self.decision_calls = []
        self.execution_calls = []
        self._decisions = []
        self._executions = []

    def set_script(self, decisions, executions):
        self._decisions = [json.dumps(item) for item in decisions]
        self._executions = list(executions)

    def create(self, model, messages, **kwargs):
        if kwargs.get("response_format", {}).get("type") == "json_object":
            self.decision_calls.append({"model": model, "messages": messages, **kwargs})
            payload = self._decisions.pop(0) if self._decisions else json.dumps(
                {"next_action": "no further steps", "goal_achieved": True}
            )
        else:
            self.execution_calls.append({"model": model, "messages": messages})
            payload = self._executions.pop(0) if self._executions else "unknown"
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=payload))]
        )


COMPLETIONS = FakeCompletions()
CLIENT_INIT = []


class OpenAI:
    """Minimal stand-in for openai.OpenAI: one client, one chat namespace."""

    def __init__(self, *args, **kwargs):
        CLIENT_INIT.append({"args": args, "kwargs": kwargs})
        self.chat = SimpleNamespace(completions=COMPLETIONS)


def install_fake_openai():
    module = types.ModuleType("openai")
    module.OpenAI = OpenAI
    sys.modules["openai"] = module


def text_of(call):
    return "\n".join(message["content"] for message in call["messages"])


def main():
    h = Harness("example 1 (agentic loop)", FILES)
    # The assertions below are about the *defaults*. A caller who exported the
    # three variables — which is exactly how the live run is invoked — would hide
    # them, so the harness reads the module with a clean environment.
    for name in ("OPENAI_COMPATIBLE_BASE_URL", "OPENAI_COMPATIBLE_MODEL",
                 "OPENAI_COMPATIBLE_API_KEY"):
        os.environ.pop(name, None)

    install_fake_openai()
    COMPLETIONS.set_script(DECISIONS, EXECUTIONS)
    listing = load_listing(FILES / "01_agentic_loop_research.py", "agentic_loop_research")

    # Importing the module must not start an agent: the entry point is guarded.
    h.equal(len(COMPLETIONS.decision_calls) + len(COMPLETIONS.execution_calls), 0,
            "importing the listing makes no model call")

    # The provider is configuration, not code: the endpoint and model default to
    # OpenRouter and DeepSeek V4.1 Flash, and the key comes from the environment.
    h.equal(listing.BASE_URL, "https://openrouter.ai/api/v1",
            "the base URL defaults to OpenRouter")
    h.equal(listing.MODEL, "~deepseek/deepseek-flash-latest",
            "the model defaults to DeepSeek V4.1 Flash")
    h.equal(CLIENT_INIT[-1]["kwargs"].get("base_url"), listing.BASE_URL,
            "the client is built with the configured base URL")
    h.check("api_key" in CLIENT_INIT[-1]["kwargs"],
            "the client reads the key from the environment")

    os.environ["OPENAI_COMPATIBLE_MODEL"] = "~deepseek/deepseek-v4-flash-latest"
    overridden = load_listing(
        FILES / "01_agentic_loop_research.py", "agentic_loop_research_override"
    )
    h.equal(overridden.MODEL, "~deepseek/deepseek-v4-flash-latest",
            "OPENAI_COMPATIBLE_MODEL overrides the default model")
    del os.environ["OPENAI_COMPATIBLE_MODEL"]

    summary = listing.run_agentic_loop(listing.PRIMARY_GOAL)

    h.equal(summary, DECISIONS[2]["next_action"], "the loop returns the final synthesis")
    h.contains(summary, "1960", "the returned summary carries the founding year")
    h.equal(len(listing.ACTION_HISTORY), 3, "three decisions were recorded")
    h.equal([step["iteration"] for step in listing.ACTION_HISTORY], ["1", "2", "3"],
            "history is numbered by iteration")
    h.equal(len(COMPLETIONS.decision_calls), 3, "one planning call per iteration")
    h.equal(len(COMPLETIONS.execution_calls), 2, "two execution calls, none after the goal")
    h.equal(COMPLETIONS.decision_calls[0]["model"], listing.MODEL,
            "the planning call uses the module's model constant")
    h.check(all(call.get("response_format") == {"type": "json_object"}
                for call in COMPLETIONS.decision_calls),
            "every planning call asks for a JSON object")
    h.contains(text_of(COMPLETIONS.decision_calls[1]), "Brasília",
               "iteration 2 observes the result of iteration 1")
    h.contains(text_of(COMPLETIONS.decision_calls[2]), "April 21, 1960",
               "iteration 3 observes the result of iteration 2")

    # The bound on the loop is the safeguard against a model that never stops.
    COMPLETIONS.decision_calls.clear()
    COMPLETIONS.execution_calls.clear()
    COMPLETIONS.set_script(
        [{"next_action": "Keep looking", "goal_achieved": False}],
        ["nothing yet"],
    )
    failure = listing.run_agentic_loop(listing.PRIMARY_GOAL, max_iterations=1)
    h.contains(failure, "failed to achieve goal within 1 iterations",
               "an unreachable goal ends at the iteration limit")

    # A second run starts from empty memory instead of inheriting the first.
    COMPLETIONS.decision_calls.clear()
    COMPLETIONS.execution_calls.clear()
    COMPLETIONS.set_script(DECISIONS, EXECUTIONS)
    listing.run_agentic_loop(listing.PRIMARY_GOAL)
    h.equal(len(listing.ACTION_HISTORY), 3, "a second run starts from empty memory")

    h.write_json("trace.json", {
        "goal": listing.PRIMARY_GOAL,
        "decisions": [item["next_action"] for item in DECISIONS],
        "execution_results": EXECUTIONS,
        "final": summary,
    })
    return h.report()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(Harness("example 1 (agentic loop)", FILES).crash())
