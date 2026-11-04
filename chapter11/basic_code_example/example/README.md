# Example 1 — the basic RAG pipeline

## What it does

A policy document is loaded, split, embedded and stored, then retrieved with a question. Four stages, one script: load, index, retrieve, answer.

## The listings

| file | what it is |
| --- | --- |
| `01_context_window_rag.py` | the listing: loader, splitter, embeddings, Chroma and RetrievalQA |
| `run_basic_rag.py` | the harness: fake clients, the same pipeline |

## Run it

```bash
cd chapter11/basic_code_example/example/files
python3 run_basic_rag.py
```

`01_context_window_rag.py` needs an embedding provider and a key, so the harness scripts both clients and runs the same loader, splitter, store and chain. It writes `output/result.json` and exits non-zero if the retrieval path stops answering.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the answer and the chunk count |

## Notes

- Needs `langchain-classic`, `langchain-text-splitters`, `langchain-openai` and `chromadb`.
- The listing needs `OPENAI_COMPATIBLE_API_KEY`; embeddings read `EMBEDDING_BASE_URL` and `EMBEDDING_API_KEY` because a chat gateway does not necessarily serve an embeddings API.
- The harness swaps `OpenAIEmbeddings` and `ChatOpenAI` for fakes; the loader, splitter, store and chain are the listing's.
- Live, `run_live.sh` points those two variables at Gemini's OpenAI-compatible
  endpoint with `gemini-embedding-2`; the listing sends raw strings, not token
  ids, because that endpoint answers 501 to the token-array form.
