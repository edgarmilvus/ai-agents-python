# Python AI Autonomous Agents — companion code

Runnable code for *Python AI Autonomous Agents*. Each chapter folder holds one
listing per example and exercise exactly as it appears in the book, plus a harness —
a script that runs the listing, feeds it a scripted model instead of the network,
and checks what came back.

## Setup

You need Python 3.11 or 3.12 (3.13 is too new for some of the pinned packages).

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip install -r requirements-browser.txt
```

Use the interpreter by its version, not `python3`: on a Mac the system `python3` is
often 3.9, and `openai` 2.54 needs 3.10 or newer, so the install stops with
`Could not find a version that satisfies the requirement openai==2.54.0`. Substitute
`python3.12` if that is the one you have.

Activating the environment is optional: every command names the interpreter by path, so
it works from any shell without `source .venv/bin/activate`.

The second requirements file is the optional extra: Selenium and its driver manager, for
chapter 14's real browser run. The offline suite stubs Selenium, so leaving it out keeps
all 133 harnesses green; `run_everything.sh` skips that step and prints the command.

## Environment

Only the live run needs these. The suites read no key and touch no network.

The listings never hard-code a provider. They read three variables:

| variable | used for | default in code |
| --- | --- | --- |
| `OPENAI_COMPATIBLE_API_KEY` | the key sent to the gateway | none, required |
| `OPENAI_COMPATIBLE_BASE_URL` | the OpenAI-compatible endpoint | `https://openrouter.ai/api/v1` |
| `OPENAI_COMPATIBLE_MODEL` | the model that answers | `~deepseek/deepseek-flash-latest` |

```bash
export OPENAI_COMPATIBLE_API_KEY=sk-or-...
export OPENAI_COMPATIBLE_BASE_URL=https://openrouter.ai/api/v1
export OPENAI_COMPATIBLE_MODEL='~deepseek/deepseek-flash-latest'
```

Only the key has to be set: the two defaults are OpenRouter's, and OpenRouter and
DeepSeek are the two gateways the book uses. Point the base URL somewhere else and
the same listings run there, because nothing in the code names a provider — the
runners pass these three variables through unchanged.

## Run

One chapter, then the whole volume:

```bash
./chapter1/run_offline.sh
./run_offline.sh
```

A chapter prints one line per project and a verdict:

```
ok      basic_code_example/example — 18 assertions passed
...
chapter 1: ok
```

The volume runner prints every chapter and closes with the totals — for this build,
20 chapters, 133 harnesses, 957 assertions, `volume: ok`, in three to four minutes.
Each chapter writes its log to `chapterN/output/run_N.log`; the volume runner writes
`output/run_offline.log`. No key and no network are needed: the listings that call a
model are driven through a scripted client their harnesses install.

## Live run

The suites prove the code paths; the live run proves the prompts. It needs the key
from Environment, and it spends money — about nine cents for the 21 listings on
DeepSeek Flash, under half a dollar per run, fifteen to twenty minutes:

```bash
./run_live.sh              # every listing
./run_live.sh --only 2 16  # selected chapters
./run_live.sh --list       # the listings, free
```

It runs one or two listings per chapter that instantiates a model (1–8, 11, 16, 19),
plus chapter 7's three exercise crews, each in its project's `output/` with its own
timeout. A listing passes when the process exits 0, prints something and shows no
traceback; each one keeps its log in `output/live/`. Chapter 6's hierarchical crew
is in there and takes three to eleven minutes, depending on how often the manager
delegates. `--slow` adds chapter 7's template, which runs four crews and takes over
fifteen minutes: 23 listings instead of 21.

Two chapters need a second service. Without it those listings are reported as
`SKIP`, naming the variable, and the run still ends clean:

```bash
export EMBEDDING_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/"
export EMBEDDING_MODEL="gemini-embedding-2"
export EMBEDDING_API_KEY=...        # chapter 11 only

export LANGCHAIN_API_KEY=...        # chapter 16 only
export LANGCHAIN_TRACING_V2="true"
```

