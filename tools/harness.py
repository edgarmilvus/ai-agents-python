"""Assertion and artefact helper shared by the chapter harnesses.

A harness is a script that imports a listing, drives it, checks the result and
prints exactly one verdict line:

    ok      example 1 (agentic loop) — 12 assertions passed
    FAILED  example 1 (agentic loop) — 2 of 12 assertions failed

Artefacts go to the project's `output/` folder, which is created on demand.
Nothing here writes an absolute path: artefacts record relative names only.
"""
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import sys
import traceback


def load_listing(path: pathlib.Path, name: str):
    """Import a listing as a module without running its __main__ block."""
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Harness:
    def __init__(self, name: str, files_dir: pathlib.Path):
        self.name = name
        self.files_dir = pathlib.Path(files_dir)
        self.project = self.files_dir.parent
        self.output = self.project / "output"
        self.count = 0
        self.failures: list[str] = []

    # -- assertions -----------------------------------------------------
    def check(self, condition, message: str) -> bool:
        self.count += 1
        if not condition:
            self.failures.append(message)
        return bool(condition)

    def equal(self, actual, expected, message: str) -> bool:
        return self.check(actual == expected, f"{message} (got {actual!r}, expected {expected!r})")

    def contains(self, haystack, needle, message: str) -> bool:
        return self.check(needle in haystack, f"{message} (missing {needle!r})")

    # -- artefacts ------------------------------------------------------
    def write_json(self, name: str, data) -> pathlib.Path:
        self.output.mkdir(parents=True, exist_ok=True)
        path = self.output / name
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        return path

    def write_text(self, name: str, text: str) -> pathlib.Path:
        self.output.mkdir(parents=True, exist_ok=True)
        path = self.output / name
        path.write_text(text)
        return path

    # -- reporting ------------------------------------------------------
    def report(self) -> int:
        if self.failures:
            print(f"FAILED  {self.name} — {len(self.failures)} of {self.count} assertions failed")
            for failure in self.failures:
                print(f"        {failure}")
            code = 1
        else:
            print(f"ok      {self.name} — {self.count} assertions passed")
            code = 0
        # The machine-readable verdict goes to stderr: libraries that draw a
        # live box (CrewAI, rich) write to stdout and would otherwise splice the
        # verdict into a border, where no line-anchored pattern can find it.
        print(f"__VERDICT__ {code} {self.count} {self.name}", file=sys.stderr)
        # Leave without running interpreter finalisation. CrewAI, litellm and
        # Selenium keep daemon threads alive, and one of them can take the stdin
        # lock while the runtime is shutting down: CPython then aborts with
        # "Fatal Python error: _enter_buffered_busy" *after* the verdict, turning a
        # passing harness into exit code 134 on Windows. The verdict is final, so
        # there is nothing left to clean up that the harness has not already done.
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(code)

    def crash(self) -> int:
        self.count += 1
        print(f"FAILED  {self.name} — crashed before the verdict")
        traceback.print_exc(file=sys.stderr)
        return 1
