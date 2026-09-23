# 4 inputs
# hidden neurons
# 1 output neuron

from learning_setup import OBJECTS, TEST_OBJECTS, TRAINING_DATA, hidden_concept
import random
import math

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

def linear_layer(x, weights, biases):
    return [
        sum(
            input_value * weight
            for input_value, weight in zip(x, neuron_weights)
        ) + bias
        for neuron_weights, bias in zip(weights, biases)
    ]

def output_layer(h, weights, bias):
    return sum(
        input_value * weight
        for input_value, weight in zip(h, weights)
    ) + bias


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

def squared_error(prediction, ground_truth):
    return (ground_truth - prediction) ** 2

def binary_cross_entropy(prediction, ground_truth):
    # clamp so we don't get undefined when prediction == 1 or prediction == 0
    epsilon = 1e-12
    prediction = min(max(prediction, epsilon), 1 - epsilon)

    return -(ground_truth * math.log(prediction)
             + (1 - ground_truth) * math.log(1 - prediction))

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
        [
            hidden_deltas[j] * input_value
            for input_value in x
        ]
        for j in range(len(hidden))
    ]

    hidden_bias_grads = hidden_deltas.copy()
        
    return {
        "output_weight_grads": output_weight_grads,
        "output_bias_grad": output_bias_grad,
        "hidden_weight_grads": hidden_weight_grads,
        "hidden_bias_grads": hidden_bias_grads,
    }


def compute_loss(x, ground_truth, hidden_weights, hidden_biases, output_weights, output_bias):
    result = forward(x, hidden_weights, hidden_biases, output_weights, output_bias)

    return binary_cross_entropy(result["prediction"], ground_truth)


# Central Finite Difference

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

    # --------------------------------
    # 1. Hidden weights
    # --------------------------------
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

    # --------------------------------
    # 2. Hidden biases
    # --------------------------------
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

    # --------------------------------
    # 3. Output weights
    # --------------------------------
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

    # --------------------------------
    # 4. Output bias
    # --------------------------------
    loss_plus = compute_loss(my_input, ground_truth, hidden_weights, hidden_biases, output_weights, output_bias + epsilon)
    loss_minus = compute_loss(my_input, ground_truth, hidden_weights, hidden_biases, output_weights, output_bias - epsilon)
    numerical_gradient = (loss_plus - loss_minus) / (2 * epsilon)
    analytical_gradient = backward_result["output_bias_grad"]

    assert_error("output_bias", analytical_gradient, numerical_gradient)

    return True


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
    
def train(training_data, epochs=1000, learning_rate=0.1, seed=7):
    hidden_weights, hidden_biases, output_weights, output_bias = initialize_parameters(seed)

    for epoch in range(epochs):
        for x, ground_truth in training_data:
            # 1. Predict
            forward_result = forward(x, hidden_weights, hidden_biases, output_weights, output_bias)
            # 2. Compute gradients
            gradients = backward(x, ground_truth, forward_result, output_weights)
            # 3. Update params
            hidden_weights, hidden_biases, output_weights, output_bias = update_parameters(hidden_weights, hidden_biases, output_weights, output_bias, gradients, learning_rate)

        if epoch % 100 == 0:
            loss = average_loss(training_data, hidden_weights, hidden_biases, output_weights, output_bias)
            print(f"epoch: {epoch}, loss: {loss}")

    return (
        hidden_weights,
        hidden_biases,
        output_weights,
        output_bias,
    )



        








