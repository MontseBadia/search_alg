# Server: the model behind mlx_vlm.server, its frozen settings, checking what
# is actually running, and one model call.
#
# The server is started separately, by pasting server_command(), so the
# logged config is the one actually run.
#
# Tests: tests/test_server.py

import datetime
import glob
import json
import os
import subprocess
import time
import urllib.error
import urllib.request

from prompts import PROMPT_HASH, PROMPT_VERSION

HERE = os.path.dirname(os.path.abspath(__file__))

SERVER_URL = "http://localhost:8080/v1/chat/completions"
MODEL = "mlx-community/Qwen3.8-27B-4bit"

# Server-side settings. Not in the request, so logged separately.
# kv_bits changes the computation, it has to be on record.
# max_num_seqs: requests decoded together. Weights are read once per step for
# all of them, so 2 at once ~ nearly double throughput. Capped at 2: each one
# adds its own KV cache, and 2 of the largest tasks wouldn't fit in memory.
SERVER = {"port": 8080, "kv_bits": 8, "prefill_step_size": 512, "max_num_seqs": 2}

HF_MODEL_DIR = os.path.expanduser(
    "~/.cache/huggingface/hub/models--" + MODEL.replace("/", "--"))
VENV = os.path.join(HERE, ".venv")

# All request settings in one place. The server silently accepts unknown
# fields, so a typo here would just be ignored: keep names exact.
# Frozen in precommit (19 October 2026), values from the pilot.
# thinking_budget: server forces "</think>" at N thinking tokens, the model
# then has to answer with what it has (like a time limit). Without it, long
# thinking just hits max_tokens and there's no answer at all.
# max_tokens = budget + room for answers (30x30 grid ~1800 tokens, up to 2 tests).
SETTINGS = {
    "temperature": 1.0,
    "top_p": 0.95,
    "top_k": 20,  # server default is 0 = off, must be sent
    "enable_thinking": True,
    "reasoning_effort": "medium",
    "thinking_budget": 16000,
    "max_tokens": 22000,
}


def now():
    return datetime.datetime.now().isoformat(timespec="seconds")


def server_command():
    return (f"mlx_vlm.server --model {MODEL} --port {SERVER['port']} "
            f"--kv-bits {SERVER['kv_bits']} --prefill-step-size {SERVER['prefill_step_size']} "
            f"--max-num-seqs {SERVER['max_num_seqs']}")


# Read from disk, stdlib only: the harness runs outside the venv.
# HF repos can be updated under the same name, so the snapshot hash matters.
def model_revision():
    try:
        with open(os.path.join(HF_MODEL_DIR, "refs", "main")) as f:
            return f.read().strip()
    except OSError:
        return None


def mlx_vlm_version():
    found = glob.glob(os.path.join(VENV, "lib", "python*", "site-packages", "mlx_vlm-*.dist-info"))
    return os.path.basename(found[0])[len("mlx_vlm-"):-len(".dist-info")] if found else None


def run_info():
    return {"model": MODEL, "model_revision": model_revision(), "mlx_vlm": mlx_vlm_version(),
            "server": dict(SERVER),  # a copy: the logged dict can't be changed afterwards
            "prompt_version": PROMPT_VERSION, "prompt_hash": PROMPT_HASH}


# What the server is actually running with, observed, not declared.
# /health doesn't report kv-bits, prefill step or max-num-seqs, so read the
# server process's own command line: lsof finds who listens on the port, ps
# gives its exact arguments (-ww: unlimited width, otherwise ps can cut long
# command lines and the last flags). The pid changes when the server is
# restarted, so it also shows restarts between calls. Raises if nothing is
# listening. Full tool paths: always there on macOS.
def observe_server(port=SERVER["port"]):
    pids = subprocess.run(["/usr/sbin/lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN", "-t"],
                          capture_output=True, text=True).stdout.split()
    for pid in pids:
        args = subprocess.run(["/bin/ps", "-ww", "-o", "args=", "-p", pid],
                              capture_output=True, text=True).stdout.strip()
        if "mlx_vlm" in args:
            with urllib.request.urlopen(f"http://localhost:{port}/health", timeout=10) as r:
                health = json.loads(r.read())
            return {"pid": int(pid), "args": args, "health": health}
    raise RuntimeError(f"no mlx_vlm server listening on port {port} (listening pids: {pids})")


