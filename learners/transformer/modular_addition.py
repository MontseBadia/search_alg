from transformer import MyTransformer
from itertools import product
import torch
from torch import nn
from pathlib import Path
import csv
import os
from contextlib import redirect_stdout
from multiprocessing import Pool


# NOTES:
# Modulus 7 exercise


def input_and_labels(p):
    pairs = list(product(range(p), repeat=2))

    examples = [[a, b, p] for a, b in pairs]
    targets = [(a + b) % p for a, b in pairs]

    X = torch.tensor(examples, dtype=torch.long)
    y = torch.tensor(targets, dtype=torch.long)

    return X, y

def data_splits(X, y, split_seed=0, scheme="ordered"):
    generator = torch.Generator().manual_seed(split_seed) # Random number generator

    if scheme == "ordered":
        # Create random permuation of the dataset, produces tensor with indices from 0-48 in random order
        perm = torch.randperm(len(X), generator=generator)
        train_size = int(0.7 * len(X)) # Split size
        train_ids = perm[:train_size] # Train indices
        test_ids = perm[train_size:] # Test indices
    elif scheme == "unordered":
        # Split over unordered pairs, so (a, b) and (b, a) always land on the same side
        # Otherwise the test set can be solved by looking up the mirror pair
        keys = sorted({(min(a, b), max(a, b)) for a, b in X[:, :2].tolist()})
        perm = torch.randperm(len(keys), generator=generator)
        train_keys = {keys[i] for i in perm[:int(0.7 * len(keys))].tolist()} # 70% of unordered pairs, not rows
        in_train = torch.tensor([(min(a, b), max(a, b)) in train_keys for a, b in X[:, :2].tolist()])
        train_ids = in_train.nonzero().squeeze(1)
        test_ids = (~in_train).nonzero().squeeze(1)
    else:
        raise ValueError(f"unknown split scheme: {scheme}")

    X_train, y_train = X[train_ids], y[train_ids] # Train data
    X_test, y_test = X[test_ids], y[test_ids] # Test data

    return X_train, y_train, X_test, y_test, train_ids, test_ids

def accuracy(logits, targets):
    predictions = logits.argmax(dim=-1)

    return (predictions == targets).float().mean()

def print_metrics(step, train_loss, test_loss, train_acc, test_acc, param_norm):
    print(
        f"{step:5d} | "
        f"train loss {train_loss.item():.4f} | "
        f"test loss {test_loss.item():.4f} | "
        f"train acc {train_acc.item():.3f} | "
        f"test acc {test_acc.item():.3f}  | "
        f"param norm {param_norm:.3f}  | "
    )

def evaluate(step, transformer, X_train, y_train, X_test, y_test, positions, loss_fn, history):
    transformer.eval()

    with torch.no_grad():
        train_logits, _ = transformer(X_train, positions)
        test_logits, _ = transformer(X_test, positions)

        train_loss = loss_fn(train_logits, y_train)
        test_loss = loss_fn(test_logits, y_test)

        train_acc = accuracy(train_logits, y_train)
        test_acc = accuracy(test_logits, y_test)

        param_norm = parameter_norm(transformer)

    history["step"].append(step)
    history["train_loss"].append(train_loss.item())
    history["test_loss"].append(test_loss.item())
    history["train_acc"].append(train_acc.item())
    history["test_acc"].append(test_acc.item())
    history["param_norm"].append(param_norm)

    print_metrics(step, train_loss, test_loss, train_acc, test_acc, param_norm)

def train(X_train, y_train, X_test, y_test, positions, transformer, loss_fn, optimizer,
          checkpoint_dir, config, train_idx, test_idx, steps=5000, solved_evals=4):
    history = {
        "step": [],
        "train_loss": [],
        "test_loss": [],
        "train_acc": [],
        "test_acc": [],
        "param_norm": []
    }

    evaluate(0, transformer, X_train, y_train, X_test, y_test, positions, loss_fn, history)
    save_model_checkpoint(
        checkpoint_dir / "step_0.pt",
        transformer, optimizer, 0, config, train_idx, test_idx, history
    )

    solved_count = 0 # Consecutive evaluations with test acc 1.0

    for step in range(1, steps + 1):
        transformer.train()

        train_logits, _ = transformer(X_train, positions)
        train_loss = loss_fn(train_logits, y_train)

        optimizer.zero_grad()
        train_loss.backward()
        optimizer.step()

        # Evaluation
        if checkpoint_step(step) or step == steps:
            evaluate(step, transformer, X_train, y_train, X_test, y_test, positions, loss_fn, history)
            save_model_checkpoint(
                checkpoint_dir / f"step_{step}.pt",
                transformer, optimizer, step, config, train_idx, test_idx, history
            )

            # Early stop on success only
            if history["test_acc"][-1] == 1.0:
                solved_count += 1
            else:
                solved_count = 0

            if solved_count == solved_evals:
                print(f"solved: test acc 1.0 for {solved_evals} evaluations, stopping at step {step}")
                break

    return history

