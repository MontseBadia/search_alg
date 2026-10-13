import sys
from pathlib import Path
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent)) # flat imports from transformer/
from modular_addition import input_and_labels
from no_wrap import load_checkpoint

# Hypothesis (causal, from notes): some computation in the wd=1.0 model matters more
# for held-out examples than for training ones, and removing it hurts generalising most.
# Here: knock out attention or the MLP at "=" in G 180k and W 180k, compare the drop in
# train / test accuracy and correct-class margin against each model's own baseline.
#
# Conditions, all at the final position only:
#   baseline         final = pre + attn + mlp(pre + attn)
#   zero attention   final = pre + mlp(pre). One layer, so attention is the only way a and b
#                    reach "=". Every input looks the same, must collapse to one answer.
#                    Sanity anchor, not a finding.
#   no direct attn   final = pre + mlp(pre + attn). MLP still reads attention, the classifier
#                    just doesn't get attention's output directly.
#   zero mlp         final = pre + attn
#   mean mlp         final = pre + attn + mean over inputs of mlp. Less off-distribution than
#                    zero, if both agree the result isn't just an artefact of zeroing.
#
# Component dependence, not proof that this component implements the algorithm.

# Conclusion (G 180k vs W 180k, seed 0 split 2):
# Not supported at component level. Zero or mean MLP sends G to chance on train and
# test alike (train -0.93, test -0.89), W loses everything too (test 0.37 -> 0.00).
# Total dependence, not selective, so it can't tell memorising from generalising.
# Zero and mean agree, so not just an artefact of zeroing.
# Attention: zeroing it collapses both to one answer, as expected. Removing only its
# direct path costs G 0.02 test and W nothing, the classifier reads it via the MLP.
# W margin deltas are misleading, baseline is confidently wrong (-7.45) so shrinking
# the logits "helps". Trust accuracy.
# One layer means the MLP is the whole computation. Needs neuron or direction ablation.


# -- Interventions --

@torch.no_grad()
def ablated_logits(model, X, condition):
    pos = torch.arange(X.shape[1])
    block = model.block

    embedded = model.token_embedding(X) + model.position_embedding(pos)
    resid_mid, _ = block.attention(embedded)

    pre = embedded[:, -1, :]
    attn = (resid_mid - embedded)[:, -1, :]
    mlp = block.mlp(resid_mid)[:, -1, :]

    if condition == "baseline":
        final = pre + attn + mlp
    elif condition == "zero attention":
        final = pre + block.mlp(pre)
    elif condition == "no direct attn":
        final = pre + mlp
    elif condition == "zero mlp":
        final = pre + attn
    elif condition == "mean mlp":
        final = pre + attn + mlp.mean(dim=0)
    else:
        raise ValueError(f"unknown condition: {condition}")

    return model.classifier(final)

# Same margin as no_wrap.py: correct logit minus best wrong one
def accuracy_and_margin(logits, targets):
    true_logits = logits.gather(1, targets[:, None]).squeeze(1)
    competitors = logits.clone()
    competitors.scatter_(1, targets[:, None], float("-inf"))
    margins = true_logits - competitors.max(dim=1).values

    accuracy = (logits.argmax(dim=1) == targets).float().mean().item()
    return accuracy, margins.mean().item()


# ---- Tests ----
if __name__ == "__main__":
    CHECKPOINTS = Path(__file__).resolve().parent.parent / "checkpoints_p17" / "unordered"
    RUNS = {
        "G": CHECKPOINTS / "wd1.0" / "run_seed_0_split_2" / "step_180000.pt",
        "W": CHECKPOINTS / "wd0.1" / "run_seed_0_split_2" / "step_180000.pt",
    }
    CONDITIONS = ["baseline", "zero attention", "no direct attn", "zero mlp", "mean mlp"]

    X, y = input_and_labels(17)

    for run_name, path in RUNS.items():
        model, checkpoint = load_checkpoint(path)
        splits = {"train": checkpoint["train_idx"], "test": checkpoint["test_idx"]}

        # Baseline has to be the model's own forward, and what training logged
        logits, _ = model(X, torch.arange(3))
        assert torch.allclose(ablated_logits(model, X, "baseline"), logits, atol=1e-5)
        for split, idx in splits.items():
            accuracy, _ = accuracy_and_margin(logits[idx], y[idx])
            assert abs(accuracy - checkpoint["history"][f"{split}_acc"][-1]) < 1e-6

        # Zero attention must give one answer for every input
        assert ablated_logits(model, X, "zero attention").argmax(dim=1).unique().numel() == 1

        print(f"\n{run_name} 180k")
        print(f"{'condition':>15} | {'train acc':>9} {'test acc':>9} | {'train margin':>12} {'test margin':>12}"
              f" | {'d train acc':>11} {'d test acc':>10} {'d test margin':>13}")

        base = {}
        for condition in CONDITIONS:
            logits = ablated_logits(model, X, condition)
            scores = {split: accuracy_and_margin(logits[idx], y[idx]) for split, idx in splits.items()}
            if condition == "baseline":
                base = scores

            print(f"{condition:>15} | {scores['train'][0]:>9.3f} {scores['test'][0]:>9.3f}"
                  f" | {scores['train'][1]:>12.2f} {scores['test'][1]:>12.2f}"
                  f" | {scores['train'][0] - base['train'][0]:>+11.3f}"
                  f" {scores['test'][0] - base['test'][0]:>+10.3f}"
                  f" {scores['test'][1] - base['test'][1]:>+13.2f}")
