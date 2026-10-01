# -----
# MLP PYTORCH
# -----
 
# Replaces explicit params with nn.Linear layers

# Features: [blue, large, rounded, striped]
# Target: blue AND large

from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F


class MLP(nn.Module):
    def __init__(self):
        super().__init__()

        # nn.Linear(in_features, out_features)
        # weight.shape == (out_features, in_features)
        self.layer1 = nn.Linear(4, 3)
        self.layer2 = nn.Linear(3, 1)

    def forward(self, X, analysis=False):
        z1 = self.layer1(X)
        h = torch.sigmoid(z1)

        z2 = self.layer2(h)
        y_hat = torch.sigmoid(z2)

        if analysis:
            return y_hat, h

        return y_hat

def initialize_data():
    X = torch.tensor([
        [1.0, 0.0, 1.0, 0.0],
        [0.0, 1.0, 1.0, 0.0],
        [1.0, 1.0, 0.0, 1.0],
    ])
    y = torch.tensor([
        [0.0],
        [0.0],
        [1.0],
    ])
    return X, y

def inspect_model_params(model):
    print(model.layer1.weight.shape)
    print(model.layer1.bias.shape)
    print(model.layer2.weight.shape)
    print(model.layer2.bias.shape)

    for name, parameter in model.named_parameters():
        print(name, parameter.shape)
    # for params in model.parameters():
    #     print(params)

def inspect_model_state(model):
    state = model.state_dict()
    for name, tensor in state.items():
        print(name, tensor.shape)

def inspect_optimizer_state(optimizer):
    state = optimizer.state_dict()
    print(state)

def train(model, optimizer, X, y, epochs=100):
    for epoch in range(epochs):
        y_hat = model(X)
        loss = F.binary_cross_entropy(y_hat, y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        if epoch % 10 == 0: print(f"{epoch}/{epochs} -> loss: {loss.item()}")

CHECKPOINT_PATH = Path(__file__).resolve().parent / "mlp.pt"

def save_model_checkpoint(model):
    torch.save(model.state_dict(), CHECKPOINT_PATH)

def load_saved_params(model):
    model.load_state_dict(torch.load(CHECKPOINT_PATH))

def print_evaluation(model, X, y):
    with torch.no_grad():
        y_hat = model(X)
        predictions = (y_hat >= 0.5).to(y.dtype)
        print("\nprobabilities:", y_hat.flatten())
        print("predictions:", predictions.flatten())
        print("targets:", y.flatten())
        print("correct:", (predictions == y).sum().item(), "/", y.numel())
    




if __name__ == "__main__":
    # INITIALIZATION -----
    torch.manual_seed(0)
    X, y = initialize_data()

    # MODEL -----
    model = MLP()
    inspect_model_params(model)

    # OPTIMIZER -----
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)

    # TRAINING LOOP -----
    train(model, optimizer, X, y)

    # INSPECTION -----
    print_evaluation(model, X, y)
    inspect_model_state(model)
    save_model_checkpoint(model)
    inspect_optimizer_state(optimizer)

    new_model = MLP()
    print(model(X))
    print(new_model(X))

    # LOAD SAVED CHECKPOINT -----
    load_saved_params(new_model)
    print(torch.allclose(model(X), new_model(X))) # Should return True

    y_hat, h = model(X, analysis=True)
    print("\npredictions:")
    print(y_hat)
    print("hidden activations:")
    print(h)
    print("hidden shape:", h.shape)
