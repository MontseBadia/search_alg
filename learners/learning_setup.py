# -------------
# FOUR LEARNERS
# -------------

# Same concept in 4 different learners.
# 4 binary features, all 16 objects, hidden rule is "blue AND large"
# learners see same examples and get tested to see whether they disagree and why

# Setup for variants:
# 1- Exemplar - stores examples, hamming distance
# 2- Prototype - stores average per label, euclidean
# 3- Bayesian - probability distribution


# returns cartesian product, equivalent of a nested loop
from itertools import product


# EXPERIMENT SETUP --------------------------------

FEATURE_NAMES = ("blue", "large", "rounded", "striped")

# World - all 16 possible objects
OBJECTS = list(product((0, 1), repeat=len(FEATURE_NAMES)))

# Ground Truth - hidden rule assigning labels
def hidden_concept(x):
    blue, large, rounded, striped = x
    return bool(blue and large)

# Evidence - examples given
TRAINING_OBJECTS = [
    (1, 1, 0, 0),  # True
    (1, 1, 1, 1),  # True
    (0, 0, 0, 0),  # False
    (0, 0, 1, 0),  # False
    (1, 0, 0, 1), # Adding this example increased bayesian percentage
    (0, 1, 0, 1)  # Adding this example increased bayesian percentage even more
]
TRAINING_DATA = [(x, hidden_concept(x)) for x in TRAINING_OBJECTS]

# Queries - remaining examples not seen
TEST_OBJECTS = [x for x in OBJECTS if x not in TRAINING_OBJECTS]

