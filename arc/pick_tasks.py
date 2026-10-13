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

import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
AGI2_TRAINING = os.path.join(HERE, "data", "data", "training")
AGI1_DIRS = [os.path.join(HERE, "data_agi1", "data", d) for d in ("training", "evaluation")]

SEED = 0
N = 30


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
