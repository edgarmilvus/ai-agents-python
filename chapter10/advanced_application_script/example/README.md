# Example 2 — three persistence layers

## What it does

Configuration in JSON, conversation history in SQLite, semantic memory in Chroma: two sessions in one run show each layer reloading what the previous one wrote.

## The listings

| file | what it is |
| --- | --- |
| `01_three_layer_persistence.py` | the listing: the three stores and two sessions |
| `run_three_layers.py` | the harness: asserts the reloads and cleans the output |

## Run it

```bash
cd chapter10/advanced_application_script/example/files
python3 01_three_layer_persistence.py
```

The listing is the run: it prints two sessions, the reloaded SQLite history and the semantic recall. `run_three_layers.py` asserts all three layers and exits non-zero if a session loses its state.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | the three layers that were exercised |

## Notes

- Needs `langchain-classic`, `langchain-community` and `chromadb`; no key and no network, the model and embeddings are fakes.
- `ConversationBufferWindowMemory` needs `input_key="input"` here: the chain also receives `semantic_context`, and without it saving the turn cannot tell the two inputs apart.
- The demo deletes its files at the end, so nothing is left behind.
