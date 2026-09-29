# Cross Seed Stability
# Question: are the probe and sensitivity results a property of the training data, or just of seed 7?
# Conclusion:

# ---------------------------------------
# Experiment 4. Cross Seed Stability
# ---------------------------------------

from statistics import median, pstdev, quantiles

from neural import train, predict
from learning_setup import SIX_EXAMPLE_DATA, EIGHT_EXAMPLE_DATA, OBJECTS, hidden_concept
from linear_probing import HIDDEN_SIZE, CONCEPTS, extract_hidden_values, train_probe, leave_one_out_score
from causal_intervention import normalize, cosine_similarity, predict_from_hidden
from sensitivity import feature_sensitivity


# ----------------------------------------
# CONFIGURATION
# ----------------------------------------

NUM_SEEDS = 100

NETWORK_EPOCHS = 2000
NETWORK_LEARNING_RATE = 0.1

THRESHOLD = 0.5

BLUE = 0
LARGE = 1
ROUNDED = 2
STRIPED = 3


# ----------------------------------------
# HELPERS
# ----------------------------------------

def mean(values):
    return sum(values) / len(values)

# A network can end up completely ignoring the nuisance features, which is the
# good case, not an error
def safe_ratio(numerator, denominator):
    if denominator == 0:
        return float("inf")

    return numerator / denominator


# ----------------------------------------
# TRAIN ONE SEED
# ----------------------------------------

def train_for_seed(training_data, seed):
    return train(training_data, epochs=NETWORK_EPOCHS, learning_rate=NETWORK_LEARNING_RATE, seed=seed, verbose=False, log_every=200)

# Score against the true concept on all 16 objects, not just the training examples
def full_world_accuracy(network_params):
    correct = 0

    for x in OBJECTS:
        _, prediction, _ = predict(network_params, x, threshold=THRESHOLD)

        if prediction == hidden_concept(x):
            correct += 1

    return correct


# ------------------------------------------
# REPRESENTATION-LEVEL METRICS
# ------------------------------------------

# Measure:
# 1. leave-one-out decodability of blue AND large
# 2. alignment between the target probe direction and
#    the network's own output direction
def target_probe_metrics(network_params, hidden_values):
    rule = CONCEPTS["blue AND large"]

    loo_score = leave_one_out_score(hidden_values, rule)

    # Full-data probe, only to read off the direction it found
    hidden_data = [hidden_values[x] for x in OBJECTS]
    labels = [bool(rule(x)) for x in OBJECTS]

    probe_weights, _ = train_probe(hidden_data, labels)
    direction = normalize(probe_weights)

    _, _, output_weights, _ = network_params

    # Does the probe point where the output layer already looks?
    alignment = cosine_similarity(direction, output_weights)

    return {"loo_score": loo_score, "alignment": alignment}


# Compress the four feature-sensitivity measurements into:
# - relevant sensitivity: blue + large
# - nuisance sensitivity: rounded + striped
# - relevant / nuisance ratio
def sensitivity_summary(network_params):
    blue = feature_sensitivity(network_params, OBJECTS, BLUE)
    large = feature_sensitivity(network_params, OBJECTS, LARGE)
    rounded = feature_sensitivity(network_params, OBJECTS, ROUNDED)
    striped = feature_sensitivity(network_params, OBJECTS, STRIPED)

    relevant_output = (blue["logit"] + large["logit"]) / 2
    nuisance_output = (rounded["logit"] + striped["logit"]) / 2

    return {
        "relevant_output": relevant_output,
        "nuisance_output": nuisance_output,
        "ratio": safe_ratio(relevant_output, nuisance_output),
    }


# -----------------------------------------------
# BEST TARGET-ALIGNED NEURON ACROSS SEEDS
# -----------------------------------------------

def find_most_target_aligned_neuron(hidden_values):
    positive_objects = [x for x in OBJECTS if hidden_concept(x)]
    negative_objects = [x for x in OBJECTS if not hidden_concept(x)]

    candidates = []

    for neuron_index in range(HIDDEN_SIZE):
        positive_mean = mean([hidden_values[x][neuron_index] for x in positive_objects])
        negative_mean = mean([hidden_values[x][neuron_index] for x in negative_objects])

        signed_gap = (positive_mean - negative_mean)
        candidates.append(
            {
                "neuron_index": neuron_index,
                "positive_mean": positive_mean,
                "negative_mean": negative_mean,
                "signed_gap": signed_gap,
                "separation": abs(signed_gap),
                "polarity": ("positive-high" if signed_gap > 0 else "positive-low"),
            }
        )

    return max(candidates, key=lambda result: result["separation"])


# ------------------------------------------
# BEST-NEURON ABLATION
# ------------------------------------------

