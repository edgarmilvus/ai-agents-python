# Chapter 3 — The Tool Belt: Connecting LLMs to APIs, Files, and the Web

The chapter's code, one folder per section. Every folder holds the listing exactly
as it appears in the book, a harness that drives it and asserts what happened, and
an `output/` folder for what the harness produced.

| folder | listing | what it shows |
| --- | --- | --- |
| `basic_code_example/example/` | `01_tool_schema.py` | a function and the schema that describes it |
| `advanced_application_script/example/` | `01_market_analyst.py` | two schemed tools: an API read and a file append |
| `necessary_setup_code_block/example/` | `01_mock_services.py` | the seeded database, mock API and mock files |
| `starter_code_for_the_exercises/example/` | `01_exercise_tools.py` | the seven tools the exercises start from |
| `exercise_1_the_secure_configuration_manager_a/exercise/` | `01_secure_config_agent.py` | reading and updating JSON without losing keys |
| `exercise_2_the_real_time_financial_analyst_ag/exercise/` | `01_financial_analyst_agent.py` | a quote tool with real error paths |
| `exercise_3_the_orm_inventory_query_agent_data/exercise/` | `01_orm_inventory_agent.py` | three optional filters over SQLAlchemy |
| `exercise_4_interactive_challenge_the_multi_mo/exercise/` | `01_deployment_analyst_agent.py` | live status versus historical log |
| `exercise_5_tool_schema_validation_and_robustn/exercise/` | `01_schema_validation_agent.py` | a tool that validates before it computes |

## Run the chapter

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./chapter3/run_offline.sh
```

`run_offline.sh` runs the nine harnesses and prints one line per harness; the log is
written to `chapter3/output/run_3.log`. Any harness that fails makes the suite
exit 1. No API key and no network are needed: the one listing that calls a model is
driven through a scripted chat model.

## Two blocks are libraries

`01_mock_services.py` and `01_exercise_tools.py` define behaviour and run nothing,
and the five exercise listings define tools without calling them. Their harnesses
compose the published blocks and call the tools, so no listing is duplicated:

```
mock services + exercise tool -> one program, run in process
```
