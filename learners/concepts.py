# -------------
# FOUR LEARNERS
# -------------

# Same concept in 4 different learners.
# 4 binary features, all 16 objects, hidden rule is "blue AND large"
# learners see same examples and get tested to see whether they disagree and why

# Variants:
# 1- Exemplar - stores examples, hamming distance
# 2- Prototype - stores average per label, euclidean

# Notes:
# - When two or more training examples are equally close to the query and have different labels,
# the learner chooses whatever comes first. So order matters.


from itertools import product # returns cartesian product, equivalent of a nested loop
from math import sqrt


FEATURE_NAMES = ("blue", "large", "rounded", "striped")

# World - all 16 possible objects
def all_objects():
    return list(product((0, 1), repeat=4))

# Ground Truth - hidden rule assigning labels
def hidden_concept(x):
    blue, large, rounded, striped = x
    return bool(blue and large)

objects = all_objects()

# Evidence - examples given
# training_objects = [
#     (1, 1, 0, 1),
#     (0, 1, 0, 1),
#     (1, 0, 0, 1),
# ]

training_objects = [
    (1, 1, 0, 0),  # True
    (1, 1, 1, 1),  # True
    (0, 0, 0, 0),  # False
    (0, 0, 1, 0),  # False
]

training_data = [(x, hidden_concept(x)) for x in training_objects]

# Queries - remaining examples not seen
test_data = [x for x in objects if x not in training_objects]


# --
# EXEMPLAR LEARNER -----
# --
# Complexity (n examples, d features): O(n*d) per query

def hamming_distance(a, b):
    return sum(a_item != b_item for a_item, b_item in zip(a, b))

# 1-Nearest neighbour learner
# Find training element with smallest distance from query, then return same label
def exemplar_predict(training_data, query):
    nearest_element = min(training_data, key=lambda x: hamming_distance(x[0], query))
    return nearest_element[1]


# --
# PROTOTYPE LEARNER -----
# --
# Complexity (n examples, d features):
# - O(n*d) per query (builds averages each call)
# - O(d) when not rebuilding average

def examples_with_label(training_data, target_label):
    return [x for x, label in training_data if label == target_label]

# This is called component wise average
def average_vector(examples):
    return tuple(sum(column) / len(column) for column in zip(*examples))

def euclidean_distance(a, b):
    return sqrt(sum((a_item - b_item) ** 2 for a_item, b_item in zip(a, b)))

def prototype_predict(training_data, query):
    positive_examples = examples_with_label(training_data, True)
    negative_examples = examples_with_label(training_data, False)

    # skip a label with no examples, its average is () and would be distance 0 to everything
    prototypes = []
    if positive_examples:
        prototypes.append((average_vector(positive_examples), True))
    if negative_examples:
        prototypes.append((average_vector(negative_examples), False))

    nearest_element = min(prototypes, key=lambda x: euclidean_distance(x[0], query))
    return nearest_element[1]





# -- Tests ----

if __name__ == "__main__":

    # for x in objects:
    #     print(x, hidden_concept(x))

    # print(test_data)

    print("Distances --------\n")

    v1 = (0, 1, 1)
    v2 = (1, 0, 1)

    print(f"hamming distance: {hamming_distance(v1, v2)}")
    assert hamming_distance(v1, v2) == 2

    # test if learners return correct labels
    for x, label in training_data:
        assert exemplar_predict(training_data, x) == label
        assert prototype_predict(training_data, x) == label

    print("\nTest queries --------\n")
    print("query          truth  exemplar  prototype")

    exemplar_correct = 0
    prototype_correct = 0
    for x in test_data:
        truth = hidden_concept(x)
        exemplar_answer = exemplar_predict(training_data, x)
        prototype_answer = prototype_predict(training_data, x)
        exemplar_correct += exemplar_answer == truth
        prototype_correct += prototype_answer == truth
        print(f"{x}  {truth!s:5}  {exemplar_answer!s:8}  {prototype_answer!s:9}")

    print(f"\nexemplar:  {exemplar_correct}/{len(test_data)}")
    print(f"prototype: {prototype_correct}/{len(test_data)}")
