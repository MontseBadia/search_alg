# -----
# MLP
# -----

# Tiny Neural Network:
# 4 inputs -> 3 hidden units -> 1 output

# Learning Pipeline:
# 1. Initialize parameters
# 2. Forward pass
# 3. Loss
# 4. Backpropagation
# 5. Gradient check
# 6. Gradient descent
# 7. Training
# 8. Behavioral evaluation
# 9. Seed and evidence-intervention experiments

from learning_setup import OBJECTS, TEST_OBJECTS, TRAINING_DATA, hidden_concept
import random
import math

# --------------------------------------------------
# 1. PARAMETER INITIALIZATION
# --------------------------------------------------

INPUT_SIZE = 4
HIDDEN_SIZE = 3

def sigmoid(z):
    return 1 / (1 + math.exp(-z))

def initialize_parameters(seed=7):
    random.seed(seed)

    # random.uniform returns floating number between specified numbers
    hidden_weights = [[random.uniform(-1, 1) for _ in range(INPUT_SIZE)] for _ in range(HIDDEN_SIZE)]
    hidden_biases = [random.uniform(-1, 1) for _ in range(HIDDEN_SIZE)]
    output_weights = [random.uniform(-1, 1) for _ in range(HIDDEN_SIZE)]
    output_bias = random.uniform(-1, 1)

    return (hidden_weights, hidden_biases, output_weights, output_bias)

# ------------------------------
# 2. FORWARD PASS
# ------------------------------

# Hidden neuron j:
#   z_j = sum_i x_i * w_ji + b_j
#   h_j = sigmoid(z_j)
#
# Output neuron:
#   z_o = sum_j h_j * v_j + b_o
#   prediction = sigmoid(z_o)

# Returns pre-activation z values for a layer
def linear_layer(x, weights, biases):
    return [
        sum(
            input_value * weight
            for input_value, weight in zip(x, neuron_weights)
        ) + bias
        for neuron_weights, bias in zip(weights, biases)
    ]

# Returns single output neuron pre-activation z value
def output_layer(h, weights, bias):
    return sum(
        input_value * weight
        for input_value, weight in zip(h, weights)
    ) + bias

# Runs one input through the network and keeps values needed by backprop
def forward(x, hidden_weights, hidden_biases, output_weights, output_bias):
    # hidden_z are weighted sums before nonlinearity
    hidden_z = linear_layer(x, hidden_weights, hidden_biases)
    hidden = [sigmoid(z) for z in hidden_z]

    output_z = output_layer(hidden, output_weights, output_bias)
    prediction = sigmoid(output_z)

    return {
        "hidden_z": hidden_z,
        "hidden": hidden,
        "output_z": output_z,
        "prediction": prediction
    }

# -----------------------------------
# 3. LOSS
# -----------------------------------
# We use binary cross-entropy because the target is Boolean and the output is sigmoid.

# Alternative loss kept for comparison
def squared_error(prediction, ground_truth):
    return (ground_truth - prediction) ** 2

def binary_cross_entropy(prediction, ground_truth):
    # clamp so we don't get undefined when prediction == 1 or prediction == 0
    epsilon = 1e-12
    prediction = min(max(prediction, epsilon), 1 - epsilon)

    return -(ground_truth * math.log(prediction)
             + (1 - ground_truth) * math.log(1 - prediction))

def compute_loss(x, ground_truth, hidden_weights, hidden_biases, output_weights, output_bias):
    result = forward(x, hidden_weights, hidden_biases, output_weights, output_bias)

    return binary_cross_entropy(result["prediction"], ground_truth)

# ---------------------------------------------
# 4. BACKPROPAGATION
# ---------------------------------------------

# Backprop = efficient credit assignment through the computation graph
# It computes one gradient for every trainable parameter

def backward(x, ground_truth, forward_result, output_weights):
    prediction = forward_result["prediction"]
    hidden = forward_result["hidden"]

    output_delta = prediction - ground_truth
    output_weight_grads = [
        output_delta * hidden_value
        for hidden_value in hidden
    ]
    output_bias_grad = output_delta

    hidden_deltas = [
        output_delta
        * output_weights[j]
        * hidden[j]
        * (1 - hidden[j])
        for j in range(len(hidden))
    ]

    hidden_weight_grads = [
        [hidden_deltas[j] * input_value for input_value in x]
        for j in range(len(hidden))
    ]

    hidden_bias_grads = hidden_deltas.copy()
        
    return {
        "output_weight_grads": output_weight_grads,
        "output_bias_grad": output_bias_grad,
        "hidden_weight_grads": hidden_weight_grads,
        "hidden_bias_grads": hidden_bias_grads,
    }


