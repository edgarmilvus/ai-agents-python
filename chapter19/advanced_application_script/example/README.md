# Example 2 — the two-stage pipeline

## What it does

Compress first, extract second: a verbose feedback document is summarised in step A, and the short summary is what step B sends to the structured-output call. Usage from both calls is accumulated into one estimate.

## The listings

| file | what it is |
| --- | --- |
| `01_optimized_pipeline.py` | the listing: client, compression, structured extraction, report |
| `run_optimized_pipeline.py` | the harness: a fake client with fixed usage numbers |

## Run it

```bash
cd chapter19/advanced_application_script/example/files
python3 run_optimized_pipeline.py
```

`01_optimized_pipeline.py` calls the endpoint twice, so it needs a key. The harness replaces `OpenAI` with a fake that answers both calls, then checks the accumulated usage and the schema handling.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/result.json` | how many calls it made |

## Notes

- The extraction used `response_model=MarketSummary`, which is the instructor API, not the OpenAI SDK: with a plain client the call raises. It now asks for `response_format={"type": "json_object"}`, puts the schema in the prompt and validates the answer with `MarketSummary.model_validate_json` — because a schema-typed response format is not available on every gateway (DeepSeek rejects it).
- The parsed object is read from `choices[0].message.parsed`; the usage still comes from the response, so both steps are priced.
- The model and endpoint come from `OPENAI_COMPATIBLE_*`, like the rest of the volume.
