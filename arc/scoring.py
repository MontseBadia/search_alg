# Parser + scorer for model answers. Pure: no server, no model, so old logs
# can be rescored any time, and Week 5's solver can reuse score().
#
# Parser: takes the ANSWER text (content, never the thinking) and reads the
# last N code blocks, N = number of test inputs. Last, not first: the model
# sometimes writes intermediate grids before the final one (afe3afe9).
#
# Mildly lenient: digits separated by spaces or commas, and a row of bare
# digits ("012") is split per digit. Anything else is a format failure with a
# reason, never a guess.
#
# Scorer: exact match per test input, solved only if all match (precommit).
# Shape and matching cells are diagnostics only, never partial credit.

import re

CODE_BLOCK = re.compile(r"```[^\n]*\n(.*?)```", re.S)


def parse_grid(block):
    rows = []
    for line in block.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        tokens = [t for t in re.split(r"[\s,]+", line) if t]
        if len(tokens) == 1 and len(tokens[0]) > 1:
            tokens = list(tokens[0])  # "012" -> 0 1 2
        if not all(len(t) == 1 and t in "0123456789" for t in tokens):
            raise ValueError(f"not digits 0-9: {line[:40]!r}")
        rows.append([int(t) for t in tokens])
    if not rows:
        raise ValueError("empty block")
    if len({len(r) for r in rows}) != 1:
        raise ValueError("ragged rows")
    return rows


# Returns (grids, None) or (None, reason).
def parse_answer(content, n_tests):
    if not content or not content.strip():
        return None, "no answer text"
    blocks = CODE_BLOCK.findall(content)
    if len(blocks) < n_tests:
        return None, f"{len(blocks)} code block(s) for {n_tests} test input(s)"
    try:
        return [parse_grid(b) for b in blocks[-n_tests:]], None
    except ValueError as e:
        return None, str(e)


def shape(grid):
    return (len(grid), len(grid[0]))


# One model answer against a task. finish_reason "length" with no answer
# means it hit max_tokens: format failure, outcome 1 in precommit.
def score(task, content, finish_reason=None):
    tests = task["test"]
    grids, reason = parse_answer(content, len(tests))
    if grids is None:
        if finish_reason == "length":  # cut off: say so, it's not a formatting mistake
            reason = ("hit max_tokens, no answer" if not (content or "").strip()
                      else f"hit max_tokens mid-answer ({reason})")
        return {"auto_outcome": "format failure", "format_reason": reason, "per_test": []}
    per_test = []
    for got, pair in zip(grids, tests):
        want = pair["output"]
        same_shape = shape(got) == shape(want)
        per_test.append({
            "exact": got == want,
            "shape": shape(got),
            "expected_shape": shape(want),
            "cells_match": (sum(a == b for r1, r2 in zip(got, want) for a, b in zip(r1, r2))
                            if same_shape else None),
            "cells_total": len(want) * len(want[0]),
        })
    solved = all(t["exact"] for t in per_test)
    return {"auto_outcome": "solved" if solved else "wrong grid",
            "format_reason": None, "per_test": per_test}


# Convenience for a saved result file (pilot or runner).
# A crash (server died mid-call) is not the model's outcome: never scored,
# the call gets rerun (precommit).
def score_result(task, result):
    if "crash" in result:
        return {"auto_outcome": "crash, rerun", "format_reason": result["crash"]["type"], "per_test": []}
    if "bad_response" in result:  # reply arrived but wasn't JSON: infrastructure, not the model
        return {"auto_outcome": "crash, rerun", "format_reason": "bad response", "per_test": []}
    # Metal out of memory: the machine failed, not the model (two calls over the 45000 concurrency limit).
    if "error" in result and "Insufficient Memory" in result["error"].get("body", ""):
        return {"auto_outcome": "crash, rerun", "format_reason": "out of memory", "per_test": []}
    if "error" in result:
        return {"auto_outcome": "format failure",
                "format_reason": f"server error {result['error']['status']}", "per_test": []}
    choice = result["response"]["choices"][0]
    return score(task, choice["message"].get("content"), choice.get("finish_reason"))


# ---- Pilot summary ----
# Tests are in tests/test_scoring.py. This just rescores the real pilot files.

if __name__ == "__main__":
    import json
    import os
    from harness import load_task, RUNS

    print("pilot files:")
    for name in sorted(os.listdir(os.path.join(RUNS, "pilot"))):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(RUNS, "pilot", name)) as f:
            result = json.load(f)
        s = score_result(load_task(result["task_id"]), result)
        print(f"  {name:36} {s['auto_outcome']:15} {s['format_reason'] or ''}",
              [(t["shape"], t["expected_shape"], t["cells_match"], t["cells_total"]) for t in s["per_test"]])
