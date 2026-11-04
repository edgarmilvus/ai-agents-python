# Example 2 — the strategy analyst

## What it does

The same pipeline over a project history, with a retrieval chain that answers a question and then quotes the sources it used. The demo removes its vector store when it finishes.

## The listings

| file | what it is |
| --- | --- |
| `01_strategy_analyst_rag.py` | the listing: indexing, retrieval chain, sources and cleanup |
| `run_strategy_analyst.py` | the harness: fake clients and the cleanup check |

## Run it

```bash
cd chapter11/advanced_application_script/example/files
python3 run_strategy_analyst.py
```

`01_strategy_analyst_rag.py` needs an embedding provider and a key, so the harness scripts both clients and runs the same index and query. It writes `output/result.json` and exits non-zero if the sources or the cleanup disappear.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the answer |

## Notes

- Needs `langchain-classic`, `langchain-text-splitters`, `langchain-openai` and `chromadb`.
- `langchain.text_splitter` and `langchain.schema` no longer exist in LangChain 1.x: the imports come from `langchain_text_splitters` and `langchain_core.documents`.
- Live, the embeddings come from Gemini (`gemini-embedding-2`) via its
  OpenAI-compatible endpoint; the listing sends raw strings rather than token ids,
  because that endpoint answers 501 to the token-array form.