def selected_neuron_ablation(network_params, hidden_values, neuron_index):
    _, _, output_weights, output_bias = network_params

    baseline = mean([hidden[neuron_index] for hidden in hidden_values.values()])
    total_logit_change = 0.0

    flips = 0
    positive_flips = 0
    negative_flips = 0

    for x in OBJECTS:
        hidden = hidden_values[x]

        original_z, _, original_label = predict_from_hidden(hidden, output_weights, output_bias)

        # Replace the neuron with its mean, so the network keeps running but learns nothing from it
        ablated_hidden = hidden.copy()
        ablated_hidden[neuron_index] = baseline

        ablated_z, _, ablated_label = predict_from_hidden(ablated_hidden, output_weights, output_bias)

        total_logit_change += abs(ablated_z - original_z)

        if ablated_label != original_label:
            flips += 1

            if hidden_concept(x):
                positive_flips += 1
            else:
                negative_flips += 1

    return {
        "mean_abs_logit_change": total_logit_change / len(OBJECTS),
        "flips": flips,
        "positive_flips": positive_flips,
        "negative_flips": negative_flips,
    }


# ------------------------------------------
# BEST-NEURON PATCHING
# ------------------------------------------

def patch_effect(network_params, hidden_values, recipient, donor, neuron_index):
    _, _, output_weights, output_bias = network_params

    recipient_hidden = hidden_values[recipient]
    donor_hidden = hidden_values[donor]

    _, _, original_label = predict_from_hidden(recipient_hidden, output_weights, output_bias)

    # Copy one neuron over from the donor and see if the label moves
    patched_hidden = recipient_hidden.copy()
    patched_hidden[neuron_index] = donor_hidden[neuron_index]

    _, _, patched_label = predict_from_hidden(patched_hidden, output_weights, output_bias)

    return original_label != patched_label


def selected_neuron_patching(network_params, hidden_values, neuron_index):
    positive_objects = [x for x in OBJECTS if hidden_concept(x)]
    negative_objects = [x for x in OBJECTS if not hidden_concept(x)]

    def count_flips(recipients, donors, same_class=False):
        flips = 0
        total = 0

        for recipient in recipients:
            for donor in donors:
                # Patching an object from itself is a no-op, skip it
                if same_class and recipient == donor:
                    continue

                total += 1

                if patch_effect(network_params, hidden_values, recipient, donor, neuron_index):
                    flips += 1

        return {"flips": flips, "total": total, "rate": flips / total}

    return {
        "negative_to_positive": count_flips(positive_objects, negative_objects),
        "positive_to_negative": count_flips(negative_objects, positive_objects),
        # Same-class pairs are the control: the neuron should not flip these
        "positive_to_positive": count_flips(positive_objects, positive_objects, same_class=True),
        "negative_to_negative": count_flips(negative_objects, negative_objects, same_class=True),
    }


def analyze_best_neuron(network_params, hidden_values):
    aligned = find_most_target_aligned_neuron(hidden_values)
    neuron_index = aligned["neuron_index"]

    _, _, output_weights, _ = network_params
    output_weight = output_weights[neuron_index]

    # Useful polarity-independent measure.
    #
    # positive-high + positive weight
    # or
    # positive-low + negative weight
    #
    # both produce a positive value.
    class_effect = output_weight * aligned["signed_gap"]

    ablation = selected_neuron_ablation(network_params, hidden_values, neuron_index)
    patching = selected_neuron_patching(network_params, hidden_values, neuron_index)

    return {
        "neuron_index": neuron_index,
        "separation": aligned["separation"],
        "positive_mean": aligned["positive_mean"],
        "negative_mean": aligned["negative_mean"],
        "polarity": aligned["polarity"],
        "output_weight": output_weight,
        "class_effect": class_effect,
        "ablation": ablation,
        "patching": patching,
    }


# ------------------------------------------
# ANALYZE ONE SEED
# ------------------------------------------

def analyze_seed(training_data, seed):
    network = train_for_seed(training_data, seed)
    hidden_values = extract_hidden_values(network)

    probe_metrics = target_probe_metrics(network, hidden_values)
    sensitivity = sensitivity_summary(network)
    best_neuron = analyze_best_neuron(network, hidden_values)

    return {
        "seed": seed,
        "accuracy": full_world_accuracy(network),
        "target_loo": probe_metrics["loo_score"],
        "probe_alignment": probe_metrics["alignment"],
        "relevant_sensitivity": sensitivity["relevant_output"],
        "nuisance_sensitivity": sensitivity["nuisance_output"],
        "sensitivity_ratio": sensitivity["ratio"],
        "best_neuron": best_neuron,
    }


def run_cross_seed_condition(name, training_data, num_seeds=NUM_SEEDS):
    print(f"\n--- Running cross seed experiment: {name} ---")

    return [analyze_seed(training_data, seed) for seed in range(num_seeds)]


# ------------------------------------------
# DISTRIBUTION SUMMARIES
# ------------------------------------------

# Report more than the mean, so one or two unusual seeds
# cannot hide behind an average
def distribution_summary(values):
    q1, _, q3 = quantiles(values, n=4, method="inclusive")

    return {
        "mean": mean(values),
        "median": median(values),
        "std": pstdev(values),
        "min": min(values),
        "q1": q1,
        "q3": q3,
        "max": max(values),
    }


