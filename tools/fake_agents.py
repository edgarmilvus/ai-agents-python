"""A chat fake that can bind tools and then call them.

`FakeListChatModel` cannot stand in for a tool-calling agent: `bind_tools` raises,
and a plain text answer is never a tool call, so the executor would either fail or
answer without touching a tool. This fake accepts the binding, replays a scripted
list of `(tool_name, arguments)` pairs, and only then returns a final answer.

The plan is the harness's; the prompt, the tools and the agent loop stay the
listing's.
"""
from typing import Any, Dict, List, Optional, Tuple

from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage


class ScriptedToolChat(FakeMessagesListChatModel):
    responses: List[Any] = []
    plan: List[Tuple[str, Dict[str, Any]]] = []
    answer: str = "Done."

    def bind_tools(self, tools, **kwargs):
        names = {tool.name for tool in tools}
        steps = [(name, args) for name, args in self.plan if name in names]
        if not steps:
            # The harness scripted the whole conversation itself.
            return self
        messages: List[AIMessage] = [
            AIMessage(content="", tool_calls=[{"name": name, "args": args,
                                               "id": f"call-{index}"}])
            for index, (name, args) in enumerate(steps)
        ]
        messages.append(AIMessage(content=self.answer))
        self.responses = messages
        self.i = 0
        return self


def text_model(text: str, plan: Optional[List[Tuple[str, Dict[str, Any]]]] = None,
               answer: str = "Done.") -> ScriptedToolChat:
    """A fake that answers with `text`, and calls tools if the agent binds any."""
    model = ScriptedToolChat(responses=[AIMessage(content=text)], plan=plan or [],
                             answer=answer)
    return model
