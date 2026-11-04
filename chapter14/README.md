# Chapter 14 — Browser Agents: Automating the Web with Selenium and AI

The chapter's code, one folder per section. Every folder holds the listing exactly
as it appears in the book, a harness that drives it, and an `output/` folder for
what the harness produced.

| folder | listing | what it shows |
| --- | --- | --- |
| `basic_code_example/example/` | `01_digital_librarian.py` | one Selenium flow, no model |
| `advanced_application_script/example/` | `01_job_filter_agent.py` | a page read by Selenium, judged by a model |
| `python_implementation_structure/example/` | `01_browser_tool.py` | one wrapper for every browser action |
| `exercise_1_the_dynamic_locator_decipherer/exercise/` | `01_dynamic_locator.py` | a locator rewritten after it fails |
| `exercise_2_autonomous_multi_page_task_flow_wi/exercise/` | `01_multi_page_memory.py` | login, tier, confirm, across three pages |
| `exercise_3_interactive_challenge_enhancing_re/exercise/` | `01_visual_verification.py` | a confidence score that can reject the order |
| `exercise_4_enforcing_dry_and_abstraction_with/exercise/` | `01_browser_tool_dry.py` | three commands, one wrapper |

## Run the chapter

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./chapter14/run_offline.sh
```

`run_offline.sh` runs the seven harnesses and prints one line per harness; the log is
written to `chapter14/output/run_14.log`. Any harness that fails makes the suite
exit 1. Nothing here launches a browser: the two listings that import Selenium are
run against `tools/fake_selenium.py`, a scripted driver that records what the agent
asked the page to do. To run those two for real, `pip install selenium
webdriver-manager` and have Chrome installed.

## What the harnesses caught

Four of the five defects made a listing print something that looked fine while the
path it was teaching never ran.

- **The retry never happened.** In exercise 1 the first locator succeeded by
  construction, so the failure branch, the feedback prompt and the CSS rewrite —
  the subject of the exercise — were unreachable. The mock now fails the first
  attempt, with the reason the prompt needs.
- **The agent never left the login page.** In exercise 2 the run rebuilt the
  driver but kept the tool that held the old one, so the page advanced inside an
  object nobody was reading. The run stalled at step 3 for ten steps. Both objects
  are rebound now.
- **The suspicious order passed.** In exercise 3 the scenario was chosen by looking
  for `purchase 5 units` in the goal, which both scenarios contain, so the
  "Suspicious Outcome" run got the success page and scored 0.99. It now checks the
  scenario marker and scores 0.35.
- **The listings were silent.** All four exercise solutions left their
  `# Example Execution` calls commented out, so running the file printed nothing.
  They are uncommented and each now shows its own trace.
- **The legacy stack.** The advanced listing imported `PromptTemplate` and
  `PydanticOutputParser` from the 0.x `langchain` package and hardcoded `gpt-4o`
  with an OpenAI key. It now imports from `langchain_core` and reaches
  `~deepseek/deepseek-flash-latest` through `OPENAI_COMPATIBLE_*`.
