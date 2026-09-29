# ---------------------------------------
# Experiment 3. Causal Intervention
# ---------------------------------------
 
import math
from linear_probing import train_network_pair, extract_hidden_values, CONCEPTS, train_probe
from learning_setup import TRAINING_DATA, OBJECTS, hidden_concept




HIDDEN_SIZE = 3

def sigmoid(z):
    return 1 / (1 + math.exp(-z))

def predict_from_hidden(hidden, output_weights, output_bias, threshold=0.5):
    output_z = (
        sum(
            h * weight
            for h, weight in zip(hidden, output_weights)
        ) + output_bias
    )

    probability = sigmoid(output_z)
    prediction = probability >= threshold

    return output_z, probability, prediction

# Returns something like: [0.42, 0.38, 0.57]
def mean_hidden_activations(hidden_values):
    # Gets the length of the first value in the dictionary
    hidden_size = len(next(iter(hidden_values.values())))
    means = []

    for neuron in range(hidden_size):
        mean = sum(
            hidden[neuron]
            for hidden in hidden_values.values()
        ) / len(hidden_values)

        means.append(mean)

    return means


# ----------------------------------------------
# NEURON ABLATION
# ----------------------------------------------

def ablate_neuron(hidden, neuron_index, baseline):
    ablated = hidden.copy()
    ablated[neuron_index] = baseline

    return ablated

def neuron_ablation_score(network_params, hidden_values, neuron_index):
    (_, _, output_weights, output_bias) = network_params

    means = mean_hidden_activations(hidden_values)
    baseline = means[neuron_index]

    total_logit_change = 0.0
    total_probability_change = 0.0
    label_flips = 0

    flipped_objects = []

    for x in OBJECTS:
        hidden = hidden_values[x]

        (original_z, original_probability, original_label) = predict_from_hidden(hidden, output_weights, output_bias)

        ablated_hidden = ablate_neuron(hidden, neuron_index, baseline)

        (ablated_z, ablated_probability, ablated_label) = predict_from_hidden(ablated_hidden, output_weights, output_bias)

        total_logit_change += abs(ablated_z - original_z)
        total_probability_change += abs(ablated_probability - original_probability)

        if ablated_label != original_label:
            label_flips += 1
            flipped_objects.append(x)

    n = len(OBJECTS)

    return {
        "mean_logit_change": total_logit_change / n,
        "mean_probability_change": total_probability_change / n,
        "label_flips": label_flips,
        "flipped_objects": flipped_objects
    }

def run_ablation_experiment(network_name, network_params, hidden_values):
    print(f"\n--- {network_name} ---")

    for neuron_index in range(HIDDEN_SIZE):
        result = neuron_ablation_score(network_params, hidden_values, neuron_index)

        print(
            f"Neuron {neuron_index}: "
            f"logit change="
            f"{result['mean_logit_change']:.3f}, "
            f"prob change="
            f"{result['mean_probability_change']:.3f}, "
            f"label flips="
            f"{result['label_flips']}/16"
            f"flipped_objects="
            f"{result['flipped_objects']}"
        )

# ----------------------------------------------
# ACTIVATION PATCHING
# ----------------------------------------------

def patch_neuron(recipient_hidden, donor_hidden, neuron_index):
    patched = recipient_hidden.copy()
    patched[neuron_index] = (donor_hidden[neuron_index])
    return patched


def activation_patch_effect(network_params, hidden_values, recipient_obj, donor_obj, neuron_index):
    (_, _, output_weights, output_bias) = network_params
    recipient_hidden = hidden_values[recipient_obj]
    donor_hidden = hidden_values[donor_obj]

    # Original recipient output
    (original_z, original_probability, original_label) = predict_from_hidden(recipient_hidden, output_weights, output_bias)

    # Replace one recipient activation with the donor's real activation
    patched_hidden = patch_neuron(recipient_hidden, donor_hidden, neuron_index)

    (patched_z, patched_probability, patched_label) = predict_from_hidden(patched_hidden, output_weights, output_bias)

    return {
        "recipient": recipient_obj,
        "donor": donor_obj,
        "original_activation": recipient_hidden[neuron_index],
        "donor_activation": donor_hidden[neuron_index],
        "original_z": original_z,
        "patched_z": patched_z,
        "logit_change": patched_z - original_z,
        "original_probability": original_probability,
        "patched_probability": patched_probability,
        "probability_change": (patched_probability - original_probability),
        "original_label": original_label,
        "patched_label": patched_label,
        "label_flipped": original_label != patched_label,
    }

