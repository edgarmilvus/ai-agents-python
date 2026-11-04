# Chapter 11 — Vector Memory: RAG for Agents (The Hippocampus)

The chapter's code, one folder per section. Every folder holds the listing exactly
as it appears in the book, a harness that drives it and asserts what happened, and
an `output/` folder for what the harness produced.

| folder | listing | what it shows |
| --- | --- | --- |
| `basic_code_example/example/` | `01_context_window_rag.py` | load, split, embed, store, retrieve, answer |
| `advanced_application_script/example/` | `01_strategy_analyst_rag.py` | retrieval over project history, with sources |
| `exercise_5_multi_vector_rag_for_code_and_docu/exercise/` | `01_multi_vector_hint.py` | the mocked infrastructure and the router |
| `unified_solution_block_for_the_exercises/example/` | `01_unified_solution.py` | all five exercises in one block |

## Run the chapter

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./chapter11/run_offline.sh
```

`run_offline.sh` runs the four harnesses and prints one line per harness; the log is
written to `chapter11/output/run_11.log`. Any harness that fails makes the suite
exit 1. The two RAG examples are driven through fake embeddings and a scripted
chat model, so no key and no network are needed; the two exercise blocks are fully
mocked.

## Embeddings are a second endpoint

A chat gateway does not necessarily serve an embeddings API. The listings read
`EMBEDDING_BASE_URL` and `EMBEDDING_API_KEY` for the
embedding client and fall back to the chat gateway when they are unset, so a
provider that offers one but not the other is a configuration change rather than
a code change.

## What the harnesses caught

- **`langchain.text_splitter` and `langchain.schema`** no longer exist in
  LangChain 1.x: the imports come from `langchain_text_splitters` and
  `langchain_core.documents`, and `RetrievalQA` from `langchain_classic`.
- **A datetime inside a metadata filter**: `json.dumps` refused it, so the
  chapter's second exercise died before reaching the router. It now passes
  `default=str`.
- **An f-string with a backslash**: the unified solution could not even be
  parsed on Python 3.11 (`f"…replace('\n', ' ')…"`), so the preview is built on
  its own line.
- **One key for two services** was the chapter's own warning; the listings now
  configure chat and embeddings separately.
