import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent)) # flat imports from transformer/
from modular_addition import input_and_labels
from no_wrap import load_checkpoint, checkpoint_paths
from representation import extract_final_residual, geometry_gap

# Hypothesis (from notes): the representation tied to generalising starts changing
# before held-out accuracy peaks.
# As written almost anything gradual passes, so the version tested here:
# the train-test gap (representation.py) reaches half its rise before test accuracy does.
#
# t50 = first step where the 3-checkpoint moving average reaches min + 0.5 * (max - min)
# lead = t50(test acc) - t50(gap), > 0 means the representation moved first

# Conclusion:
# Supported. Gap reaches t50 before test acc in 12/15 wd 1.0 runs (5k-40k steps
# earlier), 3 tied, never after. G: 55k vs 90k.
# Not just graded vs thresholded: same 12 leads vs correct-class probability on test
# (checked outside this file, prob t50 lands within a checkpoint of acc t50).
# 3 of the 12 leads are one checkpoint (5k), close to a tie. W tied, but it barely
# generalises so its t50 is mostly noise. Final residual only, timing not cause.


# -- Series over checkpoints --

def run_series(run_dir, X):
    steps, test_acc, gap = [], [], []

    for path in checkpoint_paths(run_dir):
        model, checkpoint = load_checkpoint(path)
        train = extract_final_residual(model, X[checkpoint["train_idx"], :2])
        test = extract_final_residual(model, X[checkpoint["test_idx"], :2])

        steps.append(checkpoint["step"])
        test_acc.append(checkpoint["history"]["test_acc"][-1])
        gap.append(geometry_gap(train, test)["gap"])

    return steps, test_acc, gap


# -- Halfway step --

# Moving average so one noisy checkpoint can't set t50
def moving_average(values, window=3):
    smoothed = []
    for i in range(len(values)):
        chunk = values[max(0, i - window + 1):i + 1]
        smoothed.append(sum(chunk) / len(chunk))
    return smoothed

def halfway_step(steps, values):
    smoothed = moving_average(values)
    threshold = min(smoothed) + 0.5 * (max(smoothed) - min(smoothed))

    for step, value in zip(steps, smoothed):
        if value >= threshold:
            return step


# ---- Tests ----
if __name__ == "__main__":
    # Sanity: a series that rises at step 30 has t50 at 30 once the average catches up
    toy_steps = [0, 10, 20, 30, 40, 50, 60]
    assert halfway_step(toy_steps, [0, 0, 0, 1, 1, 1, 1]) == 40 # avg at 30 is 1/3, at 40 is 2/3
    # Rise at the very end: smoothed max is only 2/3, so threshold 1/3, reached at 50
    assert halfway_step(toy_steps, [0, 0, 0, 0, 0, 1, 1]) == 50

    CHECKPOINTS = Path(__file__).resolve().parent.parent / "checkpoints_p17" / "unordered"
    X, y = input_and_labels(17)

    RUNS = {
        "G (wd 1.0)": CHECKPOINTS / "wd1.0" / "run_seed_0_split_2",
        "W (wd 0.1)": CHECKPOINTS / "wd0.1" / "run_seed_0_split_2",
    }

    for run_name, run_dir in RUNS.items():
        steps, test_acc, gap = run_series(run_dir, X)

        print(f"\n{run_name}")
        print(f"{'step':>7} {'test acc':>9} {'gap':>7}")
        for step, acc, g in zip(steps, test_acc, gap):
            if step % 10000 == 0 or step == 5000:
                print(f"{step:>7} {acc:>9.3f} {g:>+7.3f}")

        t_acc, t_gap = halfway_step(steps, test_acc), halfway_step(steps, gap)
        print(f"t50 test acc {t_acc}, t50 gap {t_gap}, lead {t_acc - t_gap:+d}")

    # Same lead for every wd 1.0 run, one run can't settle it
    print("\nall wd 1.0 runs")
    print(f"{'run':>22} {'final acc':>9} {'t50 acc':>8} {'t50 gap':>8} {'lead':>8}")
    leads = []
    for run_dir in sorted((CHECKPOINTS / "wd1.0").glob("run_*")):
        steps, test_acc, gap = run_series(run_dir, X)
        t_acc, t_gap = halfway_step(steps, test_acc), halfway_step(steps, gap)
        leads.append(t_acc - t_gap)
        print(f"{run_dir.name:>22} {test_acc[-1]:>9.3f} {t_acc:>8} {t_gap:>8} {t_acc - t_gap:>+8d}")

    ahead = sum(lead > 0 for lead in leads)
    behind = sum(lead < 0 for lead in leads)
    print(f"gap first in {ahead}, acc first in {behind}, tied {len(leads) - ahead - behind}")
