#!/usr/bin/env python3
"""Prove chapter 18's queue for real: Redis, an RQ worker, one finished job.

The offline harness replaces the queue with an in-memory object. This script does
the opposite: it starts a real Redis (if one is not already up), copies the
listing to a temporary module so the worker can import the task function — which
is exactly what fails when the file is run as `__main__` — starts `rq worker`,
submits through the FastAPI app, and polls until the job finishes.

    python3 tools/queue_demo.py
"""
from __future__ import annotations

import importlib.util
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
LISTING = ROOT / "chapter18/advanced_application_script/example/files/01_queue_worker.py"
QUEUE = "agent_analysis"
TIMEOUT = 60


def redis_up() -> bool:
    return subprocess.run(["redis-cli", "ping"], capture_output=True).returncode == 0


def main() -> int:
    if not LISTING.exists():
        print("missing", LISTING)
        return 2
    if shutil.which("redis-server") is None:
        print("redis-server not installed (brew install redis)")
        return 2

    started_redis = False
    if not redis_up():
        subprocess.run(["redis-server", "--daemonize", "yes"], check=True,
                       capture_output=True)
        started_redis = True
        for _ in range(20):
            if redis_up():
                break
            time.sleep(0.25)
        if not redis_up():
            print("redis did not start")
            return 2

    work = pathlib.Path(tempfile.mkdtemp(prefix="rq_demo_"))
    worker = None
    try:
        shutil.copy(LISTING, work / "queue_worker.py")
        env = dict(os.environ, PYTHONPATH=str(work))
        rq_cli = pathlib.Path(sys.executable).parent / "rq"
        worker = subprocess.Popen(
            [str(rq_cli), "worker", QUEUE],
            cwd=work, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )
        log = worker.stdout
        deadline = time.time() + 15
        while time.time() < deadline:
            line = log.readline()
            if not line:
                break
            if "Listening on" in line:
                break

        spec = importlib.util.spec_from_file_location("queue_worker", work / "queue_worker.py")
        module = importlib.util.module_from_spec(spec)
        sys.path.insert(0, str(work))
        spec.loader.exec_module(module)
        from fastapi.testclient import TestClient

        client = TestClient(module.app)
        submitted = client.post("/analyze/submit", json={"company_name": "Acme Corp"})
        if submitted.status_code != 202:
            print("FAIL: submit returned", submitted.status_code, submitted.text[:200])
            return 1
        job_id = submitted.json()["job_id"]
        print(f"submit: 202, job {job_id}")

        seen = []
        deadline = time.time() + TIMEOUT
        while time.time() < deadline:
            state = client.get(f"/analyze/status/{job_id}").json()
            if not seen or seen[-1] != state["status"]:
                seen.append(state["status"])
                print("  state:", state["status"])
            if state["status"] in ("finished", "failed"):
                break
            time.sleep(1)

        if "finished" not in seen:
            print("FAIL: job did not finish, states:", seen)
            return 1
        result = client.get(f"/analyze/status/{job_id}").json().get("result") or {}
        if result.get("company") != "Acme Corp":
            print("FAIL: unexpected result", result)
            return 1
        print("result:", result)
        print("PASS: queue -> worker -> result")
        return 0
    finally:
        if worker is not None:
            worker.terminate()
            try:
                worker.wait(timeout=10)
            except subprocess.TimeoutExpired:
                worker.kill()
        shutil.rmtree(work, ignore_errors=True)
        if started_redis:
            subprocess.run(["redis-cli", "shutdown", "nosave"], capture_output=True)


if __name__ == "__main__":
    sys.exit(main())
