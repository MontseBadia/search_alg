# -------------
# PROTOTYPE LEARNER
# -------------

# Model: compress each observed category into its component-mean
# Inductive bias: a class is well represented by its coordinates mean
# Complexity (n examples, d features):
# - O(n*d) per query (builds averages each call)
# - O(d) when not rebuilding average

from math import sqrt
from learning_setup import OBJECTS, TEST_OBJECTS, TRAINING_DATA, hidden_concept





def examples_with_label(training_data, target_label):
    return [x for x, label in training_data if label == target_label]

# This is called component wise average
def average_vector(examples):
    if not examples:
        raise ValueError("Cannot average an empty category")
    # zip(*examples) groups all first coordinates, all second coordinates, etc.
    return tuple(sum(column) / len(column) for column in zip(*examples))

def euclidean_distance(a, b):
    return sqrt(sum((a_item - b_item) ** 2 for a_item, b_item in zip(a, b)))

def make_prototypes(training_data):
    prototypes = []
    for label in (True, False):
        examples = examples_with_label(training_data, label)
        if examples:
            prototypes.append((average_vector(examples), label))
    if not prototypes:
        raise ValueError("Prototype requires at least one example")
    return prototypes


def predict_with_prototypes(prototypes, query):
    nearest = min(prototypes, key=lambda item: euclidean_distance(item[0], query))
    # Ties go to the first prototype, True in make_prototypes().
    return nearest[1]


def prototype_predict(training_data, query):
    return predict_with_prototypes(make_prototypes(training_data), query)




# ---- TESTS ------
def run_tests():
    assert len(OBJECTS) == 16 and len(TEST_OBJECTS) == 10
    assert average_vector([(0, 1), (1, 1)]) == (0.5, 1.0)
    assert euclidean_distance((0, 0), (3, 4)) == 5
    assert all(prototype_predict(TRAINING_DATA, x) == label for x, label in TRAINING_DATA)
    assert make_prototypes([((1, 0), True)]) == [((1.0, 0.0), True)]
    try:
        make_prototypes([])
    except ValueError:
        pass
    else:
        raise AssertionError("Empty training data must fail")
    print("Prototype tests passed")


# 4. FIXED-DATA EXPERIMENT: build prototypes once, then predict.
def run_experiment():
    prototypes = make_prototypes(TRAINING_DATA)
    print("\nLearned prototypes:", prototypes)
    correct = 0
    print("\nPrototype: six training objects, ten unseen objects")
    print("query          truth  prediction  correct")
    for x in TEST_OBJECTS:
        truth = hidden_concept(x)
        prediction = predict_with_prototypes(prototypes, x)
        correct += prediction == truth
        print(f"{str(x):14} {str(truth):5}  {str(prediction):10}  {prediction == truth}")
    print(f"Accuracy: {correct}/{len(TEST_OBJECTS)}")


if __name__ == "__main__":
    run_tests()
    run_experiment()