# ----------------------------------------------------
# 5. GRADIENT CHECKING
# ----------------------------------------------------

# Backprop gives analytical gradients.
# Central Finite Differences give an independent numerical approximation

def gradient_check(my_input, ground_truth, hidden_weights, hidden_biases, output_weights, output_bias, epsilon=1e-6):
    forward_result = forward(my_input, hidden_weights, hidden_biases, output_weights, output_bias)
    backward_result = backward(my_input, ground_truth, forward_result, output_weights)

    def assert_error(name, analytical_gradient, numerical_gradient):
        error = abs(analytical_gradient - numerical_gradient)

        assert error < 1e-6, (
            f"{name} failed gradient check: "
            f"analytical={analytical_gradient}, "
            f"numerical={numerical_gradient}, "
            f"error={error}"
        )

    # ------- Hidden weights -----------
    for i, neuron_weights in enumerate(hidden_weights):
        for j, _ in enumerate(neuron_weights):
            original_weight = hidden_weights[i][j]

            # Move from original to original + epsilon
            hidden_weights[i][j] += epsilon
            loss_plus = compute_loss(my_input, ground_truth, hidden_weights, hidden_biases, output_weights, output_bias)

            # Move from original + epsilon to original - epsilon
            hidden_weights[i][j] -= 2 * epsilon
            loss_minus = compute_loss(my_input, ground_truth, hidden_weights, hidden_biases, output_weights, output_bias)

            # Restore weight
            hidden_weights[i][j] = original_weight

            numerical_gradient = (loss_plus - loss_minus) / (2 * epsilon)
            analytical_gradient = (backward_result["hidden_weight_grads"][i][j])

            assert_error(f"hidden_weights[{i}][{j}]", analytical_gradient, numerical_gradient)

    # ------- Hidden biases -----------
    for i, _ in enumerate(hidden_biases):
        original_bias = hidden_biases[i]

        # Add epsilon
        hidden_biases[i] += epsilon
        loss_plus = compute_loss(my_input, ground_truth, hidden_weights, hidden_biases, output_weights, output_bias)

        # Substract epsilon
        hidden_biases[i] -= 2 * epsilon
        loss_minus = compute_loss(my_input, ground_truth, hidden_weights, hidden_biases, output_weights, output_bias)

        # Restore weight
        hidden_biases[i] = original_bias

        numerical_gradient = (loss_plus - loss_minus) / (2 * epsilon)
        analytical_gradient = (backward_result["hidden_bias_grads"][i])

        assert_error(f"hidden_biases[{i}]", analytical_gradient, numerical_gradient)

    # ------- Output weights -------------
    for i, _ in enumerate(output_weights):
        original_weight = output_weights[i]

        # Add epsilon
        output_weights[i] += epsilon
        loss_plus = compute_loss(my_input, ground_truth, hidden_weights, hidden_biases, output_weights, output_bias)

        # Substract epsilon
        output_weights[i] -= 2 * epsilon
        loss_minus = compute_loss(my_input, ground_truth, hidden_weights, hidden_biases, output_weights, output_bias)

        # Restore weight
        output_weights[i] = original_weight

        numerical_gradient = (loss_plus - loss_minus) / (2 * epsilon)
        analytical_gradient = (backward_result["output_weight_grads"][i])

        assert_error(f"output_weights[{i}]", analytical_gradient, numerical_gradient)

    # ------ Output bias -------------
    loss_plus = compute_loss(my_input, ground_truth, hidden_weights, hidden_biases, output_weights, output_bias + epsilon)
    loss_minus = compute_loss(my_input, ground_truth, hidden_weights, hidden_biases, output_weights, output_bias - epsilon)
    numerical_gradient = (loss_plus - loss_minus) / (2 * epsilon)
    analytical_gradient = backward_result["output_bias_grad"]

    assert_error("output_bias", analytical_gradient, numerical_gradient)

    return True

