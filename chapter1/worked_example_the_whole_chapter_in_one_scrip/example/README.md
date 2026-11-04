# Worked example — the whole chapter in one script

## What it does

The four exercise solutions above, unchanged, in a single file whose `__main__` block runs them in sequence. It is the chapter's end-to-end demo: one command shows the OODA loop, the memory agent, the tool router and the planning layer.

## The listings

| file | what it is |
| --- | --- |
| `01_all_exercises_demo.py` | the worked example, generated from the four solution listings |
| `run_worked_example.py` | the harness: checks the demo still contains each solution, then runs it |

## Run it

```bash
cd chapter1/worked_example_the_whole_chapter_in_one_scrip/example/files
python3 01_all_exercises_demo.py
```

The listing is the run: it executes the four exercises in sequence and prints each section. The harness checks that the demo still contains every solution and exits non-zero if an exercise fails.

## What it produces

Written by the harness:

| path | what it is |
| --- | --- |
| `output/demo.log` | the complete output of one run, stdout and stderr together |

## Notes

- The demo is generated, never hand-assembled:

```bash
python3 tools/build_chapter1_demo.py
```

- Exercises 1 and 2 use `random`, so their numbers differ between runs; the sequence of phases does not.
- The four solutions coexist because each keeps its own function names. Two exercises defining the same name would silently shadow each other, which is why the file is generated and checked.
