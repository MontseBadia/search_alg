# -------------
# EXEMPLAR LEARNER
# -------------

# 1-Nearest Neighbour

# Model: store observations, measure distance, return nearest label
# Inductive bias: nearby objects should share labels
# Complexity (n examples, d features): O(n*d) per query

# Notes:
# - When two or more training examples are equally close to the query and have different labels,
# the learner chooses whatever comes first. So order matters.

from learning_setup import OBJECTS, TEST_OBJECTS, TRAINING_DATA, hidden_concept


def hamming_distance(a, b):
    return sum(a_item != b_item for a_item, b_item in zip(a, b))

# 1-Nearest neighbour learner
# Find training element with smallest distance from query, then return same label
def exemplar_predict(training_data, query):
    if not training_data:
        raise ValueError("Exemplar requires at least one example")
    # Equal distance goes to the first match, so order matters
    nearest_element = min(training_data, key=lambda x: hamming_distance(x[0], query))
    return nearest_element[1]


# ---- TESTS ------

def run_tests():
    assert len(OBJECTS) == 16 and len(TEST_OBJECTS) == 10
    assert hamming_distance((0, 1, 1), (1, 0, 1)) == 2
    assert all(exemplar_predict(TRAINING_DATA, x) == label for x, label in TRAINING_DATA)
    # Equidistant conflicting examples: the earlier wins
    tie = [((0, 0), False), ((1, 1), True)]
    assert exemplar_predict(tie, (0, 1)) is False
    assert exemplar_predict(list(reversed(tie)), (0, 1)) is True
    try:
        exemplar_predict([], (0, 0))
    except ValueError:
        pass
    else:
        raise AssertionError("Empty training data must fail")
    print("Exemplar tests passed")


def run_experiment():
    correct = 0
    print("\nExemplar: six training objects, ten unseen objects")
    print("query          truth  prediction  correct")
    for x in TEST_OBJECTS:
        truth = hidden_concept(x)
        prediction = exemplar_predict(TRAINING_DATA, x)
        correct += prediction == truth
        print(f"{str(x):14} {str(truth):5}  {str(prediction):10}  {prediction == truth}")
    print(f"Accuracy: {correct}/{len(TEST_OBJECTS)}")


if __name__ == "__main__":
    run_tests()
    run_experiment()
