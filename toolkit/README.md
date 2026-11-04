# toolkit

Two things the book describes and does not ship: a check for the twelve failures
it catalogues, and a way to test an agent offline.

```bash
pip install ./toolkit          # from the repository root
agent-audit .                  # audit a tree
agent-audit . --list           # the twelve rules, with their chapter
agent-audit . --json           # machine-readable, for CI
```

Exit code is 1 when anything is found, so it drops into CI unchanged.

| rule | chapter | what it catches |
| --- | --- | --- |
| `unbounded-memory` | 1 | history appended and sent to the model, never trimmed |
| `untyped-tool` | 3 | a tool exposed without annotations, or with `**kwargs` |
| `exit` | 8 | `while True` with no break, return or raise |
| `pickle-boundary` | 10 | a checkpoint format in a module that also talks to the network |
| `silent-except` | 12 | `except Exception: pass` |
| `retry-logical` | 12 | one retry policy for every failure |
| `sync-io-in-async` | 13 | blocking I/O inside a coroutine |
| `shell-injection` | 15 | a shell command built from generated text |
| `no-trace` | 16 | tracing on, project unnamed |
| `budget` | 17 | a model loop with nothing bounding calls, tokens or time |
| `prose-contract` | 19 | an answer parsed with a regex instead of a schema |
| `string-handoff` | 20 | one agent's string handed straight to another |

## How it is trusted

`tests/` holds two fixtures and one assertion per claim:

- `fixtures/trap/` — twelve small files, one per rule: every rule must fire;
- `fixtures/clean/` — a correct agent: nothing may fire;
- the book's own tree — 133 harnesses verify it, so the audit must report zero
  findings there. If it does not, the rule is wrong, not the code.

```bash
python -m unittest discover -s tests    # from toolkit/
agent-audit ../.. --exclude 'run_*.py' --exclude '*/toolkit/*'
```

It has been deliberately small: no plugin system, no config file, no dependencies
outside the standard library. A rule is a function over an `ast` tree, and the
list is data, so the book's appendix can be generated from the same source.

## The book's appendix

`build_appendix.py` renders the appendix of the book from the same rules:

```bash
python build_appendix.py            # print the section
python build_appendix.py --write    # replace it in the manuscript
python build_appendix.py --check    # fail when the book is out of date
```

The appendix uses indented code blocks instead of fences: a fenced block under an
"appendix" heading would be read by the book's extractor as a listing it must run.