def print_distribution(label, values, decimals=3):
    stats = distribution_summary(values)

    print(
        f"{label:24} "
        f"mean={stats['mean']:.{decimals}f}  "
        f"median={stats['median']:.{decimals}f}  "
        f"std={stats['std']:.{decimals}f}  "
        f"min={stats['min']:.{decimals}f}  "
        f"q1={stats['q1']:.{decimals}f}  "
        f"q3={stats['q3']:.{decimals}f}  "
        f"max={stats['max']:.{decimals}f}"
    )


def print_field_distribution(label, results, key, decimals=3):
    print_distribution(label, [result[key] for result in results], decimals=decimals)


# ------------------------------------------
# SUMMARIZE REPRESENTATION-LEVEL RESULTS
# ------------------------------------------

def summarize_results(name, results):
    print(f"\n--- {name}: representation-level ---\n")

    true_function_count = sum(result["accuracy"] == len(OBJECTS) for result in results)
    print("true function:", f"{true_function_count}/{len(results)}")

    print_field_distribution("target LOO", results, "target_loo", decimals=2)
    print_field_distribution("probe alignment", results, "probe_alignment")
    print_field_distribution("relevant sensitivity", results, "relevant_sensitivity")
    print_field_distribution("nuisance sensitivity", results, "nuisance_sensitivity")
    print_field_distribution("sensitivity ratio", results, "sensitivity_ratio")


# ------------------------------------------
# SUMMARIZE BEST-NEURON RESULTS
# ------------------------------------------

PATCH_TYPES = [
    "negative_to_positive",
    "positive_to_negative",
    "positive_to_positive",
    "negative_to_negative",
]

def summarize_best_neurons(name, results):
    best_neurons = [result["best_neuron"] for result in results]
    n = len(best_neurons)

    print(f"\n--- {name}: best target-aligned neuron ---\n")

    # Raw index is only diagnostic, neuron identities can permute across seeds
    print("Winning neuron index:")

    for neuron_index in range(HIDDEN_SIZE):
        count = sum(result["neuron_index"] == neuron_index for result in best_neurons)
        print(f"  neuron {neuron_index}: {count}/{n}")

    positive_high = sum(result["polarity"] == "positive-high" for result in best_neurons)
    positive_low = (n - positive_high)

    print("\nPolarity:")
    print(f"  positive-high: {positive_high}/{n}")
    print(f"  positive-low:  {positive_low}/{n}")

    print("\nClass alignment:")
    print("  class-aligned output sign:", sum(result["class_effect"] > 0 for result in best_neurons), "/", n)

    print_field_distribution("class separation", best_neurons, "separation")
    print_distribution("|output weight|", [abs(result["output_weight"]) for result in best_neurons])
    print_field_distribution("class effect", best_neurons, "class_effect")

    print("\nAblation:")

    for label, key in [("total flips", "flips"), ("positive flips", "positive_flips"), ("negative flips", "negative_flips")]:
        print_distribution(label, [result["ablation"][key] for result in best_neurons], decimals=2)

    print("\nPatching flip rates:")

    for patch_type in PATCH_TYPES:
        print_distribution(patch_type, [result["patching"][patch_type]["rate"] for result in best_neurons])


# ------------------------------------------
# SIDE-BY-SIDE TRANSITION SUMMARY
# ------------------------------------------

def summarize_transition(wrong_results, correct_results):
    print("\n=== 6 examples -> 8 examples ===\n")

    def print_shift(label, wrong_values, correct_values):
        print(f"{label:22} {mean(wrong_values):8.3f} -> {mean(correct_values):8.3f}")

    metrics = [
        ("target LOO", "target_loo"),
        ("probe alignment", "probe_alignment"),
        ("relevant sensitivity", "relevant_sensitivity"),
        ("nuisance sensitivity", "nuisance_sensitivity"),
        ("sensitivity ratio", "sensitivity_ratio"),
    ]

    for label, key in metrics:
        print_shift(label, [r[key] for r in wrong_results], [r[key] for r in correct_results])

    wrong_best = [result["best_neuron"] for result in wrong_results]
    correct_best = [result["best_neuron"] for result in correct_results]

    print_shift(
        "best-neuron separation",
        [r["separation"] for r in wrong_best],
        [r["separation"] for r in correct_best],
    )

    short_labels = {
        "negative_to_positive": "N->P patch flip rate",
        "positive_to_negative": "P->N patch flip rate",
        "positive_to_positive": "P->P patch flip rate",
        "negative_to_negative": "N->N patch flip rate",
    }

    for patch_type in PATCH_TYPES:
        print_shift(
            short_labels[patch_type],
            [r["patching"][patch_type]["rate"] for r in wrong_best],
            [r["patching"][patch_type]["rate"] for r in correct_best],
        )




if __name__ == "__main__":
    wrong_results = run_cross_seed_condition("6-example network", SIX_EXAMPLE_DATA)

    correct_training_data = EIGHT_EXAMPLE_DATA
    correct_results = run_cross_seed_condition("8-example network", correct_training_data)

    summarize_results("6-example network", wrong_results)
    summarize_results("8-example network", correct_results)

    # Is the same neuron story stable across seeds?
    summarize_best_neurons("6-example network", wrong_results)
    summarize_best_neurons("8-example network", correct_results)

    summarize_transition(wrong_results, correct_results)