"OpenAI-compatible" is not a guarantee that every listing runs. Gemini 3, through
its `/v1beta/openai/` surface, requires a `thought_signature` on every function call
the conversation replays; the OpenAI client drops that field, so a tool-calling
listing fails on its second turn. Single-turn calls and listings without tools work
there.

## Run everything

`./run_everything.sh` is the whole check in one command: the offline suite, the
Redis queue demo, the browser run, and with `--live` the live run at the end. About
four minutes without it, twenty with it.

```bash
./run_everything.sh           # suite + services, live run skipped
./run_everything.sh --live    # the same, then the 21 listings
```

A phase whose service or package is missing is skipped with the command that
installs it — Redis, Chrome, Selenium — and the closing summary lists what ran and
what did not. That is why the script ends `ok` on a machine that has none of them,
and why `--live` without a key is skipped instead of failing.

The two services on their own:

```bash
./run_queue_demo.sh   # chapter 18 for real: Redis + rq worker + one finished job
```

It starts Redis if it is not running, copies the listing to a temporary module
(served as `__main__`, because the task function is not importable by the worker),
submits through the app and polls until the job is finished. Chapter 14's browser
run is a plain command, with `requirements-browser.txt` installed:
`chapter14/basic_code_example/example/files/01_digital_librarian.py`.

## Windows

Native Windows works; there is no WSL step. Use Python 3.11 or 3.12, not 3.13: some
pinned packages have no wheels for it.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m pip install -r requirements-browser.txt   # chapter 14 only

.venv\Scripts\python run_offline.py          # the suite, same totals as run_offline.sh
.venv\Scripts\python run_offline.py --only 5 10 11

.venv\Scripts\python tools\live_runner.py    # the live run, needs the key
.venv\Scripts\python tools\live_runner.py --list
```

`run_everything.sh` is a bash script: on Windows run the two commands it would chain
— `run_offline.py` and `tools\live_runner.py` — and add the services only if you want
them. Chrome runs natively and Selenium Manager fetches the driver; Redis has no
native server (Memurai installs one as a Windows service for chapter 18's demo);
chapter 17 measures the overrun after the call instead of interrupting it, because
Windows has no `SIGALRM`. The suite runs without any of them.

## Toolkit

`toolkit/` checks the twelve failures the book catalogues, in your own code:

```bash
.venv/bin/python -m pip install ./toolkit
.venv/bin/agent-audit .              # exit code 1 when something is found
.venv/bin/agent-audit . --list       # the rules, with the chapter that explains each
```

On Windows the same three lines are `.venv\Scripts\python -m pip install ./toolkit`
and `.venv\Scripts\agent-audit`.

Pointed at this repository it reports findings, and that is correct: the rules are
about agent code, so they also fire on the harnesses, which stub a model, and on
`toolkit/tests/fixtures/trap/`, which exists to trip every rule. Scope it to what
the rules are for:

```bash
.venv/bin/agent-audit . --exclude 'run_*.py' --exclude 'toolkit/*'
# 149 files · 0 finding(s)
```

That is the second half of its validation: `tests/fixtures/trap/` must light every
rule, and the book's listings must come out clean.

## Layout

```
chapterN/
  README.md                        index of the chapter's projects
  run_offline.sh                   one line per harness
  output/run_N.log                 the suite log
  <section>/<example|exercise>/
    README.md                      what it is, how to run it, what it produces
    files/                         listing + harness
    output/                        artefacts written by the harness
run_offline.sh                     every chapter, plus the totals
run_live.sh                        the model-calling listings, against the real API
run_everything.sh                  offline suite + services + live, skipping what is absent
run_queue_demo.sh                  chapter 18 against a real Redis and worker
run_offline.py                     the same suite without a POSIX shell
tools/                             shared helpers: harness base and scripted fakes
VERSION                            the build these files come from
```

Each listing in `files/` is the text printed in the book, byte for byte; the
`run_*.py` beside it is the harness that drives it, and it is not in the book.

## License

The code in this folder is released under the MIT License; see `LICENSE`.
