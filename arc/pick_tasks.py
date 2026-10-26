# Pick the 30 Week 3 tasks.
#
# Pool: ARC-AGI-2 training tasks whose id is not in ARC-AGI-1 (233 of 1000).
# Not evaluation/, that stays unseen for Solver v1 in Week 5.
# Not the 767 old ones, public since 2019, the model has likely memorised them.
#
# Checked once by content, not just id: the 767 shared ids are the old tasks
# with train pairs reordered (766) or lightly edited (1), and none of the 233
# shares a single input/output pair with any ARC-AGI-1 task.
#
# Data: arc/data/ (ARC-AGI-2 repo) and arc/data_agi1/ (ARC-AGI-1 repo).

import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
AGI2_TRAINING = os.path.join(HERE, "data", "data", "training")
AGI1_DIRS = [os.path.join(HERE, "data_agi1", "data", d) for d in ("training", "evaluation")]

SEED = 0
N = 30

# Pilot: only to measure speed, memory, thinking length. Never scored.
PILOT_SEED = 1
PILOT_N = 3

# Fallback from precommit: only if the model solves more than 25/30.
FALLBACK_SEED = 1
FALLBACK_N = 10


def task_ids(folder):
    return {f[:-len(".json")] for f in os.listdir(folder) if f.endswith(".json")}


def new_in_agi2():
    old = set()
    for d in AGI1_DIRS:
        old |= task_ids(d)
    # sorted: listdir order depends on the filesystem, the sample must not
    return sorted(task_ids(AGI2_TRAINING) - old)


def pick(seed=SEED, n=N):
    return sorted(random.Random(seed).sample(new_in_agi2(), n))


# The 203 left after the 30, so pilot tasks never overlap the scored ones.
def remaining():
    return sorted(set(new_in_agi2()) - set(pick()))


def pick_pilot(seed=PILOT_SEED, n=PILOT_N):
    return sorted(random.Random(seed).sample(remaining(), n))


# Excludes the pilot: same seed on the same pool would redraw the pilot tasks
# first, and those were used to tune settings, so they can't be scored.
def pick_fallback(seed=FALLBACK_SEED, n=FALLBACK_N):
    pool = sorted(set(remaining()) - set(pick_pilot()))
    return sorted(random.Random(seed).sample(pool, n))


# Cells the model has to read: train inputs + outputs + test inputs.
# Measured ~2 prompt tokens per cell (7215 tokens for 3600 cells).
def task_cells(task_id):
    with open(os.path.join(AGI2_TRAINING, task_id + ".json")) as f:
        task = json.load(f)
    grids = [p[k] for p in task["train"] for k in ("input", "output")]
    grids += [p["input"] for p in task["test"]]
    return sum(len(g) * len(g[0]) for g in grids)


# ---- Tests ----

if __name__ == "__main__":
    pool = new_in_agi2()
    print("pool size:", len(pool))

    chosen = pick()
    print(f"seed {SEED}, {N} tasks:")
    for t in chosen:
        print(" ", t)

    assert len(pool) == 233
    assert len(set(chosen)) == N
    assert set(chosen) <= set(pool)
    assert pick() == chosen  # same seed, same tasks
    assert pick(seed=1) != chosen

    rest = remaining()
    pilot = pick_pilot()
    print(f"\npilot, seed {PILOT_SEED}, from {len(rest)} remaining:")
    for t in pilot:
        print(f"  {t}  ~{2 * task_cells(t)} prompt tokens")
    biggest = max(rest, key=task_cells)
    print(f"largest remaining: {biggest}  ~{2 * task_cells(biggest)} prompt tokens")

    assert len(rest) == 203
    assert not set(pilot) & set(chosen)
    assert set(pilot) <= set(rest)
    assert pick_pilot() == pilot

    fallback = pick_fallback()
    print(f"\nfallback, seed {FALLBACK_SEED}, only if > 25/30:", " ".join(fallback))
    assert len(set(fallback)) == FALLBACK_N
    assert not set(fallback) & set(pilot)
    assert not set(fallback) & set(chosen)
