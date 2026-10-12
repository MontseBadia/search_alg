import sys
from pathlib import Path
import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parent.parent)) # flat imports from transformer/
from modular_addition import input_and_labels
from no_wrap import load_checkpoint

# Hypothesis:
# The 180k checkpoint organizes examples sharing the same modular answer more consistently than the 5k checkpoint.

# Conclusion (G vs W, seed 0 split 2, final residual, centred cosine):
# Weakly supported. Test moves toward same-answer train in both runs (G 0.07 -> 0.50,
# W -0.03 -> 0.38), so most of it comes with training, not generalising.
# What separates G: test is placed almost as well as train (0.50 vs 0.54), in W
# much less (0.38 vs 0.59), even though W clusters its train more tightly.
# One seed each, final residual partly forced by accuracy. Next: resid_mid, more seeds.


# -- Extract representations --

@torch.no_grad()
def extract_final_residual(model, pairs, p=17, device="cpu"):
    model.eval()

    pairs = torch.as_tensor(
        pairs, dtype=torch.long, device=device
    )

    a, b = pairs[:, 0], pairs[:, 1]

    equals = torch.full_like(a, p)
    X = torch.stack([a, b, equals], dim=1)

    pos = torch.arange(3, device=device).unsqueeze(0)
    # Shape [1, 3], assuming positional embedding broadcasts.

    logits, cache = model(X, pos, return_cache=True)

    return {
        "pairs": pairs.cpu(),
        "targets": ((a + b) % p).cpu(),
        "residual": cache["final_residual"].detach().cpu(),
        "predictions": logits.argmax(dim=-1).cpu(),
    }




def geometry_gap(left, right, same_dataset=False):
    # Centre on the left (train) mean, otherwise the shared "=" offset grows over training
    # and pushes every similarity up, squeezing the gap
    centre = left["residual"].float().mean(dim=0)
    h1 = F.normalize(left["residual"].float() - centre, dim=1)
    h2 = F.normalize(right["residual"].float() - centre, dim=1)

    similarity = h1 @ h2.T

    y1 = left["targets"]
    y2 = right["targets"]
    same_answer = y1[:, None] == y2[None, :]

    p1 = left["pairs"]
    p2 = right["pairs"]

    # Exclude pairs sharing an operand in either position.
    shared_operand = (
        (p1[:, :, None, None] ==
         p2[None, None, :, :])
        .any(dim=(1, 3))
    )

    valid = ~shared_operand

    if same_dataset:
        valid &= torch.triu(
            torch.ones_like(valid, dtype=torch.bool),
            diagonal=1
        )

    same = similarity[valid & same_answer]
    different = similarity[valid & ~same_answer]

    assert same.numel() > 0
    assert different.numel() > 0

    return {
        "same": same.mean().item(),
        "different": different.mean().item(),
        "gap": (same.mean() - different.mean()).item(),
        "n_same": same.numel(),
        "n_different": different.numel(),
    }




# ---- Tests ----
if __name__ == "__main__":
    CHECKPOINTS = Path(__file__).resolve().parent.parent / "checkpoints_p17" / "unordered"
    # W is the control: same seed, same split, same steps, but it barely generalises.
    # If its train-test gap also grows, the G result is about training time, not generalising
    RUNS = {
        "G (wd 1.0)": CHECKPOINTS / "wd1.0" / "run_seed_0_split_2",
        "W (wd 0.1)": CHECKPOINTS / "wd0.1" / "run_seed_0_split_2",
    }

    device = "cpu"
    X, y = input_and_labels(17)

    for run_name, run_dir in RUNS.items():
        print(f"\n{run_name}")

        # -- Extract datasets --

        model_5k, checkpoint_5k = load_checkpoint(run_dir / "step_5000.pt", device)
        model_180k, checkpoint_180k = load_checkpoint(run_dir / "step_180000.pt", device)

        # Same run so same split, pairs come from the checkpoint
        train_pairs = X[checkpoint_5k["train_idx"], :2]
        test_pairs = X[checkpoint_5k["test_idx"], :2]

        train_5k = extract_final_residual(
            model_5k, train_pairs, device=device
        )
        test_5k = extract_final_residual(
            model_5k, test_pairs, device=device
        )

        train_180k = extract_final_residual(
            model_180k, train_pairs, device=device
        )
        test_180k = extract_final_residual(
            model_180k, test_pairs, device=device
        )

        for name, data, checkpoint, key in [
            ("train_5k", train_5k, checkpoint_5k, "train_acc"),
            ("test_5k", test_5k, checkpoint_5k, "test_acc"),
            ("train_180k", train_180k, checkpoint_180k, "train_acc"),
            ("test_180k", test_180k, checkpoint_180k, "test_acc"),
        ]:
            accuracy = (data["predictions"] == data["targets"]).float().mean().item()
            print(
                name,
                "pairs:", tuple(data["pairs"].shape),
                "residual:", tuple(data["residual"].shape),
                f"accuracy: {accuracy:.3f}",
            )
            # Has to match what training logged, otherwise wrong pairs or wrong split
            assert abs(accuracy - checkpoint["history"][key][-1]) < 1e-6

        for step, train, test in [
            (5000, train_5k, test_5k),
            (180000, train_180k, test_180k),
        ]:
            for name, left, right, same_dataset in [
                ("train-train", train, train, True),
                ("train-test", train, test, False),
            ]:
                result = geometry_gap(left, right, same_dataset)

                print(
                    f"{step:6d} {name:11s}"
                    f" same={result['same']:+.3f}"
                    f" different={result['different']:+.3f}"
                    f" gap={result['gap']:+.3f}"
                    f" n=({result['n_same']}, {result['n_different']})"
                )
