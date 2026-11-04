# Chapter 16 — Tracing and Debugging: Observability with LangSmith

The chapter's code, one folder per section. Every folder holds the listing exactly
as it appears in the book, a harness that drives it, and an `output/` folder for
what the harness produced.

| folder | listing | what it shows |
| --- | --- | --- |
| `basic_code_example_activating_global_tracing/example/` | `01_global_tracing.py` | one LCEL chain under one environment switch |
| `advanced_application_script/example/` | `01_traced_agent.py` | two tools, two queries, two paths |
| `worked_example_the_exercise_scripts/example/` | `01_exercise_scripts.py` | the four exercises' code in one block |
| `unified_solution_block_for_the_five_exercises/example/` | `01_solutions.py` | all five solutions, executed at import |

Everything here runs without a LangSmith account and without a model key. The
harnesses install an in-memory client (`tools/fake_langsmith.py`) and a chat fake
that can bind tools (`tools/fake_agents.py`), and set `LANGCHAIN_TRACING_V2=false`,
so nothing leaves the process.

## Run the chapter

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./chapter16/run_offline.sh
```

`run_offline.sh` runs the four harnesses and prints one line per harness; the log is
written to `chapter16/output/run_16.log`. Any harness that fails makes the suite
exit 1.

## What the harnesses caught

The chapter is about seeing what an agent did; four of these defects made the agent
do nothing at all.

- **No agent could be built.** Every prompt in the exercise code lacked the
  `agent_scratchpad` placeholder, so `create_openai_tools_agent` refused with
  "Prompt missing required variables". Three prompts in the worked example and
  three in the solutions are fixed.
- **The prompt was fetched from the agent.** `agent_executor.agent.prompt` does not
  exist on the object this creator returns, so the cost comparison crashed. Both
  configurations now share `build_inventory_prompt()`.
- **The failing tool never failed.** Exercise 2 is about `"150 units"` reaching a
  tool that wants an `int`; the solution's tool called
  `cleaned_amount.split()[0]`, which quietly turns `"150 units"` into `150`. It now
  converts the whole string, and the exercise produces the failure its analysis
  describes.
- **The extraction returned a message.** `prompt | llm` with no parser hands back
  an `AIMessage`, which then went into the run's outputs. `StrOutputParser` closes
  the chain in both blocks.
- **`create_react_agent` cannot take that prompt.** The advanced listing paired the
  text-ReAct creator with a `MessagesPlaceholder` prompt; it now uses
  `create_openai_tools_agent`, and the prose follows.
- **The switch was forced on.** `LANGCHAIN_TRACING_V2` is now set with
  `setdefault`, so a harness (or a reader without an account) can turn tracing off
  and still run the code. The banner prints what the variable actually says.
