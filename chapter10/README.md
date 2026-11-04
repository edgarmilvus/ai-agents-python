# Chapter 10 — Handling State and History: Long-term Persistent Memory

The chapter's code, one folder per section. Every folder holds the listing exactly
as it appears in the book, a harness that drives it and asserts what happened, and
an `output/` folder for what the harness produced.

| folder | listing | what it shows |
| --- | --- | --- |
| `basic_code_example/example/` | `01_state_snapshot.py` | one pickled state across two runs |
| `advanced_application_script/example/` | `01_three_layer_persistence.py` | JSON config, SQLite history, Chroma memory |
| `python_code_implementation_block/example/` | `01_persistence_pipeline.py` | config, async history and reload |
| `exercise_4_the_unified_persistent_agent_chall/exercise/` | `01_unified_persistent_agent.py` | the four exercises in one agent |

## Run the chapter

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./chapter10/run_offline.sh
```

`run_offline.sh` runs the four harnesses and prints one line per harness; the log is
written to `chapter10/output/run_10.log`. Any harness that fails makes the suite
exit 1. Everything runs offline: the model and the embeddings in the advanced
example are fakes.

## What the harnesses caught

- **Two inputs, one memory.** The advanced chain receives `semantic_context` and
  `input`, so `ConversationBufferWindowMemory` could not tell which one was the
  user's turn and raised `ValueError: One input key expected`. The memory now
  declares `input_key="input"`.
- **`langchain.memory` / `langchain.chains`** no longer exist in LangChain 1.x;
  the imports come from `langchain-classic`, and `FakeListChatModel` /
  `FakeEmbeddings` from `langchain-core`.
- **Warnings with absolute paths.** The langchain imports print deprecation
  notices containing `site-packages` paths; the advanced harness silences them so
  no artefact carries a username.
