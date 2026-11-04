"""The twelve rules of the book, as data and as checks.

One rule, one failure it prevents, one chapter that explains it. The appendix in
the book is generated from this file, so prose and behaviour cannot drift.
"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass

MODEL_CALLS = (
    ".create(", ".invoke(", ".ainvoke(", ".kickoff(", ".run(", ".generate(",
    ".complete(", ".chat(", " acompletion(",
)
MODEL_NAMES = ("OpenAI", "ChatOpenAI", "ChatGoogle", "LLM(", "Crew(", "Agent(", "client.chat")

TRACE_MARKERS = ("@traceable", "langsmith", "LANGCHAIN_TRACING", "LANGSMITH_TRACING",
                 "traceable(", "RunTree", "tracing_v2")
SCHEMA_MARKERS = ("BaseModel", "response_format", "model_validate", "model_validate_json",
                  "BaseSettings", "schema()", "output_pydantic", "output_json")
BOUNDARY_MARKERS = ("requests", "httpx", "fastapi", "FastAPI", "upload", "urlopen",
                    "socket", "aiohttp")


@dataclass(frozen=True)
class Rule:
    id: str
    chapter: int
    title: str
    message: str
    wrong: str
    right: str


RULES = [
    Rule("budget", 17, "No budget around the model loop",
         "A loop calls the model with nothing that bounds calls, tokens or time.",
         "while True:\n    answer = llm.invoke(messages)",
         "for _ in range(MAX_STEPS):\n    if spent_usd > BUDGET: raise BudgetExceeded"),
    Rule("exit", 8, "No exit condition",
         "`while True` never breaks, returns or raises: the loop can only be killed.",
         "while True:\n    step()",
         "while not done:\n    done = step()"),
    Rule("untyped-tool", 3, "Tool without a typed contract",
         "A tool is exposed to the model without annotations or with **kwargs.",
         "@tool\ndef search(q): ...", "@tool\ndef search(query: str) -> str: ..."),
    Rule("silent-except", 12, "Exception swallowed",
         "The handler does nothing: the failure disappears and the loop goes on.",
         "try:\n    run()\nexcept Exception:\n    pass",
         "except Exception as exc:\n    log.warning('run failed: %s', exc)\n    raise"),
    Rule("sync-io-in-async", 13, "Blocking I/O inside async code",
         "A coroutine calls blocking I/O directly: the event loop stops for everyone.",
         "async def gate():\n    return input('approve? ')",
         "async def gate():\n    return await asyncio.to_thread(input, 'approve? ')"),
    Rule("pickle-boundary", 10, "Pickle crossing a boundary",
         "A checkpoint format is used in a module that also talks to the network.",
         "pickle.loads(request.body)", "payload = json.loads(request.body)"),
    Rule("unbounded-memory", 1, "Memory with no bound",
         "History is appended on every turn and never trimmed: the window fills.",
         "history.append(turn)", "history.append(turn)\nhistory = history[-WINDOW:]"),
    Rule("shell-injection", 15, "Shell built from a string",
         "Generated text reaches a shell: the sandbox becomes a command line.",
         "subprocess.run(f'python {code}', shell=True)", "subprocess.run([sys.executable, path])"),
    Rule("no-trace", 16, "Tracing on, project unnamed",
         "Tracing is enabled but no project name is set: the runs land somewhere nobody opens.",
         'os.environ["LANGCHAIN_TRACING_V2"] = "true"',
         'os.environ["LANGCHAIN_TRACING_V2"] = "true"\nos.environ["LANGCHAIN_PROJECT"] = "agent-demo"'),
    Rule("prose-contract", 19, "Contract read out of prose",
         "The answer is parsed with regex or split instead of a schema.",
         "score = float(re.search(r'Score: (\\d+)', reply).group(1))",
         "result = Reply.model_validate_json(reply)\nscore = result.score"),
    Rule("retry-logical", 12, "One retry policy for every failure",
         "The loop retries whatever raised, including failures that cannot change.",
         "for _ in range(3):\n    try: call()\n    except Exception: continue",
         "if isinstance(exc, NotFound): replan()\nelse: retry()"),
    Rule("string-handoff", 20, "Free text between agents",
         "An agent hands its result to another agent as a string, not a contract.",
         "class WriterAgent:\n    def run(self) -> str: ...",
         "class WriterAgent:\n    def run(self) -> Draft: ..."),
]


# -- helpers -------------------------------------------------------------

def _strip(node) -> ast.AST:
    return node


def _walk_calls(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            yield node


def _call_name(node: ast.Call) -> str:
    func = node.func
    parts = []
    while isinstance(func, ast.Attribute):
        parts.append(func.attr)
        func = func.value
    if isinstance(func, ast.Name):
        parts.append(func.id)
    return ".".join(reversed(parts))


def _is_model_call(node: ast.Call) -> bool:
    name = _call_name(node)
    return any(marker.strip(". ") in name for marker in MODEL_CALLS) or \
        any(m in name for m in ("chat.completions", "invoke", "kickoff", "ainvoke"))


def _findings(rule, path, line, detail=""):
    return {"rule": rule.id, "chapter": rule.chapter, "path": str(path),
            "line": line, "title": rule.title,
            "message": rule.message if not detail else f"{rule.message} ({detail})"}


def _in_async(node, parents):
    parent = parents.get(id(node))
    while parent is not None:
        if isinstance(parent, ast.AsyncFunctionDef):
            return True
        if isinstance(parent, (ast.FunctionDef,)):
            return False
        parent = parents.get(id(parent))
    return False


def _parents(tree):
    table = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            table[id(child)] = node
    return table


def _is_wrapped_in_thread(node, parents):
    parent = parents.get(id(node))
    while parent is not None:
        if isinstance(parent, ast.Call) and _call_name(parent) in (
                "asyncio.to_thread", "asyncio.get_running_loop", "run_in_executor"):
            return True
        parent = parents.get(id(parent))
    return False


# -- the twelve checks ---------------------------------------------------

def check_budget(tree, src, path):
    parents = _parents(tree)
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.While, ast.For)):
            continue
        body_calls = [c for stmt in node.body for c in ast.walk(stmt) if isinstance(c, ast.Call)]
        if not any(_is_model_call(c) for c in body_calls):
            continue
        scope = parents.get(id(node))
        while scope is not None and not isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef)):
            scope = parents.get(id(scope))
        guards = ("budget", "timeout", "max_iter", "max_steps", "deadline", "max_calls")
        names = set()
        for n in ast.walk(scope) if scope else []:
            if isinstance(n, ast.Name):
                names.add(n.id.lower())
            if isinstance(n, ast.arg):
                names.add(n.arg.lower())
        if not any(g in name for name in names for g in guards):
            out.append(_findings(RULE_BY_ID["budget"], path, node.lineno))
    return out


def check_exit(tree, src, path):
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.While):
            continue
        if not (isinstance(node.test, ast.Constant) and node.test.value is True):
            continue
        exits = [n for stmt in node.body for n in ast.walk(stmt)
                 if isinstance(n, (ast.Break, ast.Return, ast.Raise))]
        awaits = [n for stmt in node.body for n in ast.walk(stmt)
                  if isinstance(n, ast.Await)]
        if awaits:
            continue                      # cancellable: the exit is the task, not the body
        if not exits:
            out.append(_findings(RULE_BY_ID["exit"], path, node.lineno))
    return out


def check_untyped_tool(tree, src, path):
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        decorated = any(
            (isinstance(d, ast.Name) and d.id == "tool") or
            (isinstance(d, ast.Call) and _call_name(d).split(".")[-1] == "tool")
            for d in node.decorator_list)
        if not decorated:
            continue
        args = [a for a in node.args.args if a.arg not in ("self", "cls")]
        missing = [a.arg for a in args if a.annotation is None]
        if missing or node.args.kwarg is not None:
            detail = "no annotation: " + ", ".join(missing) if missing else "**kwargs"
            out.append(_findings(RULE_BY_ID["untyped-tool"], path, node.lineno, detail))
    return out


def check_silent_except(tree, src, path):
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ExceptHandler):
            continue
        body = [s for s in node.body if not (isinstance(s, ast.Expr)
                and isinstance(s.value, ast.Constant))]
        if not body and (node.type is None or isinstance(node.type, ast.Name)):
            out.append(_findings(RULE_BY_ID["silent-except"], path, node.lineno, "empty handler"))
            continue
        generic = node.type is None or (isinstance(node.type, ast.Name)
                                        and node.type.id in ("Exception", "BaseException"))
        if len(body) == 1 and isinstance(body[0], ast.Pass) and generic:
            out.append(_findings(RULE_BY_ID["silent-except"], path, node.lineno))
    return out


def check_sync_io(tree, src, path):
    parents = _parents(tree)
    blocking = {"input", "sleep", "open", "system", "urlopen"}
    out = []
    for node in _walk_calls(tree):
        if not _in_async(node, parents):
            continue
        if _is_wrapped_in_thread(node, parents):
            continue
        name = _call_name(node)
        leaf = name.split(".")[-1]
        blocked_api = any(name.startswith(p) for p in
                          ("requests.", "httpx.", "sqlite3.connect", "urllib.request."))
        if leaf not in blocking and not blocked_api:
            continue
        if "asyncio" in name or "to_thread" in name:
            continue
        out.append(_findings(RULE_BY_ID["sync-io-in-async"], path, node.lineno, name))
    return out


def check_pickle_boundary(tree, src, path):
    uses = "pickle.dump" in src or "pickle.load" in src or "pickle.dumps" in src
    boundary = any(m in src for m in BOUNDARY_MARKERS)
    if uses and boundary:
        line = src[:src.index("pickle.")].count("\n") + 1
        return [_findings(RULE_BY_ID["pickle-boundary"], path, line)]
    return []


MEMORY_WORDS = ("history", "memory", "messages", "context", "conversation",
                "transcript", "turns", "scratchpad")


def check_unbounded_memory(tree, src, path):
    """Only a structure that is *sent to the model* can overflow the window."""
    appends = [n for n in ast.walk(tree)
               if isinstance(n, ast.Call) and _call_name(n).endswith("append")
               and isinstance(n.func, ast.Attribute)]
    if not appends:
        return []
    bounded = ("maxlen" in src or re.search(r"\[-\s*\w+\s*:\]", src) or "pop(0)" in src
               or "deque(" in src)
    if bounded:
        return []
    sent = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _is_model_call(node):
            for arg in list(node.args) + [k.value for k in node.keywords]:
                for sub in ast.walk(arg):
                    if isinstance(sub, ast.Name):
                        sent.add(sub.id.lower())
        if isinstance(node, ast.JoinedStr) or (isinstance(node, ast.Call) and
                                               _call_name(node).endswith(("format", "join"))):
            for sub in ast.walk(node):
                if isinstance(sub, ast.Name):
                    sent.add(sub.id.lower())
    for node in appends:
        name = node.func.value.id.lower() if isinstance(node.func.value, ast.Name) else ""
        if not name or not any(w in name for w in MEMORY_WORDS):
            continue
        if name not in sent:
            continue
        return [_findings(RULE_BY_ID["unbounded-memory"], path, node.lineno,
                          f"{name} appended and sent, never trimmed")]
    return []


def check_shell_injection(tree, src, path):
    out = []
    for node in _walk_calls(tree):
        name = _call_name(node)
        if name.startswith(("subprocess.", "os.system", "os.popen")):
            shell = any(k.arg == "shell" and isinstance(k.value, ast.Constant) and k.value.value is True
                        for k in node.keywords)
            dynamic = any(isinstance(a, (ast.JoinedStr, ast.BinOp)) or
                          (isinstance(a, ast.Call) and _call_name(a) in ("format",)) or
                          (isinstance(a, ast.Name) and a.id not in ("sys",))
                          for a in node.args)
            if shell or (name.startswith(("os.system", "os.popen")) and dynamic):
                out.append(_findings(RULE_BY_ID["shell-injection"], path, node.lineno, name))
    return out


def check_no_trace(tree, src, path):
    """The chapter 16 pitfall: tracing that writes to a project nobody defined."""
    enabled = any(m in src for m in ("LANGCHAIN_TRACING_V2", "LANGSMITH_TRACING"))
    named = any(m in src for m in ("LANGCHAIN_PROJECT", "LANGSMITH_PROJECT",
                                  "project_name", "project="))
    if enabled and not named:
        line = next((i + 1 for i, l in enumerate(src.splitlines())
                     if "TRACING_V2" in l or "LANGSMITH_TRACING" in l), 1)
        return [_findings(RULE_BY_ID["no-trace"], path, line, "no project name")]
    return []


def check_prose_contract(tree, src, path):
    """A model answer that code then parses by hand instead of by schema."""
    if any(m in src for m in SCHEMA_MARKERS):
        return []
    # names that hold a model answer
    answers = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            text = ast.get_source_segment(src, node.value) or ""
            if ".content" in text or "choices" in text:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        answers.add(target.id)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and \
                node.func.attr == "get" and node.args and isinstance(node.args[0], ast.Constant):
            # reply.get("content") style
            pass
    if not answers:
        return []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node)
        is_regex = name.startswith("re.") and name.split(".")[-1] in ("search", "match", "findall")
        is_split = isinstance(node.func, ast.Attribute) and node.func.attr == "split"
        if not (is_regex or is_split):
            continue
        used = {n.id for arg in list(node.args) + [k.value for k in node.keywords]
                for n in ast.walk(arg) if isinstance(n, ast.Name)}
        if used & answers:
            return [_findings(RULE_BY_ID["prose-contract"], path, node.lineno,
                              f"parsing {', '.join(sorted(used & answers))}")]
    return []


def check_retry_logical(tree, src, path):
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.For, ast.While)):
            continue
        if isinstance(node, ast.For):
            it = node.iter
            is_range = isinstance(it, ast.Call) and _call_name(it) == "range"
            if not is_range:
                continue                  # a loop over items, not a retry
        has_try = any(isinstance(n, ast.Try) for stmt in node.body for n in ast.walk(stmt))
        if not has_try:
            continue
        generic = any(isinstance(h, ast.ExceptHandler) and
                      (h.type is None or (isinstance(h.type, ast.Name) and h.type.id == "Exception"))
                      and any(isinstance(x, (ast.Continue, ast.Pass))
                              for x in h.body)
                      for stmt in node.body for n in ast.walk(stmt) if isinstance(n, ast.Try)
                      for h in n.handlers)
        if generic and "HTTPStatus" not in src and "status_code" not in src and "isinstance(" not in src:
            out.append(_findings(RULE_BY_ID["retry-logical"], path, node.lineno))
    return out


def check_string_handoff(tree, src, path):
    agents = [n for n in ast.walk(tree)
              if isinstance(n, ast.ClassDef) and "Agent" in n.name]
    if len(agents) < 2:
        return []
    out = []
    fed = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            for arg in node.args:
                if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Attribute):
                    fed.add(arg.func.attr)
    for cls in agents:
        for node in cls.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                ret = node.returns
                if isinstance(ret, ast.Name) and ret.id == "str" and node.name in fed:
                    out.append(_findings(RULE_BY_ID["string-handoff"], path, node.lineno,
                                         f"{cls.name}.{node.name}() -> str, passed to another agent"))
    return out


RULE_BY_ID = {r.id: r for r in RULES}

CHECKS = {
    "budget": check_budget,
    "exit": check_exit,
    "untyped-tool": check_untyped_tool,
    "silent-except": check_silent_except,
    "sync-io-in-async": check_sync_io,
    "pickle-boundary": check_pickle_boundary,
    "unbounded-memory": check_unbounded_memory,
    "shell-injection": check_shell_injection,
    "no-trace": check_no_trace,
    "prose-contract": check_prose_contract,
    "retry-logical": check_retry_logical,
    "string-handoff": check_string_handoff,
}


def audit_source(path, source, enabled=None):
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [{"rule": "parse", "chapter": 0, "path": str(path),
                 "line": exc.lineno or 0, "title": "File does not parse",
                 "message": str(exc)}]
    findings = []
    for rule_id, check in CHECKS.items():
        if enabled and rule_id not in enabled:
            continue
        findings.extend(check(tree, source, path))
    return findings
