# Week 3 analysis: scores sample 1 and joins it with the blind judgments.
# Running it on runs/main unblinds the per-task scores, so only after
# judgments.csv is final.
#
# Numbers are the pre-registered ones (precommit), every pass@2 threshold
# read on s1 pass@1 (Changes, 29 Oct):
#   - pass@1 per variant vs predictions and my 29/30
#   - near zero (<= 2/30 in each variant) -> variant comparison on components
#   - outcome distribution, components, shape correct, cells correct
#   - difficulty 1-2 vs 4-5 within 20 points
#   - maybe_forced against solved

import csv
import json
import os
import re
from collections import Counter

from harness import load_task, run_path
from scoring import score_result
from server import summarize

HERE = os.path.dirname(os.path.abspath(__file__))
JUDGMENTS = os.path.join(HERE, "runs", "main", "judgments.csv")
HAND_LOG = os.path.join(HERE, "notes", "hand_solving_log.md")

VARIANTS = ("text", "rule_first")
PREDICTED = {"text": 15, "rule_first": 20}  # pass@2 predictions, read on pass@1
HUMAN = 29
ORDER = ["format failure", "solved", "perception", "got rule", "partial",
         "underdetermined", "wrong", "unresolved"]


def load_judgments(path=JUDGMENTS):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


# "### Task id: X" ... "- difficulty 1-5: N"
def load_difficulty(path=HAND_LOG):
    difficulty, task = {}, None
    with open(path) as f:
        for line in f:
            m = re.match(r"### Task id: (\w+)", line)
            if m:
                task = m.group(1)
            m = re.match(r"- difficulty 1-5: (\d)", line)
            if m and task:
                difficulty[task] = int(m.group(1))
    return difficulty


def load_result(task_id, variant):
    with open(run_path(task_id, variant, 1)) as f:
        return json.load(f)


# Format failure and solved come from the score and go first in the order,
# the rest is the blind judgment.
def final_outcome(judged, auto):
    if auto in ("format failure", "solved"):
        return auto
    return judged


# One row per judgment. Loaders passed in so this runs without runs/main.
def join(judgments, difficulty, load_result=load_result, load_task=load_task):
    rows = []
    for j in judgments:
        result = load_result(j["task"], j["variant"])
        s = score_result(load_task(j["task"]), result)
        if s["auto_outcome"] == "crash, rerun":  # a crash at the result path means a missed rename
            raise ValueError(f"{j['task']} {j['variant']}: crash at the result path")
        comps = [int(c) for c in j["components"].split()]
        rows.append({
            "task": j["task"], "variant": j["variant"],
            "judged": j["outcome"], "auto": s["auto_outcome"],
            "outcome": final_outcome(j["outcome"], s["auto_outcome"]),
            "components": sum(comps) / len(comps),
            "tags": [t for t in j["tags"].split(";") if t],
            "per_test": s["per_test"],
            "maybe_forced": summarize(result).get("maybe_forced", False),
            "difficulty": difficulty.get(j["task"]),
        })
    return rows


def pct(k, n):
    return f"{k}/{n} ({100 * k / n:.0f}%)" if n else "0/0"


def report(rows):
    out = []
    by_variant = {v: [r for r in rows if r["variant"] == v] for v in VARIANTS}
    solved = {v: sum(r["outcome"] == "solved" for r in rs) for v, rs in by_variant.items()}

    out.append("== pass@1 (sample 1)")
    for v, rs in by_variant.items():
        out.append(f"  {v:10} {pct(solved[v], len(rs))}   predicted {PREDICTED[v]}/30, me {HUMAN}/30")
    near_zero = all(k <= 2 for k in solved.values())
    out.append(f"  near zero (<= 2/30 in each): {near_zero}"
               + ("  -> compare on components + outcomes" if near_zero else "  -> compare on accuracy"))
    surprising = [v for v, k in solved.items() if k < 5 or k > 25]
    out.append(f"  surprising (< 5 or > 25): {surprising or 'none'}")
    if any(k > 25 for k in solved.values()):
        out.append("  > 25/30: add 10 more tasks (pick_fallback)")

    out.append("\n== outcomes (final)")
    for v, rs in by_variant.items():
        c = Counter(r["outcome"] for r in rs)
        out.append(f"  {v:10} " + ", ".join(f"{o} {c[o]}" for o in ORDER if c[o]))

    out.append("\n== rule components (mean fraction)")
    for v, rs in by_variant.items():
        out.append(f"  {v:10} {sum(r['components'] for r in rs) / len(rs):.2f}")

    # Shape: per answer, all test outputs the right size. Cells: pooled over
    # right-size test outputs. Diagnostic only, never credit.
    out.append("\n== shape correct / cells correct (answers with a grid)")
    for v, rs in by_variant.items():
        answered = [r for r in rs if r["per_test"]]
        right = [r for r in answered if all(t["shape"] == t["expected_shape"] for t in r["per_test"])]
        tests = [t for r in answered for t in r["per_test"] if t["cells_match"] is not None]
        cells = sum(t["cells_match"] for t in tests) / sum(t["cells_total"] for t in tests) if tests else 0
        out.append(f"  {v:10} shape {pct(len(right), len(answered))}, cells {cells:.2f}")

    out.append("\n== difficulty (mine): 1-2 vs 4-5, prediction within 20 points")
    for v, rs in by_variant.items():
        easy = [r for r in rs if r["difficulty"] in (1, 2)]
        hard = [r for r in rs if r["difficulty"] in (4, 5)]
        e = sum(r["outcome"] == "solved" for r in easy)
        h = sum(r["outcome"] == "solved" for r in hard)
        gap = 100 * (e / len(easy) - h / len(hard)) if easy and hard else float("nan")
        out.append(f"  {v:10} easy {pct(e, len(easy))}, hard {pct(h, len(hard))}, gap {gap:.0f} points")

    out.append("\n== maybe_forced vs solved")
    for v, rs in by_variant.items():
        f = [r for r in rs if r["maybe_forced"]]
        n = [r for r in rs if not r["maybe_forced"]]
        out.append(f"  {v:10} forced solved {pct(sum(r['outcome'] == 'solved' for r in f), len(f))}, "
                   f"not forced solved {pct(sum(r['outcome'] == 'solved' for r in n), len(n))}")

    out.append("\n== tags")
    for v, rs in by_variant.items():
        c = Counter(t for r in rs for t in r["tags"])
        out.append(f"  {v:10} " + (", ".join(f"{t} {k}" for t, k in c.most_common()) or "none"))

    # Leads for the score-dependent tags, not tags themselves
    out.append("\n== to look at")
    for r in rows:
        if r["outcome"] == "solved" and r["judged"] != "got rule":
            out.append(f"  {r['task']} {r['variant']}: solved, judged {r['judged']} -> right grid, wrong stated rule?")
        if r["judged"] == "got rule" and r["outcome"] not in ("solved", "format failure"):
            out.append(f"  {r['task']} {r['variant']}: got rule, grid wrong -> execution tag")

    out.append("\n== per row")
    for r in rows:
        shapes = " ".join("ok" if t["shape"] == t["expected_shape"] else f"{t['shape']}!={t['expected_shape']}"
                          for t in r["per_test"]) or "-"
        out.append(f"  {r['task']} {r['variant']:10} {r['outcome']:15} judged {r['judged']:9} "
                   f"comp {r['components']:.2f} d{r['difficulty']} {'forced' if r['maybe_forced'] else '':6} {shapes}")
    return "\n".join(out)


if __name__ == "__main__":
    print(report(join(load_judgments(), load_difficulty())))
