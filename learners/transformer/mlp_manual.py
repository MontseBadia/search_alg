# -----
# MLP MANUAL
# -----

# Creating explicit tensors and matrix operations
# Autograd computes gradients
# Parameters are updated manually in learning sequence, otherwise SGD
# One update per batch

# Features: [blue, large, rounded, striped]
# Target: blue AND large

import torch
import torch.nn.functional as F


# NOTES:
# Batch dimension is carried along, while matrix multiplication transforms the feature dimension
# Gradients shape matches the params shape
# Binary Cross Entropy averages losses


def set_seeds():
    torch.manual_seed(0)

def initialize_params():
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

    W1 = torch.randn(4, 3, requires_grad=True)
    b1 = torch.zeros(3, requires_grad=True)
    W2 = torch.randn(3, 1, requires_grad=True)
    b2 = torch.zeros(1, requires_grad=True)

    lr = 0.1

    return X, y, W1, b1, W2, b2, lr

def forward(X, W1, b1, W2, b2):
    # Pre-activation hidden neuron
    z1 = X @ W1 + b1
    # Hidden activations
    h = torch.sigmoid(z1)

    # Pre-activation output neuron
    z2 = h @ W2 + b2
    # Activation / Prediction
    return torch.sigmoid(z2)

def update_params(W1, b1, W2, b2, lr):
    # Adding no.grad so that it does not track the parameter update
    with torch.no_grad():
        W1 -= lr * W1.grad
        b1 -= lr * b1.grad
        W2 -= lr * W2.grad
        b2 -= lr * b2.grad

    return W1, b1, W2, b2

# Required so that previous step gradients don't contribute to next update
def clear_out_gradients(W1, b1, W2, b2):
    W1.grad.zero_()
    b1.grad.zero_()
    W2.grad.zero_()
    b2.grad.zero_()

def learning_sequence(X, y, W1, b1, W2, b2, lr):
    # FORWARD PASS -----
    y_hat = forward(X, W1, b1, W2, b2)

    # LOSS -----
    loss = F.binary_cross_entropy(y_hat, y)
    inspect_predictions_and_loss(y_hat, loss)

    # BACKWARD PASS -----
    loss.backward()
    inspect_gradients(W1, b1, W2, b2)

    # UDPATE PARAMS -----
    W1, b1, W2, b2 = update_params(W1, b1, W2, b2, lr)

    # FORWARD PASS -----
    new_y_hat = forward(X, W1, b1, W2, b2)

    # LOSS -----
    new_loss = F.binary_cross_entropy(new_y_hat, y)

    print("\nold loss:", loss.item())
    print("new loss:", new_loss.item())

    # Before the next backward pass, I need to clear out the gradients
    clear_out_gradients(W1, b1, W2, b2)

def train(X, y, W1, b1, W2, b2, optimizer, epochs=100):
    for epoch in range(epochs):
        y_hat = forward(X, W1, b1, W2, b2)
        loss = F.binary_cross_entropy(y_hat, y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        if epoch % 10 == 0: print(f"{epoch}/{epochs} -> loss: {loss.item()}")


# INSPECTION -------

def inspect_gradients(W1, b1, W2, b2):
    print("\nW1.grad")
    print(W1.grad)

    print("\nb1.grad")
    print(b1.grad)

    print("\nW2.grad")
    print(W2.grad)

    print("\nb2.grad")
    print(b2.grad)


def inspect_predictions_and_loss(y_hat, loss):
    print("predictions:")
    print(y_hat)
    print(y_hat.shape)
    print("\nloss:")
    print(loss)
    print(loss.requires_grad, loss.grad_fn)


def print_evaluation(X, W1, b1, W2, b2, y):
    with torch.no_grad():
        y_hat = forward(X, W1, b1, W2, b2)
        # Check whether it reaches threshold and then convert to target type
        predictions = (y_hat >= 0.5).to(y.dtype)
        print("\nprobabilities:", y_hat.flatten())
        print("predictions:", predictions.flatten())
        print("targets:", y.flatten())
        print("correct:", (predictions == y).sum().item(), "/", y.numel())




if __name__ == "__main__":
    # INITIALIZATION -----
    set_seeds()
    X, y, W1, b1, W2, b2, lr = initialize_params()

    # LEARNING SEQUENCE -----
    # learning_sequence(X, y, W1, b1, W2, b2, lr)

    # TRAINING LOOP -----
    optimizer = torch.optim.SGD([W1, b1, W2, b2], lr)
    train(X, y, W1, b1, W2, b2, optimizer, epochs=100)

    # EVALUATION -----
    print_evaluation(X, W1, b1, W2, b2, y)