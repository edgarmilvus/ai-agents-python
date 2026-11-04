# Chapter 19 — The Economics of Agents: Token Cost Management and Optimization

The chapter's code, one folder per section. Every folder holds the listing exactly
as it appears in the book, a harness that drives it, and an `output/` folder for
what the harness produced.

| folder | listing | what it shows |
| --- | --- | --- |
| `basic_code_example/example/` | `01_cost_tracker.py` | what three calls cost, and why |
| `advanced_application_script/example/` | `01_optimized_pipeline.py` | compress, then extract, then add up |
| `worked_example_solution_shells_for_reference/example/` | `01_solution_shells.py` | all four exercises in one run |
| `exercise_1_asynchronous_token_budget_manager/exercise/` | `01_async_budget.py` | the budget stops the call, not the invoice |
| `exercise_2_context_window_trimming_via_re_ran/exercise/` | `01_rerank_trimming.py` | ten documents in, three out |
| `exercise_3_persistent_caching_for_agent_tools/exercise/` | `01_persistent_cache.py` | the second call is free |
| `exercise_4_interactive_challenge_enforcing_st/exercise/` | `01_structured_output.py` | JSON costs less than a paragraph |

## Run the chapter

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./chapter19/run_offline.sh
```

`run_offline.sh` runs the seven harnesses and prints one line per harness; the log is
written to `chapter19/output/run_19.log`. Any harness that fails makes the suite
exit 1. Everything runs offline: the pipeline's model calls are answered by a fake
client, the rest is simulated arithmetic and `tiktoken` counts.

## What the harnesses caught

- **The structured call used the wrong API.** The extraction passed
  `response_model=MarketSummary` to `client.chat.completions.create`; that argument
  belongs to `instructor`, not to the OpenAI SDK, so the documented call raises.
  It then used `chat.completions.parse(..., response_format=MarketSummary)`, which
  works on OpenRouter, but a gateway that answers `400` to a structured
  request needs the schema-in-prompt fallback (`400 response_format type is
  unavailable`). It now asks for `{"type": "json_object"}`, carries the schema in
  the prompt and validates with `MarketSummary.model_validate_json`.
- **The trimming could not meet its own goal.** It kept two supporting documents,
  which reduced the context by 51%, and then asserted 60%. It keeps one now: 60.27%.
- **The cache demo printed different numbers every run.** The "expensive" tool
  derived its result from `hash(ticker)`, and Python salts string hashes per
  process, so the book's sample output could never be reproduced. The value now
  comes from the characters.
- **Three solutions were excerpts, not programs.** Exercises 2, 3 and 4 started
  mid-file — no imports, no token counter — and their run calls were commented out
  because a separate `main` block was supposed to drive them. Each now carries its
  own setup and runs itself; the `main` block stays in the book as the sketch it is.