if __name__ == "__main__":
    print("\n----- Check initialised params -----\n")
    hidden_weights, hidden_biases, output_weights, output_bias = initialize_parameters()
    print(f"\nHidden weights: {hidden_weights}")
    print(f"Hidden biases: {hidden_biases}")
    print(f"Output weights: {output_weights}")
    print(f"Output bias: {output_bias}\n")

    print("\n----- Forward -----\n")
    my_input = (1, 1, 0, 0)
    forward_result = forward(my_input, hidden_weights, hidden_biases, output_weights, output_bias)
    # Hidden Activations: [0.23119, 0.61227, 0.14062]
    # Output: prediction = 0.57645
    print(f"hidden_z: {forward_result["hidden_z"]}")
    print(f"hidden: {forward_result["hidden"]}")
    print(f"output_z: {forward_result["output_z"]}")
    print(f"prediction: {forward_result["prediction"]}\n")

    print("\n----- Loss -----\n")
    label = 1 # True
    prediction = forward_result["prediction"]
    print(binary_cross_entropy(prediction, label))
    print(compute_loss(my_input, label, hidden_weights, hidden_biases, output_weights, output_bias))

    print("\n----- Backward -----\n")
    backward_result = backward(my_input, label, forward_result, output_weights)
    print(f"\noutput_weight_grads: {backward_result["output_weight_grads"]}")
    print(f"output_bias_grad: {backward_result["output_bias_grad"]}")
    print(f"hidden_weight_grads: {backward_result["hidden_weight_grads"]}")
    print(f"hidden_bias_grads: {backward_result["hidden_bias_grads"]}\n")
    # output_weight_grads   -> 3 values
    # output_bias_grad      -> 1 value
    # hidden_weight_grads   -> 3 x 4 values
    # hidden_bias_grads     -> 3 values

    print("\n----- Gradient Check -----\n")
    gradient_check = gradient_check(my_input, label, hidden_weights, hidden_biases, output_weights, output_bias, epsilon=1e-6)
    print(f"\ngradient check: {"OK" if gradient_check else "Errors"}")

    print("\n----- Update Params -----\n")
    initial_loss = compute_loss(my_input, label, hidden_weights, hidden_biases, output_weights, output_bias)
    gradients = backward(my_input, label, forward_result, output_weights)
    hidden_weights, hidden_biases, output_weights, output_bias = update_parameters(hidden_weights, hidden_biases, output_weights, output_bias, gradients, learning_rate=0.1)
    print(f"\nhidden_weights: {hidden_weights}")
    print(f"hidden_biases: {hidden_biases}")
    print(f"output_weights: {output_weights}")
    print(f"output_bias: {output_bias}\n")
    final_loss = compute_loss(my_input, label, hidden_weights, hidden_biases, output_weights, output_bias)
    print(f"Initial loss: {initial_loss}")
    print(f"Final loss: {final_loss}")
    print(f"final loss is smaller? {final_loss < initial_loss}")

    print("\n----- Train -----\n")
    hidden_weights, hidden_biases, output_weights, output_bias = train(TRAINING_DATA, epochs=2000, learning_rate=0.1, seed=7)

    print("\n----- Predictions -----\n")
    for test_object, ground_truth in TRAINING_DATA:
        forward_result = forward(test_object, hidden_weights, hidden_biases, output_weights, output_bias)
        prediction = forward_result["prediction"]
        print(f"{test_object} -> {prediction} -> {ground_truth}")

    print("\n----- Test Objects -----\n")
    correct = 0
    print("query          truth  probability  prediction")
    for x in TEST_OBJECTS:
        truth = hidden_concept(x)
        result = forward(x, hidden_weights, hidden_biases, output_weights, output_bias)
        probability = result["prediction"]
        prediction = probability >= 0.5
        correct += prediction == truth
        print(
            f"{str(x):14} "
            f"{str(truth):5} "
            f"{probability:11.4f} "
            f"{prediction}            "
            f"{result["hidden"]}")
    print(f"Accuracy: {correct}/{len(TEST_OBJECTS)}")

    print("Hidden weights:")
    for i, weights in enumerate(hidden_weights):
        print(i, weights)

    print("Hidden biases:")
    print(hidden_biases)

    print("Output weights:")
    print(output_weights)

    print("Output bias:")
    print(output_bias)