# --------------------------------------------------
# 6. GRADIENT DESCENT + TRAINING
# --------------------------------------------------

# Training below uses SGD with batch size 1: update after every example.

def update_parameters(hidden_weights, hidden_biases, output_weights, output_bias, gradients, learning_rate):
    # Hidden weights
    for neuron_index in range(len(hidden_weights)):
        for weight_index in range(len(hidden_weights[neuron_index])):
            hidden_weights[neuron_index][weight_index] -= (learning_rate * gradients["hidden_weight_grads"][neuron_index][weight_index])

    # Hidden biases
    for neuron_index in range(len(hidden_biases)):
        hidden_biases[neuron_index] -= (learning_rate * gradients["hidden_bias_grads"][neuron_index])

    # Output weights
    for weight_index in range(len(output_weights)):
        output_weights[weight_index] -= (learning_rate * gradients["output_weight_grads"][weight_index])

    # Output bias
    output_bias -= (learning_rate * gradients["output_bias_grad"])

    return (
        hidden_weights,
        hidden_biases,
        output_weights,
        output_bias,
    )

def average_loss(training_data, hidden_weights, hidden_biases, output_weights, output_bias):
    total_loss = 0.0

    for x, ground_truth in training_data:
        result = forward(x, hidden_weights, hidden_biases, output_weights, output_bias)
        total_loss += binary_cross_entropy(result["prediction"], ground_truth)

    return total_loss / len(training_data)
    
def train(training_data, epochs=1000, learning_rate=0.1, seed=7, verbose=False, log_every=100):
    hidden_weights, hidden_biases, output_weights, output_bias = initialize_parameters(seed)

    if verbose:
        initial_loss = average_loss(training_data, hidden_weights, hidden_biases, output_weights, output_bias)
        print(f"epoch: initial, loss: {initial_loss}")

    for epoch in range(epochs):
        for x, ground_truth in training_data:
            # 1. Predict
            forward_result = forward(x, hidden_weights, hidden_biases, output_weights, output_bias)
            # 2. Compute gradients
            gradients = backward(x, ground_truth, forward_result, output_weights)
            # 3. Update params
            hidden_weights, hidden_biases, output_weights, output_bias = update_parameters(hidden_weights, hidden_biases, output_weights, output_bias, gradients, learning_rate)

        if verbose and (epoch + 1) % log_every == 0:
            loss = average_loss(training_data, hidden_weights, hidden_biases, output_weights, output_bias)
            print(f"epoch: {epoch + 1}, loss: {loss}")

    return (
        hidden_weights,
        hidden_biases,
        output_weights,
        output_bias,
    )

# ------------------------------------------------------------
# 7. EVALUATION + BEHAVIORAL ANALYSIS
# ------------------------------------------------------------

def predict(params, x, threshold=0.5):
    result = forward(x, *params)
    probability = result["prediction"]
    label = probability >= threshold

    return probability, label, result["hidden"]

def network_behaviour(params, objects):
    return tuple(
        forward(x, *params)["prediction"] >= 0.5
        for x in objects
    )

def true_behaviour(objects):
    return tuple(hidden_concept(x) for x in objects)

def accuracy(params, data):
    correct = 0

    for x, ground_truth in data:
        _, prediction, _ = predict(params, x)
        correct += prediction == ground_truth

    return correct / len(data)

def print_predictions(params, objects):
    print("query          truth  probability  prediction  hidden")

    correct = 0
    for x in objects:
        truth = hidden_concept(x)
        probability, prediction, hidden = predict(params, x)
        correct += prediction == truth

        print(
            f"{str(x):14} "
            f"{str(truth):5} "
            f"{probability:11.4f} "
            f"{str(prediction):10} "
            f"{hidden}"
        )

    print(f"Accuracy: {correct}/{len(objects)}")

def print_parameters(params):
    hidden_weights, hidden_biases, output_weights, output_bias = params

    print("Hidden weights:")
    for i, weights in enumerate(hidden_weights):
        print(i, weights)

    print("Hidden biases:")
    print(hidden_biases)

    print("Output weights:")
    print(output_weights)

    print("Output bias:")
    print(output_bias)

def seed_behaviour_counts(training_data, objects, seeds=100, epochs=1000, learning_rate=0.1):
    counts = {}

    for seed in range(seeds):
        params = train(training_data, epochs=epochs, learning_rate=learning_rate, seed=seed, verbose=False)
        signature = network_behaviour(params, objects)
        counts[signature] = counts.get(signature, 0) + 1

    return counts


