import sys
from pathlib import Path
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent)) # flat imports from transformer/
from transformer import MyTransformer
from modular_addition import input_and_labels

# If the model learns ordinary addition before modular addition, held-out accuracy where a + b < 17 should rise earlier than accuracy of a + b >= 17.
# I'll test using checkpoint predictions

# Measure:
# - Accuracy
# - Correct-class logit margin

# Conclusion: (G only, one run)
# Addition-first behavioral hypothesis is not supported by the observed trajectory. There's a small early signal in its favor at 20k, but the subsequent checkpoints contradict the predicted ordering.
# More interestingly, the no-wrap group eventually performs worse than the wrap group.




## -- LOAD CHECKPOINT ----

# Rebuilds the model from the config saved in the checkpoint
def load_checkpoint(path, device="cpu"):
    checkpoint = torch.load(path, map_location=device)
    c = checkpoint["config"]

    model = MyTransformer(c["d_model"], c["d_head"], c["d_mlp"], c["d_voc"], c["d_pos"], c["p"])
    model.load_state_dict(checkpoint["model_state"])
    model.to(device)
    model.eval()

    return model, checkpoint

# Sorted by step number, plain sorting puts step_10000 before step_5000
def checkpoint_paths(run_dir):
    return sorted(Path(run_dir).glob("step_*.pt"), key=lambda path: int(path.stem.split("_")[1]))


## -- WRAP VS NO WRAP ----

@torch.no_grad
def wrap_metrics(model, test_pairs, p=17, device="cpu"):
    model.eval()

    # test_pairs: [N, 2] with columns a and b
    pairs = torch.as_tensor(test_pairs, dtype=torch.long, device=device)
    a, b = pairs[:, 0], pairs[:, 1]
    raw_sum = a + b
    targets = raw_sum % p

    # Creates a tensor with shape a but values p
    equals = torch.full_like(a, p)
    tokens = torch.stack([a, b, equals], dim=1)

    logits, _ = model(tokens, torch.arange(3, device=device)) # Expected: [N, 17]
    assert logits.shape == (len(pairs), p)

    predictions = logits.argmax(dim=1)
    correct = predictions == targets

    # Target tells you which index to pick
    true_logits = logits.gather(1, targets[:, None]).squeeze(1)

    competitors = logits.clone()
    # Sets infinite value for correct target so it gets excluded from max value
    competitors.scatter_(1, targets[:, None], float("-inf"))
    best_wrong = competitors.max(dim=1).values

    margins = true_logits - best_wrong

    result = {}
    for name, mask in [("no_wrap", raw_sum < p), ("wrap", raw_sum >= p)]:
        result[name] = {
            "n": int(mask.sum().item()),
            "accuracy": correct[mask].float().mean().item(),
            "margin": margins[mask].mean().item(),
        }

    return result


if __name__ == "__main__":
    steps = [5000, 20000, 55000, 120000, 180000, 200000]

    print(
        f"{'step':>8} {'NW acc':>9} {'W acc':>9}"
        f" {'gap':>9} {'NW margin':>11} {'W margin':>11}"
    )

    CHECKPOINTS = Path(__file__).resolve().parent.parent / "checkpoints_p17" / "unordered"
    G_RUN = CHECKPOINTS / "wd1.0" / "run_seed_0_split_2"
    W_RUN = CHECKPOINTS / "wd0.1" / "run_seed_0_split_2"

    device="cpu"
    X, y = input_and_labels(17)
        
    for step in steps:
        model, checkpoint = load_checkpoint(G_RUN / f"step_{step}.pt")
        # Returns first and second column only
        test_pairs = X[checkpoint["test_idx"], :2]
        metrics = wrap_metrics(model, test_pairs, p=17, device=device)

        nw = metrics["no_wrap"]
        w = metrics["wrap"]

        print(
            f"{step:8d}"
            f" {nw['accuracy']:9.3f}"
            f" {w['accuracy']:9.3f}"
            f" {nw['accuracy'] - w['accuracy']:9.3f}"
            f" {nw['margin']:11.3f}"
            f" {w['margin']:11.3f}"
        )