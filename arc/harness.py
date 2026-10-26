# Week 3 harness: runs the model on ARC tasks, saves and logs every call.
#
# Split by job:
#   prompts.py  task loading, frozen prompt templates, prompt hash
#   server.py   frozen settings, server check, one model call, summary
#   storage.py  saving results, crash records, attempt log
#   harness.py  this file: one call end to end (pilot_call, run_call)
#   scoring.py  parser + scorer
# Still to add: the runner.
#
# Everything used from the terminal is re-exported here, so
# `import harness as h` gives h.server_command(), h.preflight(), h.run_call(),
# h.run_path(), h.VARIANTS as before.
#
# Tests: tests/test_harness.py (all tests: python3 -m unittest discover arc/tests)

import datetime
import os
import urllib.error

from prompts import PROMPT_HASH, PROMPT_VERSION, VARIANTS, build_prompt, load_task, text_sha  # noqa: F401
from server import (MODEL, SERVER, SERVER_URL, SETTINGS, call_model, check_server, now,  # noqa: F401
                    observe_server, preflight, run_info, server_command, summarize)
from storage import crash_path, log_attempt, save_new

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "runs")

SAMPLES = 3
RUN_NAME = "main"


# Shared by pilot_call and run_call: one call, saved whole, summary printed.
# Prints the summary only, never the score: rules get judged blind.
# url is only for tests; pilot_call and run_call always use the real server.
# server: what run_call observed about the running server, logged with the
# result. Checking it is run_call's job, not this function's.
# No lock: the same call started twice by mistake gives a _dup file, not a
# lost or overwritten one, and precommit says only the first completed
# attempt counts (attempts.jsonl shows which). Returns the saved path.
def call_and_save(task_id, variant, path, settings, url=SERVER_URL, server=None, **extra):
    if os.path.exists(path):  # check before the call, not after an hour of it
        raise FileExistsError(path)
    info = run_info()  # before the call: what's in place when it starts
    if server:
        info["server_observed"] = server
    prompt = build_prompt(load_task(task_id), variant)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    attempt = f"{os.path.basename(path)[:-len('.json')]}@{datetime.datetime.now():%Y%m%d-%H%M%S-%f}"

    log_attempt(path, {"event": "start", "attempt": attempt, "task_id": task_id, "variant": variant,
                       **extra, "result_path": path, "prompt_sha": text_sha(prompt),
                       "pid": os.getpid(), "server_pid": server["pid"] if server else None, "time": now()})
    try:
        result = call_model(prompt, settings, url=url)
    except BaseException as e:  # refused, Ctrl+C, a bug: log the end, then let it stop things
        # call_model only re-raises URLError for a refused connection: provably never started
        outcome = "unreachable" if isinstance(e, urllib.error.URLError) else "interrupted"
        log_attempt(path, {"event": "end", "attempt": attempt, "outcome": outcome,
                           "detail": f"{type(e).__name__}: {e}", "time": now()})
        raise
    # prompt_sha comes from the exact text sent, nothing read from disk
    result.update(task_id=task_id, variant=variant, run_info=info,
                  prompt_sha=text_sha(prompt), attempt=attempt, **extra)
    saved = path
    if "crash" in result or "bad_response" in result:
        # Beside the result path, never on it: resume skips existing result
        # files, so the call gets rerun next pass. The record stays.
        saved = crash_path(path)
    saved = save_new(saved, result)  # raw first: nothing after this can lose the call
    summary = summarize(result)
    log_attempt(path, {"event": "end", "attempt": attempt, "outcome": summary["outcome"],
                       "seconds": result["seconds"], "saved": saved, "time": now()})
    print(saved, summary)
    return saved


# Pilot only: settings can be overridden, saved to runs/pilot/. Not scored.
def pilot_call(task_id, variant, label, **overrides):
    path = os.path.join(RUNS, "pilot", f"{task_id}_{variant}_{label}.json")
    return call_and_save(task_id, variant, path, {**SETTINGS, **overrides})


def run_path(task_id, variant, sample, run_name=RUN_NAME):
    return os.path.join(RUNS, run_name, f"{task_id}_{variant}_s{sample}.json")


# Scored calls. No overrides on purpose: always the frozen SETTINGS.
# Checks happen before any compute, a typo costs a second, not 20 minutes.
# The server is verified before every scored call, not once per lane: after a
# crash the server gets restarted by hand, and a slightly different command
# then is exactly what this catches. A mismatch is logged and stops the lane.
def run_call(task_id, variant, sample, run_name=RUN_NAME):
    from pick_tasks import pick  # here, not at the top: keeps import silent and cheap
    if task_id not in pick():
        raise ValueError(f"{task_id} is not one of the 30 scored tasks")
    if variant not in VARIANTS:
        raise ValueError(f"unknown variant {variant!r}")
    if sample not in range(1, SAMPLES + 1):
        raise ValueError(f"sample must be 1..{SAMPLES}")
    path = run_path(task_id, variant, sample, run_name)
    observed = observe_server()
    problems = check_server(observed)
    if problems:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        log_attempt(path, {"event": "refused", "result_path": path, "problems": problems,
                           "observed_args": observed["args"], "time": now()})
        raise RuntimeError("server doesn't match the frozen setup:\n  " + "\n  ".join(problems))
    return call_and_save(task_id, variant, path, SETTINGS, server=observed,
                         sample=sample, run_name=run_name)