def print_behaviour_counts(counts, objects):
    target = true_behaviour(objects)

    for signature, count in sorted(
        counts.items(),
        key=lambda item: item[1],
        reverse=True,
    ):
        marker = " <-- TRUE FUNCTION" if signature == target else ""
        print(f"{signature} -> {count}{marker}")

# ----------------------------------------------
# LEARNING WALKTHROUGH
# ----------------------------------------------

def run_learning_walkthrough():
    my_input = (1, 1, 0, 0)
    ground_truth = 1.0

    # ----- Initial parameters ---------
    print("\n----- INITIAL PARAMETERS -----\n")

    params = initialize_parameters(seed=7)
    hidden_weights, hidden_biases, output_weights, output_bias = params

    print(f"Hidden weights: {hidden_weights}")
    print(f"Hidden biases: {hidden_biases}")
    print(f"Output weights: {output_weights}")
    print(f"Output bias: {output_bias}")

    # ---- Forward pass --------
    print("\n----- FORWARD -----\n")
    forward_result = forward(my_input, hidden_weights, hidden_biases, output_weights, output_bias)

    print(f"hidden_z: {forward_result['hidden_z']}")
    print(f"hidden: {forward_result['hidden']}")
    print(f"output_z: {forward_result['output_z']}")
    print(f"prediction: {forward_result['prediction']}")

    # Known fixture for seed=7.
    assert abs(forward_result["hidden"][0] - 0.23119110864263584) < 1e-12
    assert abs(forward_result["prediction"] - 0.5764458712239586) < 1e-12

    # ---- Loss ----------
    print("\n----- LOSS -----\n")

    prediction = forward_result["prediction"]
    direct_loss = binary_cross_entropy(prediction, ground_truth)
    recomputed_loss = compute_loss(my_input, ground_truth, hidden_weights, hidden_biases, output_weights, output_bias)

    print(f"prediction: {prediction}")
    print(f"ground truth: {ground_truth}")
    print(f"binary cross-entropy: {direct_loss}")
    print(f"compute_loss: {recomputed_loss}")

    assert abs(direct_loss - recomputed_loss) < 1e-12

    # ------ Backward pass -------
    print("\n----- BACKWARD -----\n")
    backward_result = backward(my_input, ground_truth, forward_result, output_weights)

    print(f"output_weight_grads: {backward_result['output_weight_grads']}")
    print(f"output_bias_grad: {backward_result['output_bias_grad']}")
    print(f"hidden_weight_grads: {backward_result['hidden_weight_grads']}")
    print(f"hidden_bias_grads: {backward_result['hidden_bias_grads']}")

    print("\nGradient shapes:")
    print("output_weight_grads -> 3 values")
    print("output_bias_grad    -> 1 value")
    print("hidden_weight_grads -> 3 x 4 values")
    print("hidden_bias_grads   -> 3 values")

    # ----- Gradient check ---------
    print("\n----- GRADIENT CHECK -----\n")
    gradient_check(my_input, ground_truth, hidden_weights, hidden_biases, output_weights, output_bias, epsilon=1e-6)
    print("gradient check: OK")

    # ---- One gradient-descent parameter update- ------
    print("\n----- UPDATE PARAMETERS -----\n")
    initial_loss = compute_loss(my_input, ground_truth, hidden_weights, hidden_biases, output_weights, output_bias)

    # update_parameters mutates the lists, so use a fresh initialization for
    # this one-step experiment rather than reusing state elsewhere.
    step_params = initialize_parameters(seed=7)
    step_hidden_weights, step_hidden_biases, step_output_weights, step_output_bias = step_params

    step_forward = forward(my_input, *step_params)
    step_gradients = backward(my_input, ground_truth, step_forward, step_output_weights)
    updated_params = update_parameters(step_hidden_weights, step_hidden_biases, step_output_weights, step_output_bias, step_gradients, learning_rate=0.1)
    final_loss = compute_loss(my_input, ground_truth, *updated_params)

    print(f"hidden_weights: {updated_params[0]}")
    print(f"hidden_biases: {updated_params[1]}")
    print(f"output_weights: {updated_params[2]}")
    print(f"output_bias: {updated_params[3]}")
    print(f"initial loss: {initial_loss}")
    print(f"final loss: {final_loss}")
    print(f"final loss is smaller? {final_loss < initial_loss}")

    assert final_loss < initial_loss

    # --- Train the network ------
    print("\n----- TRAIN -----\n")

    trained_params = train(TRAINING_DATA, epochs=2000, learning_rate=0.1, seed=7, verbose=True, log_every=200)

    # ---- TRAINING Predictions -----------
    print("\n----- TRAINING PREDICTIONS -----\n")

    for x, label in TRAINING_DATA:
        result = forward(x, *trained_params)
        print(
            f"{x} -> probability={result['prediction']:.4f} "
            f"-> prediction={result['prediction'] >= 0.5} "
            f"-> truth={label}"
        )

    # ---- TEST Predictions -------
    print("\n----- TEST PREDICTIONS -----\n")
    print_predictions(trained_params, TEST_OBJECTS)

    return trained_params