def run_activation_patching(network_name, network_params, hidden_values, neuron_index):
    positive_objects = [x for x in OBJECTS if hidden_concept(x)]
    negative_objects = [x for x in OBJECTS if not hidden_concept(x)]

    print(f"\n--- {network_name}: Neuron {neuron_index} ---")

    # -----------------------------------------------
    # NEGATIVE DONOR -> POSITIVE RECIPIENT
    # -----------------------------------------------

    neg_to_pos_results = []

    for recipient in positive_objects:
        for donor in negative_objects:
            result = activation_patch_effect(network_params, hidden_values, recipient, donor, neuron_index)
            neg_to_pos_results.append(result)

    # -----------------------------------------------
    # POSITIVE DONOR -> NEGATIVE RECIPIENT
    # -----------------------------------------------

    pos_to_neg_results = []

    for recipient in negative_objects:
        for donor in positive_objects:
            result = activation_patch_effect(network_params, hidden_values, recipient, donor, neuron_index)
            pos_to_neg_results.append(result)

    # -----------------------------------------------
    # SUMMARY
    # -----------------------------------------------

    def summarize(results):
        n = len(results)
        mean_logit_change = sum(result["logit_change"] for result in results) / n
        mean_probability_change = sum(result["probability_change"] for result in results) / n
        flips = sum(result["label_flipped"] for result in results)

        return {
            "mean_logit_change": mean_logit_change,
            "mean_probability_change": mean_probability_change,
            "flips": flips,
            "total": n,
        }

    neg_to_pos = summarize(neg_to_pos_results)
    pos_to_neg = summarize(pos_to_neg_results)

    print("\nNegative donor → Positive recipient")
    print(f"mean logit change: {neg_to_pos['mean_logit_change']:.3f}")
    print(f"mean probability change: {neg_to_pos['mean_probability_change']:.3f}")
    print(f"label flips: {neg_to_pos['flips']}/{neg_to_pos['total']}")
    print("\nPositive donor → Negative recipient")
    print(f"mean logit change: {pos_to_neg['mean_logit_change']:.3f}")
    print(f"mean probability change: {pos_to_neg['mean_probability_change']:.3f}")
    print(f"label flips: {pos_to_neg['flips']}/{pos_to_neg['total']}")

    return (
        neg_to_pos_results,
        pos_to_neg_results,
    )

def run_same_class_patching(network_name, network_params, hidden_values, neuron_index):
    positive_objects = [x for x in OBJECTS if hidden_concept(x)]
    negative_objects = [x for x in OBJECTS if not hidden_concept(x)]

    print(f"\n--- {network_name}: Neuron {neuron_index} ---")

    # -----------------------------------------------------
    # POSITIVE DONOR -> POSITIVE RECIPIENT
    # -----------------------------------------------------

    pos_to_pos_results = []

    for recipient in positive_objects:
        for donor in positive_objects:
            # Avoid patching an object with itself
            if donor == recipient:
                continue

            result = activation_patch_effect(network_params, hidden_values, recipient, donor, neuron_index)
            pos_to_pos_results.append(result)

    # -----------------------------------------------------
    # NEGATIVE DONOR -> NEGATIVE RECIPIENT
    # -----------------------------------------------------

    neg_to_neg_results = []

    for recipient in negative_objects:
        for donor in negative_objects:
            if donor == recipient:
                continue

            result = activation_patch_effect(network_params, hidden_values, recipient, donor, neuron_index)
            neg_to_neg_results.append(result)

    # -----------------------------------------------
    # SUMMARY
    # -----------------------------------------------

    def summarize(results):
        n = len(results)
        mean_abs_logit_change = sum(abs(result["logit_change"]) for result in results) / n
        mean_abs_probability_change = sum(abs(result["probability_change"]) for result in results) / n
        flips = sum(result["label_flipped"] for result in results)

        return {
            "mean_abs_logit_change": mean_abs_logit_change,
            "mean_abs_probability_change": mean_abs_probability_change,
            "flips": flips,
            "total": n,
        }

    pos_to_pos = summarize(pos_to_pos_results)
    neg_to_neg = summarize(neg_to_neg_results)

    print("\nPositive donor → Positive recipient")
    print(f"mean |logit change|: {pos_to_pos['mean_abs_logit_change']:.3f}")
    print(f"mean |probability change|: {pos_to_pos['mean_abs_probability_change']:.3f}")
    print(f"label flips: {pos_to_pos['flips']}/{pos_to_pos['total']}")
    print("\nNegative donor → Negative recipient")
    print(f"mean |logit change|: {neg_to_neg['mean_abs_logit_change']:.3f}")
    print(f"mean |probability change|: {neg_to_neg['mean_abs_probability_change']:.3f}")
    print(f"label flips: {neg_to_neg['flips']}/{neg_to_neg['total']}")

    return (
        pos_to_pos_results,
        neg_to_neg_results,
    )