# Observed vs frozen. Returns a list of mismatches, empty = OK.
# The server is always started by pasting server_command(), so the running
# command line must end with exactly that (ps shows the python + full path in
# front). Any difference counts, order and spacing too.
# /health covers what the command line can't show: the model actually loaded,
# and prefix caching (switchable by environment variable, invisible in args).
def check_server(observed):
    problems = []
    if not observed["args"].endswith(server_command()):
        problems.append(f"command differs\n    running: {observed['args']}\n    frozen:  {server_command()}")
    health = observed.get("health", {})
    if MODEL not in str(health.get("loaded_model")):
        problems.append(f"loaded model {health.get('loaded_model')!r}, frozen {MODEL!r}")
    if health.get("apc_enabled"):
        problems.append("prefix caching (APC) is on, not in the frozen setup")
    return problems


# For a manual check before starting lanes: prints what's running and any mismatch.
def preflight():
    observed = observe_server()
    problems = check_server(observed)
    print("server:", {k: observed[k] for k in ("pid", "args")})
    print("health:", observed["health"])
    print("OK, matches the frozen setup" if not problems else "MISMATCH:\n  " + "\n  ".join(problems))
    return problems


# Settings first: they can't override model or messages.
# None means "not set": the field is left out, not sent as null.
def request_body(prompt, settings=SETTINGS):
    set_only = {k: v for k, v in settings.items() if v is not None}
    return {**set_only, "model": MODEL, "messages": [{"role": "user", "content": prompt}]}


# One call, no retries. Long timeout, a call can think for most of an hour.
# Failures classified by stage, not by exception type (a named list had holes):
# - connection refused (nothing listening): the only case that proves the
#   model never started. Re-raised, the lane stops
# - failed while sending (urllib wraps it in URLError: timeout, reset): the
#   server may already have the request and be generating, so not "never
#   started". A "crash" with stage "send", rerun (precommit). No need to stop
#   the lane: if the server is really down, the server check before the next
#   call stops it
# - connected, no complete reply (server died mid-generation, cut-off body,
#   garbage reply, timeout): anything raised while waiting or reading is a
#   "crash" with stage "reply", rerun
# - complete reply: HTTP error status -> "error" (server's explanation kept);
#   valid JSON -> "response"; not JSON -> "bad_response", raw text kept
# Raw bytes first, JSON second: a decode failure can't lose what arrived.
# Ctrl+C (KeyboardInterrupt) isn't an Exception, so it still stops everything.
def call_model(prompt, settings=SETTINGS, url=SERVER_URL, timeout=4 * 3600):
    body = request_body(prompt, settings)
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    result = {"request": body, "started": now()}
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
    except urllib.error.HTTPError as e:  # before URLError: it's a subclass
        try:
            err_body = e.read().decode(errors="replace")
        except Exception as read_err:
            err_body = f"<error body unreadable: {read_err!r}>"
        result["error"] = {"status": e.code, "body": err_body}
    except urllib.error.URLError as e:
        if isinstance(e.reason, ConnectionRefusedError):
            raise
        reason = e.reason if isinstance(e.reason, BaseException) else e
        result["crash"] = {"type": type(reason).__name__, "detail": str(e), "stage": "send"}
    except Exception as e:
        result["crash"] = {"type": type(e).__name__, "detail": str(e), "stage": "reply"}
    else:
        try:
            result["response"] = json.loads(raw)
        except ValueError as e:
            result["bad_response"] = {"detail": str(e), "raw": raw.decode(errors="replace")}
    result["seconds"] = round(time.time() - start, 1)
    return result


# The fields that matter from one call. Thinking comes back in
# reasoning_content, the answer in content.
# maybe_forced is a heuristic: the server only reports total generated tokens,
# so total >= budget means thinking probably hit it. Exact count needs the
# tokenizer (venv), done later in scoring.
# Never raises: an odd response (error object, missing field) gets a note
# instead, the raw response is what counts.
def summarize(result):
    if "crash" in result:
        return {"outcome": "crash", "crash": result["crash"]["type"], "seconds": result["seconds"]}
    if "bad_response" in result:
        return {"outcome": "bad_response", "bad_response": result["bad_response"]["detail"][:100],
                "seconds": result["seconds"]}
    if "error" in result:
        return {"outcome": "error", "http_error": result["error"]["status"], "seconds": result["seconds"],
                "error_body": result["error"]["body"][:200]}
    try:
        msg = result["response"]["choices"][0]["message"]
        usage = result["response"]["usage"]
        budget = result["request"].get("thinking_budget")
        return {
            "outcome": "response",
            "finish_reason": result["response"]["choices"][0]["finish_reason"],
            "prompt_tokens": usage["prompt_tokens"],
            "completion_tokens": usage["completion_tokens"],
            "seconds": result["seconds"],
            "thinking_chars": len(msg.get("reasoning_content") or ""),
            "answer_chars": len(msg.get("content") or ""),
            "maybe_forced": budget is not None and usage["completion_tokens"] >= budget,
        }
    except (KeyError, IndexError, TypeError) as e:
        return {"outcome": "response" if "response" in result else "unknown", "summary_error": repr(e)}
