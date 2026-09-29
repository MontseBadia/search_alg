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
SIX_EXAMPLE_OBJECTS = [
    (1, 1, 0, 0),  # True
    (1, 1, 1, 1),  # True
    (0, 0, 0, 0),  # False
    (0, 0, 1, 0),  # False
    (1, 0, 0, 1), # Adding this example increased bayesian percentage
    (0, 1, 0, 1)  # Adding this example increased bayesian percentage even more
]
SIX_EXAMPLE_DATA = [(x, hidden_concept(x)) for x in SIX_EXAMPLE_OBJECTS]

# Add these in order for the seven- and eight-example interventions.
COUNTEREXAMPLE_OBJECTS = [(0, 1, 1, 0), (1, 0, 1, 0)]
COUNTEREXAMPLE_DATA = [(x, hidden_concept(x)) for x in COUNTEREXAMPLE_OBJECTS]
EIGHT_EXAMPLE_OBJECTS = SIX_EXAMPLE_OBJECTS + COUNTEREXAMPLE_OBJECTS
EIGHT_EXAMPLE_DATA = SIX_EXAMPLE_DATA + COUNTEREXAMPLE_DATA

# Queries - remaining examples not seen in each condition
SIX_EXAMPLE_TEST_OBJECTS = [x for x in OBJECTS if x not in SIX_EXAMPLE_OBJECTS]
EIGHT_EXAMPLE_TEST_OBJECTS = [x for x in OBJECTS if x not in EIGHT_EXAMPLE_OBJECTS]

# The original learner demos use the six-example baseline.
TRAINING_OBJECTS = SIX_EXAMPLE_OBJECTS
TRAINING_DATA = SIX_EXAMPLE_DATA
TEST_OBJECTS = SIX_EXAMPLE_TEST_OBJECTS
