# Sensitivity Experiment
# Conclusion: the corrected network reorganized so that blue and large matter more, while rounded and striped matter much less.

# ---------------------------------------
# Experiment 1. Representation Invariance
# ---------------------------------------

import math
from neural import predict, forward, train
from learning_setup import SIX_EXAMPLE_DATA, EIGHT_EXAMPLE_DATA, OBJECTS


# ---------------------------------------
# Checks distance between two hidden representations
# ---> "Did the representation change?"
# ---------------------------------------

def representation_distance(a, b):
    return math.sqrt(sum((a_i - b_i) ** 2 for a_i, b_i in zip(a, b)))

def hidden_representation(params, x):
    _, _, hidden = predict(params, x, threshold=0.5)
    return hidden


def hidden_distance(params, x1, x2):
    h1 = hidden_representation(params, x1)
    h2 = hidden_representation(params, x2)

    return representation_distance(h1, h2)


# ---------------------------------------
# Checks difference between output logits
# ---> "Did the representation change in a way that matters to the output?"
# ---------------------------------------

def output_logit(params, x):
    hidden_weights, hidden_biases, output_weights, output_bias = params
    result = forward(x, hidden_weights, hidden_biases, output_weights, output_bias)

    return result["output_z"]

def logit_difference(params, x1, x2):
    return abs(output_logit(params, x1) - output_logit(params, x2))



# ---------------------------------------
# Feature Sensitivity
# ---------------------------------------

BLUE = 0
LARGE = 1
ROUNDED = 2
STRIPED = 3

FEATURE_NAMES = ["blue", "large", "rounded", "striped"]

def flip_feature(x, feature_index):
    result = list(x)
    result[feature_index] = 1 - result[feature_index]
    return tuple(result)

def feature_sensitivity(params, objects, feature_index):
    hidden_total = 0.0
    logit_total = 0.0
    count = 0

    for x in objects:
        flipped = flip_feature(x, feature_index)

        # Avoid counting every pair twice.
        if x >= flipped:
            continue

        hidden_total += hidden_distance(params, x, flipped)
        logit_total += logit_difference(params, x, flipped)
        count += 1

    # Returns average sensitivity
    return {
        "hidden": hidden_total / count,
        "logit": logit_total / count,
    }




if __name__ == "__main__":

    print("\n -- Correct Function -- \n")
    full_training_data = EIGHT_EXAMPLE_DATA
    print(f"training data count: {len(full_training_data)}")
    print("           hidden                output-relevant")
    trained_params = train(full_training_data, epochs=2000, learning_rate=0.1, seed=7, verbose=False, log_every=200)
    for index, name in enumerate(FEATURE_NAMES):
        sensitivity = feature_sensitivity(trained_params, OBJECTS, index)
        print(f"{str(name):8}  {str(sensitivity["hidden"]):18}    {str(sensitivity["logit"]):8}")

    print("\n -- Incorrect Function -- \n")
    print(f"training data count: {len(SIX_EXAMPLE_DATA)}")
    print("           hidden                output-relevant")
    trained_params = train(SIX_EXAMPLE_DATA, epochs=2000, learning_rate=0.1, seed=7, verbose=False, log_every=200)
    for index, name in enumerate(FEATURE_NAMES):
        sensitivity = feature_sensitivity(trained_params, OBJECTS, index)
        print(f"{str(name):8}  {str(sensitivity["hidden"]):18}    {str(sensitivity["logit"]):8}")

