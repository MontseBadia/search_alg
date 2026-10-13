import sys
from pathlib import Path
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent)) # flat imports from transformer/
from modular_addition import input_and_labels
from no_wrap import load_checkpoint

# Hypotheses (from notes):
# Attention: attention patterns change less than residual representations.
#   -> 5k to 180k inside a run, attention pattern changes less than the final residual
# MLP: the MLP contribution differs more between G and W than the raw attention pattern.
#   -> G vs W at 180k, MLP update differs more than the attention pattern
#
# Updates and residual: change = 1 - linear CKA between the two versions, over all 289
# inputs. CKA compares similarity structure, so it works across runs with different
# bases. 0 = same geometry, 1 = nothing in common.
# Attention pattern: per-input total variation instead, 0 = same weights, 1 = disjoint.
# Tried CKA on it first: the pattern stays ~50/50 on a and b for every input, and CKA
# ignores scale, so it blew those small wiggles up into "0.80 change".

# Conclusion (G vs W, seed 0 split 2, 5k vs 180k, all 289 inputs):
# Attention: supported, with a twist. Where "=" looks barely moves, ~50/50 on a and b
# throughout (TV 0.06 in G) while the final residual changes almost completely (0.79).
# But what attention carries does change (attention update 0.56). Same tokens looked
# at, different thing read from them: the change is in OV, not QK.
# MLP: partly. At 180k G and W attend the same (TV 0.05) but their MLP updates differ
# (0.61), so yes vs the raw pattern. Only a bit more than the attention update (0.55),
# and the MLP gap was already bigger at 5k (0.69), so it doesn't track generalising.
# MLP is the big writer either way, 5-12x the attention update norm.
# TV and 1-CKA are different units, "less" means near unchanged, not a ratio.
# One seed, two checkpoints, train and test mixed.


# -- Pieces at the final position --

# Same steps as MyTransformer.forward, keeping what attention and the MLP each add
@torch.no_grad()
def final_position_pieces(model, X):
    pos = torch.arange(X.shape[1])
    block = model.block

    resid_pre = model.token_embedding(X) + model.position_embedding(pos)
    resid_mid, attention = block.attention(resid_pre)
    mlp_update = block.mlp(resid_mid)

    return {
        "attention pattern": attention[:, -1, :], # where "=" looks: [a, b, =]
        "attention update": (resid_mid - resid_pre)[:, -1, :],
        "mlp update": mlp_update[:, -1, :],
        "final residual": (resid_mid + mlp_update)[:, -1, :],
    }


# -- Linear CKA --

def linear_cka(A, B):
    A = A - A.mean(dim=0)
    B = B - B.mean(dim=0)

    cross = (B.T @ A).norm() ** 2
    return (cross / ((A.T @ A).norm() * (B.T @ B).norm())).item()

# Same input, two attention patterns, how much weight moved
def total_variation(P, Q):
    return (0.5 * (P - Q).abs().sum(dim=1)).mean().item()


# ---- Tests ----
if __name__ == "__main__":
    # Sanity: CKA is 1 for the same thing, also after rotating and scaling it,
    # and low for unrelated noise
    torch.manual_seed(0)
    A = torch.randn(289, 32)
    rotation, _ = torch.linalg.qr(torch.randn(32, 32))
    assert abs(linear_cka(A, A) - 1) < 1e-5
    assert abs(linear_cka(A, 3 * A @ rotation) - 1) < 1e-5
    assert linear_cka(A, torch.randn(289, 32)) < 0.3
    P = torch.tensor([[0.5, 0.5, 0.0]])
    assert total_variation(P, P) == 0
    assert abs(total_variation(P, torch.tensor([[0.0, 0.0, 1.0]])) - 1) < 1e-6

    CHECKPOINTS = Path(__file__).resolve().parent.parent / "checkpoints_p17" / "unordered"
    RUNS = {
        "G": CHECKPOINTS / "wd1.0" / "run_seed_0_split_2",
        "W": CHECKPOINTS / "wd0.1" / "run_seed_0_split_2",
    }
    STEPS = [5000, 180000]
    PIECES = ["attention update", "mlp update", "final residual"] # CKA ones

    X, y = input_and_labels(17)

    pieces = {}
    for run_name, run_dir in RUNS.items():
        for step in STEPS:
            model, checkpoint = load_checkpoint(run_dir / f"step_{step}.pt")
            pieces[run_name, step] = final_position_pieces(model, X)

            # Pieces have to add back up to what the model itself reads
            logits, cache = model(X, torch.arange(3), return_cache=True)
            resid_pre = model.token_embedding(X[:, -1]) + model.position_embedding(torch.tensor(2))
            rebuilt = resid_pre + pieces[run_name, step]["attention update"] + pieces[run_name, step]["mlp update"]
            assert torch.allclose(rebuilt, cache["final_residual"], atol=1e-5)

    print("mean attention from '=' to [a, b, =]")
    for run_name in RUNS:
        for step in STEPS:
            mean = pieces[run_name, step]["attention pattern"].mean(dim=0)
            print(f"  {run_name} {step // 1000:>3}k  " + "  ".join(f"{w:.3f}" for w in mean.tolist()))

    print("\nmean update size at '=' (norm)")
    for run_name in RUNS:
        for step in STEPS:
            p = pieces[run_name, step]
            print(f"  {run_name} {step // 1000:>3}k  attention {p['attention update'].norm(dim=1).mean():6.1f}"
                  f"  mlp {p['mlp update'].norm(dim=1).mean():6.1f}")

    print("\nchange over training, 5k -> 180k")
    print(f"{'':>4} {'pattern (TV)':>14}" + "".join(f" {piece:>18}" for piece in PIECES))
    for run_name in RUNS:
        early, late = pieces[run_name, 5000], pieces[run_name, 180000]
        tv = total_variation(early["attention pattern"], late["attention pattern"])
        changes = [1 - linear_cka(early[piece], late[piece]) for piece in PIECES]
        print(f"{run_name:>4} {tv:>14.3f}" + "".join(f" {c:>18.3f}" for c in changes))

    print("\nG vs W")
    print(f"{'':>4} {'pattern (TV)':>14}" + "".join(f" {piece:>18}" for piece in PIECES))
    for step in STEPS:
        g, w = pieces["G", step], pieces["W", step]
        tv = total_variation(g["attention pattern"], w["attention pattern"])
        diffs = [1 - linear_cka(g[piece], w[piece]) for piece in PIECES]
        print(f"{step // 1000:>3}k {tv:>14.3f}" + "".join(f" {d:>18.3f}" for d in diffs))
