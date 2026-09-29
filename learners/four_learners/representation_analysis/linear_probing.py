# Linear Probing
# Question: What information is actually decodable from the hidden representation?
# Conclusion:

# ---------------------------------------
# Experiment 2. Linear Probing
# ---------------------------------------

import math
import random

from neural import train, predict
from learning_setup import SIX_EXAMPLE_DATA, EIGHT_EXAMPLE_DATA, OBJECTS


# ----------------------------------------
# CONFIGURATION
# ----------------------------------------

HIDDEN_SIZE = 3

NETWORK_EPOCHS = 2000
NETWORK_LEARNING_RATE = 0.1

PROBE_EPOCHS = 5000
PROBE_LEARNING_RATE = 0.1

SEED = 7
THRESHOLD = 0.5

CONCEPTS = {
    "blue": lambda x: x[0],
    "large": lambda x: x[1],
    "rounded": lambda x: x[2],
    "striped": lambda x: x[3],
    "blue AND large": lambda x: x[0] and x[1],
}


# ----------------------------------------
# TRAIN ORIGINAL NETWORKS
# ----------------------------------------

def train_network(training_data):
    return train(training_data, epochs=NETWORK_EPOCHS, learning_rate=NETWORK_LEARNING_RATE, seed=SEED, verbose=False, log_every=200)

# Train correct and incorrect network
def train_network_pair():
    wrong_network = train_network(SIX_EXAMPLE_DATA)
    correct_training_data = EIGHT_EXAMPLE_DATA
    correct_network = train_network(correct_training_data)

    return wrong_network, correct_network


# ----------------------------------------
# EXTRACT FROZEN HIDDEN REPRESENTATIONS
# ----------------------------------------

def hidden_representation(network_params, x):
    _, _, hidden = predict(network_params, x, THRESHOLD)

    return hidden


def extract_hidden_values(network_params):
    return { x: hidden_representation(network_params, x) for x in OBJECTS }


def print_hidden_comparison(wrong_hidden, correct_hidden):
    print("\n--- Hidden Representations ---\n")

    for x in OBJECTS:
        print(f"{x} wrong={wrong_hidden[x]} correct={correct_hidden[x]}")


# ----------------------------------------
# LINEAR PROBE
# ----------------------------------------
# Training tiny classifier on top of frozen hidden layer ----- 

def initialize_probe(seed=SEED):
    random.seed(seed)
    weights = [random.uniform(-1, 1) for _ in range(HIDDEN_SIZE)]
    bias = random.uniform(-1, 1)

    return weights, bias

def sigmoid(z):
    return 1 / (1 + math.exp(-z))

# Output layer
def probe_logit(hidden, weights, bias):
    return sum(
        hidden_value * weight
        for hidden_value, weight in zip(hidden, weights)
    ) + bias

def probe_forward(hidden, weights, bias):
    z = probe_logit(hidden, weights, bias)
    return sigmoid(z)

# Train a classifier
def train_probe(hidden_data, labels, epochs=PROBE_EPOCHS, learning_rate=PROBE_LEARNING_RATE):
    weights, bias = initialize_probe()

    for _ in range(epochs):
        for hidden, target in zip(hidden_data, labels):
            prediction = probe_forward(hidden, weights, bias)

            # Sigmoid + BCE gradient
            delta = prediction - target

            # update params
            for i in range(len(weights)):
                weights[i] -= learning_rate * delta * hidden[i]
            bias -= (learning_rate * delta)
    
    return weights, bias

def predict_probe(probe_params, hidden, threshold=THRESHOLD):
    probability = probe_forward(hidden, *probe_params)
    prediction = probability >= threshold
    return probability, prediction


# ----------------------------------------
# CONCEPT HELPERS
# ----------------------------------------

def concept_labels(rule, objects=OBJECTS):
    return [bool(rule(x)) for x in objects]

def hidden_list(hidden_values, objects=OBJECTS):
    return [hidden_values[x] for x in objects]


# ----------------------------------------
# FULL-DATA PROBING
# ----------------------------------------

def full_fit_score(hidden_values, rule):
    labels = concept_labels(rule)
    representations = hidden_list(hidden_values)
    probe_params = train_probe(representations, labels)
    correct = 0

    for x, label in zip(OBJECTS, labels):
        _, prediction = predict_probe(probe_params, hidden_values[x])
        if prediction == label:
            correct += 1

    return correct


def run_full_fit_experiment(wrong_hidden, correct_hidden):
    print("\n--- Full-data Linear Probe ---\n")
    print("concept             wrong network    correct network")

    for concept, rule in CONCEPTS.items():
        wrong_score = full_fit_score(wrong_hidden, rule)
        correct_score = full_fit_score(correct_hidden, rule)

        print(f"{concept:18} {wrong_score}/16             {correct_score}/16")


# ----------------------------------------
# LEAVE-ONE-OUT PROBING
# ----------------------------------------

def leave_one_out_score(hidden_values, rule):
    correct = 0

    for held_out_obj in OBJECTS:
        # 15 objects for training the probe
        train_objects = [x for x in OBJECTS if x != held_out_obj]
        train_hidden = hidden_list(hidden_values, train_objects)
        train_labels = concept_labels(rule, train_objects)

        # Train a fresh probe
        probe_params = train_probe(train_hidden, train_labels)

        # Test only on held-out object hidden representation
        held_out_hidden = (hidden_values[held_out_obj])
        held_out_label = bool(rule(held_out_obj))

        _, prediction = predict_probe(probe_params, held_out_hidden)

        if prediction == held_out_label:
            correct += 1

    return correct

def run_leave_one_out_experiment(wrong_hidden, correct_hidden):
    print("\n--- Leave-One-Out Probe ---\n")
    print("concept             wrong network    correct network")

    for concept, rule in CONCEPTS.items():
        wrong_score = leave_one_out_score(wrong_hidden, rule)
        correct_score = leave_one_out_score(correct_hidden, rule)

        print(f"{concept:18} {wrong_score}/16             {correct_score}/16")




if __name__ == "__main__":
    # Train and freeze both networks
    wrong_network, correct_network = (train_network_pair())

    # Extract representations once
    wrong_hidden = extract_hidden_values(wrong_network)
    correct_hidden = extract_hidden_values(correct_network)

    print_hidden_comparison(wrong_hidden, correct_hidden)

    # Experiment 1: Is the concept linearly separable?
    run_full_fit_experiment(wrong_hidden, correct_hidden)

    # Experiment 2: Does the linear structure generalize?
    run_leave_one_out_experiment(wrong_hidden, correct_hidden)