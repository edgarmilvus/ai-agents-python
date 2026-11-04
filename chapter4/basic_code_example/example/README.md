# Example 1 — the CoT chain

## What it does

A prompt that forces a reasoning section, piped into the model and an output parser. The chain is an LCEL sequence: `prompt | llm | parser`, and the only thing that makes it chain-of-thought is the instruction in the template.

## The listings

| file | what it is |
| --- | --- |
| `01_cot_chain.py` | the listing: template, chain and one execution |
| `run_cot_chain.py` | the harness: a scripted model, the same prompt and parser |

## Run it

```bash
cd chapter4/basic_code_example/example/files
python3 run_cot_chain.py
```

`01_cot_chain.py` needs a key and a provider, so the harness scripts the model and runs the same prompt and parser. It writes `output/chain.json` and exits non-zero if the template stops asking for the reasoning section.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/chain.json` | whether the template asks for reasoning, the answer and the model |

## Notes

- Needs `langchain-classic` and `langchain-openai`; the listing also needs `OPENAI_COMPATIBLE_API_KEY`.
- The model's text is returned unchanged: the reasoning is in the prompt, not in the parser.
- The chapter's fragments under *Detailed Code Breakdown* are sections of this same file, kept in the book as illustrations.