# ----------------------------------------------
# PROBE-DIRECTION INTERVENTION
# ----------------------------------------------

def normalize(vector):
    norm = math.sqrt(sum(value ** 2 for value in vector))
    return [value / norm for value in vector]

def train_target_probe(hidden_values):
    rule = CONCEPTS["blue AND large"]
    hidden_data = [hidden_values[x] for x in OBJECTS]
    labels = [bool(rule(x)) for x in OBJECTS]

    probe_params = train_probe(hidden_data, labels)
    probe_weights, probe_bias = probe_params
    direction = normalize(probe_weights)

    return (probe_params, direction)

def dot(a, b):
    return sum(x * y for x, y in zip(a, b))

def vector_norm(vector):
    return math.sqrt(sum(value ** 2 for value in vector))

def cosine_similarity(a, b):
    return (dot(a, b) / (vector_norm(a) * vector_norm(b)))

def probe_output_alignment(network_params, probe_direction):
    (_, _, output_weights, _) = network_params

    return {
        "dot_product": dot(output_weights, probe_direction),
        "cosine_similarity": cosine_similarity(output_weights, probe_direction),
    }

def steer_hidden(hidden, direction, alpha):
    return [
        h + alpha * d
        for h, d in zip(hidden, direction)
    ]

def probe_direction_effect(network_params, hidden, direction, alpha):
    (_, _, output_weights, output_bias) = network_params

    (original_z, original_probability, original_label) = predict_from_hidden(hidden, output_weights, output_bias)
    steered_hidden = steer_hidden(hidden, direction, alpha)
    (steered_z, steered_probability, steered_label) = predict_from_hidden(steered_hidden, output_weights, output_bias)

    return {
        "original_z": original_z,
        "steered_z": steered_z,
        "logit_change": steered_z - original_z,
        "original_probability": original_probability,
        "steered_probability": steered_probability,
        "probability_change": (steered_probability - original_probability),
        "original_label": original_label,
        "steered_label": steered_label,
        "label_flipped": original_label != steered_label,
        "steered_hidden": steered_hidden,
    }

def outside_activation_range(hidden):
    return any(value < 0.0 or value > 1.0 for value in hidden)

ALPHAS = [
    0.01,
    0.05,
    0.10,
    0.20,
]

def run_probe_direction_intervention(network_name, network_params, hidden_values):
    (probe_params, direction) = train_target_probe(hidden_values)
    alignment = probe_output_alignment(network_params, direction)

    print(f"\n--- {network_name} ---")
    print("probe direction:", [round(value, 3) for value in direction])
    print("probe/output cosine:", f"{alignment['cosine_similarity']:.3f}")
    print("probe/output dot:", f"{alignment['dot_product']:.3f}")
    print("\nalpha   direction   mean Δlogit   flips   out-of-range")

    for magnitude in ALPHAS:
        for sign, name in [
            (+1, "+concept"),
            (-1, "-concept"),
        ]:
            alpha = sign * magnitude
            results = []
            out_of_range = 0

            for x in OBJECTS:
                result = probe_direction_effect(network_params, hidden_values[x], direction, alpha)
                results.append(result)

                if outside_activation_range(result["steered_hidden"]):
                    out_of_range += 1

            mean_logit_change = sum(result["logit_change"] for result in results) / len(results)
            flips = sum(result["label_flipped"] for result in results)

            print(
                f"{magnitude:<7.2f} "
                f"{name:<10} "
                f"{mean_logit_change:>11.3f} "
                f"{flips:>5}/16 "
                f"{out_of_range:>5}/16"
            )



if __name__ == "__main__":
    wrong_network, correct_network = (train_network_pair())
    wrong_hidden = extract_hidden_values(wrong_network)
    correct_hidden = extract_hidden_values(correct_network)

    run_ablation_experiment("Wrong network", wrong_network, wrong_hidden)
    run_ablation_experiment("Correct network", correct_network, correct_hidden)

    run_activation_patching("Wrong network", wrong_network, wrong_hidden, neuron_index=0)
    run_activation_patching("Correct network", correct_network, correct_hidden, neuron_index=0)

    run_same_class_patching("Wrong network", wrong_network, wrong_hidden, neuron_index=0)
    run_same_class_patching("Correct network", correct_network, correct_hidden, neuron_index=0)

    run_probe_direction_intervention("Wrong network", wrong_network, wrong_hidden)
    run_probe_direction_intervention("Correct network", correct_network, correct_hidden)