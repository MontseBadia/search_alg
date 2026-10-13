import sys
from pathlib import Path
import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parent.parent)) # flat imports from transformer/
from modular_addition import input_and_labels
from no_wrap import load_checkpoint
from representation import extract_final_residual

# Hypothesis (algorithmic, over training time):
# The model first forms the ordinary sum a+b, and only later the mod p answer.
# So test pairs should first sit nearer train pairs with the same raw sum, and later
# nearer train pairs with the same answer, whatever the sum.
# raw preference = sim(same raw sum) - sim(same answer, different raw sum)
#   > 0 sum-like, ~0 or < 0 organised by answer
# Final residual, train vs test. algorithmic_hypothesis.py does the same idea over
# all pairs at three sites (where in depth), this one asks when, on unseen pairs.

# Conclusion (G vs W, seed 0 split 2):
# Not established. At 180k G organises test by answer (raw pref -0.08), W in between
# (+0.03). The +0.18/+0.21 at 5k looks like token size, not a sum: same answer /
# different sum pairs are less similar than random (-0.10, -0.23), and those always
# pair small tokens with large ones. So "mod at the end" yes, "sum first" not shown.
# One seed, only 5k and 180k, 368 comparisons in the key group.

def raw_vs_mod_geometry(train, test, p=17):
    # Center both datasets using the train mean.
    mean = train["residual"].float().mean(dim=0, keepdim=True)

    h_train = F.normalize(
        train["residual"].float() - mean, dim=1
    )
    h_test = F.normalize(
        test["residual"].float() - mean, dim=1
    )

    similarity = h_train @ h_test.T

    train_sum = train["pairs"].sum(dim=1)
    test_sum = test["pairs"].sum(dim=1)

    same_raw = train_sum[:, None] == test_sum[None, :]
    same_mod = (
        train["targets"][:, None] == test["targets"][None, :]
    )

    # Exclude any overlapping operand values.
    a = train["pairs"]
    b = test["pairs"]
    shared_operand = (
        a[:, :, None, None] == b[None, None, :, :]
    ).any(dim=(1, 3))

    valid = ~shared_operand

    groups = {
        "same_raw": valid & same_raw,
        "same_mod_different_raw": valid & same_mod & ~same_raw,
        "different_mod": valid & ~same_mod,
    }

    result = {}
    for name, mask in groups.items():
        values = similarity[mask]
        result[name] = {
            "mean": values.mean().item() if values.numel() else float("nan"),
            "n": values.numel(),
        }

    return result


# ---- Tests ----
if __name__ == "__main__":
    CHECKPOINTS = Path(__file__).resolve().parent.parent / "checkpoints_p17" / "unordered"
    RUNS = {
        "G": CHECKPOINTS / "wd1.0" / "run_seed_0_split_2",
        "W": CHECKPOINTS / "wd0.1" / "run_seed_0_split_2",
    }
    X, y = input_and_labels(17)

    datasets = []
    for run_name, run_dir in RUNS.items():
        for step in [5000, 180000]:
            model, checkpoint = load_checkpoint(run_dir / f"step_{step}.pt")
            train = extract_final_residual(model, X[checkpoint["train_idx"], :2])
            test = extract_final_residual(model, X[checkpoint["test_idx"], :2])
            datasets.append((f"{run_name} {step // 1000}k", train, test))

    for name, train, test in datasets:
        r = raw_vs_mod_geometry(train, test)

        raw = r["same_raw"]["mean"]
        mod = r["same_mod_different_raw"]["mean"]
        other = r["different_mod"]["mean"]

        print(f"\n{name}")
        print(f"  Same raw sum:          {raw:+.3f} (n={r['same_raw']['n']})")
        print(f"  Same mod, different raw:{mod:+.3f} (n={r['same_mod_different_raw']['n']})")
        print(f"  Different mod:         {other:+.3f} (n={r['different_mod']['n']})")
        print(f"  Raw preference:        {raw - mod:+.3f}")
