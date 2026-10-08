from transformer import MyTransformer
from itertools import product
import torch
from torch import nn
from pathlib import Path


# NOTES:
# Modulus 7 exercise


def input_and_labels(p):
    pairs = list(product(range(p), repeat=2))

    examples = [[a, b, p] for a, b in pairs]
    targets = [(a + b) % p for a, b in pairs]

    X = torch.tensor(examples, dtype=torch.long)
    y = torch.tensor(targets, dtype=torch.long)

    return X, y

def data_splits(X, y):
    generator = torch.Generator().manual_seed(0) # Random number generator
    # Create random permuation of the dataset, produces tensor with indeces from 0-48 in random order
    perm = torch.randperm(len(X), generator=generator)
    train_size = int(0.7 * len(X)) # Split size
    train_ids = perm[:train_size] # Train indices
    test_ids = perm[train_size:] # Test indices
    X_train, y_train = X[train_ids], y[train_ids] # Train data
    X_test, y_test = X[test_ids], y[test_ids] # Test data

    return X_train, y_train, X_test, y_test

def accuracy(logits, targets):
    predictions = logits.argmax(dim=-1)

    return (predictions == targets).float().mean()

def train(X_train, y_train, X_test, y_test, positions, transformer, loss_fn, optimizer, steps=5000):
    history = {
        "train_loss": [],
        "test_loss": [],
        "train_acc": [],
        "test_acc": [],
        "param_norm": []
    }

    for step in range(steps + 1):
        transformer.train()

        train_logits, _ = transformer(X_train, positions)
        train_loss = loss_fn(train_logits, y_train)

        optimizer.zero_grad()
        train_loss.backward()
        optimizer.step()

        # Evaluation
        if step % 5000 == 0:
            transformer.eval()

            with torch.no_grad():
                train_logits, _ = transformer(X_train, positions)
                test_logits, _ = transformer(X_test, positions)

                train_loss = loss_fn(train_logits, y_train)
                test_loss = loss_fn(test_logits, y_test)

                train_acc = accuracy(train_logits, y_train)
                test_acc = accuracy(test_logits, y_test)

                param_norm = parameter_norm(transformer)

            history["train_loss"].append(train_loss.item())
            history["test_loss"].append(test_loss.item())
            history["train_acc"].append(train_acc.item())
            history["test_acc"].append(test_acc.item())
            history["param_norm"].append(param_norm)

            print(
                f"{step:5d} | "
                f"train loss {train_loss.item():.4f} | "
                f"test loss {test_loss.item():.4f} | "
                f"train acc {train_acc.item():.3f} | "
                f"test acc {test_acc.item():.3f}  | "
                f"param norm {param_norm:.3f}  | "
            )

    return history

# Gives a scalar giving an intuition of how large weights are overall
def parameter_norm(model):
    total = 0.0

    with torch.no_grad():
        for p in model.parameters():
            total += (p ** 2).sum()

    return total.sqrt().item()

def save_model_checkpoint(model):
    torch.save(model.state_dict(), CHECKPOINT_PATH)



if __name__ == "__main__":
    torch.manual_seed(0)

    # -- CONFIG -- 
    d_pos = 3
    d_model = 32 # 4
    d_head = 16 # 2
    d_mlp = 64 # 8
    p = 7 # How many possible output logits
    d_voc = p + 1

    # -- DATA -- 
    X, y = input_and_labels(p)

    print(X.shape)
    print(y.shape)

    # for i in range(5):
    #     print(X[i], "->", y[i])

    # -- SPLITS -- 
    X_train, y_train, X_test, y_test = data_splits(X, y)

    # -- POSITIONS -- 
    positions = torch.tensor([0, 1, 2])

    # -- INITIALIZERS --
    transformer = MyTransformer(d_model, d_head, d_mlp, d_voc, d_pos, p)
    loss_fn = nn.CrossEntropyLoss()
    # optimizer = torch.optim.SGD(transformer.parameters(), lr=1e-3, weight_decay=1e-2)
    optimizer = torch.optim.AdamW(transformer.parameters(), lr=1e-3, weight_decay=1e-1)

    # -- TRAINING --
    train(X_train, y_train, X_test, y_test, positions, transformer, loss_fn, optimizer, steps=120000)

    CHECKPOINT_PATH = Path(__file__).resolve().parent / "transformer_seed_0_steps_120_000.pt"
    save_model_checkpoint(transformer)