# ----------------------------------------------
# CORRECTNESS CHECKS
# ----------------------------------------------

# These verify the implementation before running learning experiments.

def run_correctness_checks():
    x = (1, 1, 0, 0)
    ground_truth = 1.0

    params = initialize_parameters(seed=7)
    hidden_weights, hidden_biases, output_weights, output_bias = params

    # 8.1 Known forward-pass fixture.
    result = forward(x, *params)
    assert abs(result["hidden"][0] - 0.23119110864263584) < 1e-12
    assert abs(result["prediction"] - 0.5764458712239586) < 1e-12

    # 8.2 Analytical backprop vs numerical derivatives.
    gradient_check(x, ground_truth, hidden_weights, hidden_biases, output_weights, output_bias)

    # 8.3 One gradient-descent step should reduce this example's loss.
    before = compute_loss(x, ground_truth, *params)
    forward_result = forward(x, *params)
    gradients = backward(x, ground_truth, forward_result, output_weights)

    updated_params = update_parameters(hidden_weights, hidden_biases, output_weights, output_bias, gradients, learning_rate=0.1)

    after = compute_loss(x, ground_truth, *updated_params)
    assert after < before

    print("Correctness checks passed")

# --------------------------------------
# EXPERIMENTS
# --------------------------------------

def run_baseline_experiment(params=None):
    if params is None:
        params = train(TRAINING_DATA, epochs=2000, learning_rate=0.1, seed=7, verbose=True, log_every=200)

    print("\n----- LEARNED PARAMETERS -----\n")
    print_parameters(params)

    print("\n----- 100-SEED BEHAVIOR DISTRIBUTION -----\n")
    counts = seed_behaviour_counts(TRAINING_DATA, OBJECTS, seeds=100, epochs=1000, learning_rate=0.1)
    print_behaviour_counts(counts, OBJECTS)

    return params


# Reproduce the evidence experiment without changing the baseline dataset
# Baseline: original TRAINING_DATA
# Intervention 1: add (0, 1, 1, 0) -> False
# Intervention 2: also add (1, 0, 1, 0) -> False
def run_evidence_interventions():
    first_counterexample = (0, 1, 1, 0)
    second_counterexample = (1, 0, 1, 0)

    datasets = [
        ("baseline", list(TRAINING_DATA)),
        (
            "+ first discriminating example",
            list(TRAINING_DATA)
            + [(first_counterexample, hidden_concept(first_counterexample))],
        ),
        (
            "+ two discriminating examples",
            list(TRAINING_DATA)
            + [
                (first_counterexample, hidden_concept(first_counterexample)),
                (second_counterexample, hidden_concept(second_counterexample)),
            ],
        ),
    ]

    target = true_behaviour(OBJECTS)

    print("\n----- EVIDENCE INTERVENTIONS -----\n")

    for name, training_data in datasets:
        counts = seed_behaviour_counts(training_data, OBJECTS, seeds=100, epochs=1000, learning_rate=0.1)
        recovered = counts.get(target, 0)

        print(f"{name}: true function recovered {recovered}/100 seeds")
        print_behaviour_counts(counts, OBJECTS)
        print()


if __name__ == "__main__":
    run_correctness_checks()
    baseline_params = run_learning_walkthrough()
    run_baseline_experiment(baseline_params)
    run_evidence_interventions()
