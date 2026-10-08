from transformer import MyTransformer
from itertools import product
import torch
from torch import nn
from pathlib import Path
import csv


# NOTES:
# Modulus 7 exercise


def input_and_labels(p):
    pairs = list(product(range(p), repeat=2))

    examples = [[a, b, p] for a, b in pairs]
    targets = [(a + b) % p for a, b in pairs]

    X = torch.tensor(examples, dtype=torch.long)
    y = torch.tensor(targets, dtype=torch.long)

    return X, y

def data_splits(X, y, split_seed=0):
    generator = torch.Generator().manual_seed(split_seed) # Random number generator
    # Create random permuation of the dataset, produces tensor with indices from 0-48 in random order
    perm = torch.randperm(len(X), generator=generator)
    train_size = int(0.7 * len(X)) # Split size
    train_ids = perm[:train_size] # Train indices
    test_ids = perm[train_size:] # Test indices
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
          checkpoint_dir, config, train_idx, test_idx, steps=5000):
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
    if step in (0, 1000, 2000):
        return True
    if 60000 <= step <= 85000:
        return step % 2500 == 0
    return step % 5000 == 0



if __name__ == "__main__":
    SEED = 0
    SPLIT_SEED = 0
    torch.manual_seed(SEED)

    # -- CONFIG -- 
    d_pos = 3
    d_model = 32 # 4
    d_head = 16 # 2
    d_mlp = 64 # 8
    p = 7 # How many possible output logits
    d_voc = p + 1
    lr = 1e-3
    weight_decay = 1e-1

    # -- DATA --
    X, y = input_and_labels(p)

    print(X.shape)
    print(y.shape)

    # for i in range(5):
    #     print(X[i], "->", y[i])

    # -- SPLITS -- 
    X_train, y_train, X_test, y_test, train_idx, test_idx = data_splits(X, y, SPLIT_SEED)

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
        "p": p,
        "d_model": d_model,
        "d_head": d_head,
        "d_mlp": d_mlp,
        "d_voc": d_voc,
        "d_pos": d_pos,
        "lr": lr,
        "weight_decay": weight_decay,
    }

    checkpoint_dir = Path(__file__).resolve().parent / "checkpoints" / f"run_seed_{SEED}"
    checkpoint_dir.mkdir(parents=True, exist_ok=False)

    train(
        X_train, y_train, X_test, y_test, positions,
        transformer, loss_fn, optimizer,
        checkpoint_dir, config, train_idx, test_idx,
        steps=120000
    )
