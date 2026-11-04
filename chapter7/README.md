# Chapter 7 — Using CrewAI: Role-Playing Agents and Task Delegation

The chapter's code, one folder per section. Every folder holds the listing exactly
as it appears in the book, a harness that drives it and asserts what happened, and
an `output/` folder for what the harness produced.

| folder | listing | what it shows |
| --- | --- | --- |
| `basic_code_example/example/` | `01_sequential_crew.py` | two agents, two tasks, one after the other |
| `advanced_application_script/example/` | `01_marketing_crew.py` | three specialists, one may delegate |
| `exercise_setup/example/` | `01_exercise_setup.py` | the configuration the exercises share |
| `solution_template_and_code_structure/example/` | `01_solution_template.py` | all four exercises in one file |
| `exercise_1_the_technical_content_writer_crew/exercise/` | `01_content_crew.py` | sequential research then writing |
| `exercise_2_the_financial_analysis_crew_delega/exercise/` | `01_financial_crew.py` | delegation with a structured report |
| `exercise_3_the_global_product_launch_crew_hie/exercise/` | `01_launch_crew.py` | a hierarchical launch crew |
| `exercise_4_interactive_challenge_integrating/exercise/` | `01_validation_crew.py` | a validation gate before scheduling |

## Run the chapter

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./chapter7/run_offline.sh
```

`run_offline.sh` runs the eight harnesses and prints one line per harness; the log is
written to `chapter7/output/run_7.log`. Any harness that fails makes the suite
exit 1. Every listing here builds a crew, so all eight are driven through a
scripted CrewAI model: no key and no network are needed.

## The same model in every crew

Each listing builds one explicit `LLM(model="openai/<model>", base_url=..., api_key=...)`
from `OPENAI_COMPATIBLE_*`. Without it CrewAI falls back to OpenAI's own endpoint and key,
which is why the original listings needed `OPENAI_API_KEY` even though the model
was a string.

## What the harnesses caught

- **A manager listed among its agents.** CrewAI 1.x rejects a hierarchical crew
  whose `manager_agent` also appears in `agents` — twice: exercise 3 and the
  template.
- **A `__main__` block calling functions it does not define**: exercise 4 invoked
  exercises 1–3, a copy of the combined template.
- **Two solutions with no imports at all** (exercises 2 and 3, and the template):
  they assumed the shared setup block, and could not run on their own.
- **`verbose=2`**, which CrewAI 1.x validates as a boolean.
