# Python AI Autonomous Agents — companion code

Runnable code for *Python AI Autonomous Agents*. Each
chapter folder holds one listing per example and exercise exactly as it appears in
the book, plus a harness that drives it and asserts what happened.

This folder is the **code-only copy**: the chapters, their harnesses and the
runners. The manuscript, the figures and the EPUB build live one level up, in the
writing folder.

All twenty chapters are processed: see `chapter1/README.md` through
`chapter20/README.md`.

## Setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip install -r requirements-browser.txt   # chapter 14, real browser
```

The second file is the optional extra: Selenium and its driver manager, used by
chapter 14's real browser run only. The offline suite stubs Selenium, so leaving it
out keeps all 133 harnesses green; `run_everything.sh` then skips that step, prints
the command above and carries on.

## Environment

The listings never hard-code a provider. They read three variables:

| variable | used for | default in code |
| --- | --- | --- |
| `OPENAI_COMPATIBLE_API_KEY` | the key sent to the gateway | none, required |
| `OPENAI_COMPATIBLE_BASE_URL` | the OpenAI-compatible endpoint | `https://openrouter.ai/api/v1` |
| `OPENAI_COMPATIBLE_MODEL` | the model that answers | `~deepseek/deepseek-flash-latest` |

Set them in your shell:

```bash
export OPENAI_COMPATIBLE_API_KEY=sk-or-...
export OPENAI_COMPATIBLE_BASE_URL=https://openrouter.ai/api/v1
export OPENAI_COMPATIBLE_MODEL='~deepseek/deepseek-flash-latest'
```

Only the key has to be set; the other two exist so a chapter can be re-run against
a different gateway or a stronger model without editing a listing. The live runner
reads the same variables, which is how a chapter can be pointed at a different
endpoint without touching its code.

## Run

One chapter:

```bash
./chapter1/run_offline.sh
```

The whole volume:

```bash
./run_offline.sh
```

No key and no network are needed for the suites: the listings that call a model are
driven through a scripted client installed by their harnesses. Chapter logs are
written to `chapterN/output/run_N.log`.

## Windows

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python run_offline.py
.venv\Scripts\python run_offline.py --only 5 10 11
```

Use Python 3.11 or 3.12, not 3.13: some pinned packages have no wheels for it yet.
The bash scripts (`run_offline.sh`, `run_live.sh`, `run_everything.sh`,
`run_queue_demo.sh`) are for macOS and Linux; on Windows use `run_offline.py` for the
suite and `tools\live_runner.py` for the live run.

Three chapters need their own software: chapter 14 needs Chrome (Selenium Manager
fetches the driver), chapter 18's queue demo needs a Redis server (Memurai installs
one as a Windows service), and chapter 17 has no `SIGALRM`, so the budget is measured
after the call instead of interrupting it. The suite itself runs without any of them.

## Live run (costs money)

The suites are offline on purpose. To prove the *prompts* against the real model,
there is a second, manual runner:

```bash
./run_live.sh              # the whole run
./run_live.sh --only 2 16  # selected chapters
./run_live.sh --list       # what it would run
```

It executes one or two example listings per chapter that actually instantiate a
model (1–8, 11, 16, 19), plus chapter 7's three exercise crews — listings that define
a driver function and leave the call to the reader, so the runner calls it. Each one
runs in its project's `output/`, with a timeout. It passes only if the process exits
0, prints something, and shows no traceback. It prints the LangSmith run count before
and after, when a key is present.

There is no provider to choose: the runner reads the same three variables the listings
read, and passes them through unchanged.

```bash
export OPENAI_COMPATIBLE_BASE_URL="https://openrouter.ai/api/v1"
export OPENAI_COMPATIBLE_MODEL="~deepseek/deepseek-flash-latest"
export OPENAI_COMPATIBLE_API_KEY=...
```

Those two defaults are what the listings carry, so on OpenRouter only the key has to be
exported. Point the base URL somewhere else and the same run works there. Each listing
has its own timeout, and that is the only limit: there is no balance to watch, so a row
that exceeds its timeout is reported, not retried.

`--slow` adds the chapter 7 template, which runs four crews in one file and takes
over fifteen minutes; its third exercise is hierarchical and with a reasoning
model can stall in delegation. Chapter 6's hierarchical crew is in the default
run: it finishes in three to eleven minutes, depending on how often the manager
delegates.

A gateway that says "OpenAI-compatible" is not automatically able to run every
listing. Gemini 3, through its `/v1beta/openai/` surface, requires a
`thought_signature` on every function call the conversation replays; the OpenAI
client receives that field and drops it, so any tool-calling listing fails on its
second turn with:

```
Function call is missing a thought_signature in functionCall parts
```

Single-turn calls and every listing without tools do work there. The two gateways
above do not add the requirement, and both are tested on the full live run.

Chapter 11 needs embeddings, which a chat gateway does not necessarily serve, and
chapter 16 needs a LangSmith key if you want to see the traces. Both are ordinary
environment variables, exported like the other three; the runner reads no key file:

```bash
export EMBEDDING_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/"
export EMBEDDING_MODEL="gemini-embedding-2"
export EMBEDDING_API_KEY=...        # Google AI Studio key, free tier is enough

export LANGCHAIN_API_KEY=...        # chapter 16 only
export LANGCHAIN_TRACING_V2="true"
```

Leave them unset and the two chapter 11 rows are reported as `SKIP` with the missing
variable named — nothing is broken, the machine is doing what it can. Chapter 16
still runs; it just sends no trace.

Logs land in `output/live/`. This is not part of `run_offline.sh`: it needs a key and
a network.

Two environment checks have their own entry points, because they need services.
`./run_everything.sh` runs the offline suite and both of them, skipping whichever is
not installed (Redis, Chrome, Selenium) and printing how to install it, then reports
the summary; `--live` adds the live run at the end.

```bash
./run_queue_demo.sh   # chapter 18 for real: Redis + rq worker + one finished job
```

It starts Redis if it is not running, copies the listing to a temporary module
(served as `__main__`, the task function is not importable by the worker),
submits through the app and polls until the job is finished. Chapter 14's real
browser run is a plain command: `pip install -r requirements-browser.txt`, then
`chapter14/basic_code_example/example/files/01_digital_librarian.py`.


## toolkit

`toolkit/` checks the twelve failures the book catalogues, in your own code:

```bash
pip install ./toolkit
agent-audit .                 # exit code 1 when something is found
agent-audit . --list          # the rules, with the chapter that explains each
```

It is validated twice: `tests/fixtures/trap/` must light every rule, and this
repository — verified by 133 harnesses — must report zero findings.

## Layout

```
chapterN/
  README.md                      index of the chapter's projects
  run_offline.sh                     one line per harness
  output/run_N.log               the suite log
  <section>/<example|exercise>/
    README.md                    what it is, how to run it, what it produces
    files/                       listing + harness
    output/                      artefacts written by the harness
run_offline.sh                       every chapter, plus the totals
run_live.sh                      the model-calling listings, against the real API
run_everything.sh                offline suite + queue + browser, --live for the run
VERSION                          which build this folder is
run_queue_demo.sh                chapter 18 against a real Redis and worker
tools/                           repo-only helpers (demo builder, harness base)
```

Listings in `files/` are the book's listings byte for byte; corrections are written
from `files/` into the manuscript, never the other way round.

## License

The code in this folder is released under the MIT License; see `LICENSE`.