# Gives a scalar giving an intuition of how large weights are overall
def parameter_norm(model):
    total = 0.0

    with torch.no_grad():
        for p in model.parameters():
            total += (p ** 2).sum()

    return total.sqrt().item()

def save_model_checkpoint(path, transformer, optimizer, step, config, train_idx, test_idx, history):
    checkpoint = {
        "step": step,
        "model_state": transformer.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "config": config,
        "train_idx": train_idx,
        "test_idx": test_idx,
        "history": history,
    }
    torch.save(checkpoint, path)
    with path.with_name("history.csv").open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(history.keys())
        writer.writerows(zip(*history.values()))


def checkpoint_step(step):
    return step % 5000 == 0



def run_experiment(SEED, SPLIT_SEED, SPLIT, weight_decay, steps):
    torch.set_num_threads(1) # One thread per process
    torch.manual_seed(SEED)

    # -- CONFIG --
    d_pos = 3
    d_model = 32 # 4
    d_head = 16 # 2
    d_mlp = 64 # 8
    p = 17 # How many possible output logits
    d_voc = p + 1
    lr = 1e-3

    # -- DATA --
    X, y = input_and_labels(p)

    # for i in range(5):
    #     print(X[i], "->", y[i])

    # -- SPLITS --
    X_train, y_train, X_test, y_test, train_idx, test_idx = data_splits(X, y, SPLIT_SEED, SPLIT)

    # -- POSITIONS -- 
    positions = torch.tensor([0, 1, 2])

    # -- INITIALIZERS --
    transformer = MyTransformer(d_model, d_head, d_mlp, d_voc, d_pos, p)
    loss_fn = nn.CrossEntropyLoss()
    # optimizer = torch.optim.SGD(transformer.parameters(), lr=1e-3, weight_decay=1e-2)
    optimizer = torch.optim.AdamW(transformer.parameters(), lr=lr, weight_decay=weight_decay)

    # -- TRAINING --
    config = {
        "init_seed": SEED,
        "split_seed": SPLIT_SEED,
        "split": SPLIT,
        "p": p,
        "d_model": d_model,
        "d_head": d_head,
        "d_mlp": d_mlp,
        "d_voc": d_voc,
        "d_pos": d_pos,
        "lr": lr,
        "weight_decay": weight_decay,
        "steps": steps, # Max steps, a run can stop earlier if solved
    }

    checkpoint_dir = Path(__file__).resolve().parent / "checkpoints_p17" / SPLIT / f"wd{weight_decay}" / f"run_seed_{SEED}_split_{SPLIT_SEED}"
    checkpoint_dir.mkdir(parents=True, exist_ok=False)

    # Each run logs to its own file
    with (checkpoint_dir / "train.log").open("w") as log, redirect_stdout(log):
        history = train(
            X_train, y_train, X_test, y_test, positions,
            transformer, loss_fn, optimizer,
            checkpoint_dir, config, train_idx, test_idx,
            steps=steps
        )

    print(f"done {checkpoint_dir.relative_to(checkpoint_dir.parents[3])} | "
          f"step {history['step'][-1]} | test acc {history['test_acc'][-1]:.3f}")


if __name__ == "__main__":
    # -- GRID --
    SEEDS = [0, 1, 2, 3, 4]
    SPLIT_SEEDS = [0, 1, 2]
    SPLITS = ["unordered"] # "ordered" and/or "unordered"
    WEIGHT_DECAYS = [1e-1, 1.0]
    STEPS = 200000 
    WORKERS = 6 # Parallel runs

    runs = list(product(SEEDS, SPLIT_SEEDS, SPLITS, WEIGHT_DECAYS, [STEPS]))
    print(f"{len(runs)} runs")

    with Pool(WORKERS) as pool:
        pool.starmap(run_experiment, runs)
