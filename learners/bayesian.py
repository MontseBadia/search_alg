# -------------
# BAYESIAN LEARNER
# -------------

# Uncertainty over candidate boolean programs

from learning_setup import FEATURE_NAMES, OBJECTS, TEST_OBJECTS, TRAINING_DATA, hidden_concept

from collections import defaultdict
from math import isclose

MAX_SIZE = 5  # Finite, size-bounded hypothesis space; a modeling assumption.


# Manual hypotheses
def h1(x):
    return bool(x[0]) # blue

def h2(x):
    return bool(x[1]) # large

def h3(x):
    return bool(x[0] and x[1]) # blue and large

def h4(x):
    return bool(x[0] or x[1]) # blue or large


# 1 DSL / INTERPRETER

# Hypotheses are ASTs, NOT the hand-written h1, h2, h3, h4 functions.
# ('var', i), ('not', child), ('and', left, right), ('or', left, right)
("var", 0) # blue, number is index
("var", 1) # large
("var", 2) # rounded
("var", 3) # striped

# Input
# ("var", 0), (1, 1, 0, 0)
# ("not", ("var", 0))
# ("and", ("var", 0), ("var", 1))

def evaluate_program(program, x):
    operation = program[0]

    if operation == "var":
        return bool(x[program[1]])
    if operation == "not":
        return not evaluate_program(program[1], x)
    if operation == "and":
        return evaluate_program(program[1], x) and evaluate_program(program[2], x)
    if operation == "or":
        return evaluate_program(program[1], x) or evaluate_program(program[2], x)

    raise ValueError(f"Unknown operation: {operation}")


# Prior: length is AST node count in this case.
# ("not", ("var", 0)) -> size 2
# ("and", ("var", 0), ("var", 1)) -> size 3
def program_size(program):
    operation = program[0]

    if operation == "var":
        return 1
    if operation == "not":
        return (1 + program_size(program[1]))
    if operation in ("and", "or"):
        return (1 + program_size(program[1]) + program_size(program[2]))
    raise ValueError(f"Unknown operation: {operation}")



# 2. ENUMERATE THE HYPOTHESIS SPACE -----------------------------------------
# Bottom-up DP: build every ordered AST, WITHOUT behavioral deduplication.


# Fininte hypothesis space
HYPOTHESES = [
    ("var", 0), # False
    ("var", 1), # False
    ("and", ("var", 0), ("var", 1)), # True
    ("or", ("var", 0), ("var", 1)) # False
]

def construct_op(op, value1, value2=None):
    if op == "var":
        return ("var", value1)
    if op == "not":
        return ("not", value1)
    if op == "and":
        return ("and", value1, value2)
    if op == "or":
        return ("or", value1, value2)
    raise ValueError(f"Operation not known: {op}")
    
def base_programs():
    return [construct_op("var", size) for size in range(len(FEATURE_NAMES))]

def programs_of_size(size, programs=None):
    if programs is None:
        programs = {}

    if 1 not in programs:
        programs[1] = base_programs()

    for i in range(2, size + 1):
        # reuse existing programs
        if i in programs:
            continue

        # Programs with 1 child
        programs[i] = [construct_op("not", child) for child in programs[i - 1]]

        # Binary programs, 2 children
        for left_size in range(1, i - 1):
            right_size = i - 1 - left_size
            for left in programs[left_size]:
                for right in programs[right_size]:
                    for op in ("and", "or"):
                        programs[i].append(construct_op(op, left, right))
                
    return programs[size]

def enumerate_hypotheses(max_size=MAX_SIZE):
    cache = {}
    hypotheses = []
    for size in range(1, max_size + 1):
        hypotheses.extend(programs_of_size(size, cache))
    return hypotheses, cache


# Deterministic likelihood: 1 if consistent, 0 otherwise
# Consistency filtering, used to check hypotheses
def consistent(program, training_data):
    return all(evaluate_program(program, x) == label for x, label in training_data)


# Returns unnormalised weights
def prior_weight(program):
    # negative exponent returns probability, decreasing as size grows
    return 2 ** (-program_size(program))


# Posterior: likelihood * prior, normalised across hypothesis space
# Set length_prior=False to reproduce uniform-prior behaviour
def posterior(hypotheses, training_data, length_prior=False):
    weights = [
        (prior_weight(hyp) if length_prior else 1.0)
        if consistent(hyp, training_data)  else 0.0
        for hyp in hypotheses
    ]
    total = sum(weights)
    if total == 0:
        raise ValueError("No consistent hypotheses")

    return [weight / total for weight in weights]


# 3. POSTERIOR PREDICTIVE ----------------------------------------------------

# Sums probabilities predicting True
def bayesian_predict(hypotheses, probabilities, query):
    if len(hypotheses) != len(probabilities):
        raise ValueError("One probability is required per hypothesis")
    
    return sum(
        probability for hyp, probability in zip(hypotheses, probabilities)
        if evaluate_program(hyp, query)
    )


# If above threshold, it predicts True
def predict_label(hypotheses, probabilities, query):
    return bayesian_predict(hypotheses, probabilities, query) >= 0.5


# 4. ANALYZE FUNCTIONS, NOT JUST PROGRAMS -----------------------------------
# BAYESIAN INFERENCE

# Likelihood: P(D | h) = 1 if ALL observations match, else 0.
# Assumption: the oracle's labels are noise-free.
def behaviour(program, objects):
    return tuple(evaluate_program(program, x) for x in objects)


# Sums weights for programs implementing the same function
def posterior_mass_by_behaviour(hypotheses, probabilities, objects):
    mass = defaultdict(float)
    for program, weight in zip(hypotheses, probabilities):
        if weight > 0:
            mass[behaviour(program, objects)] += weight
    return dict(mass)


def shortest_representatives(hypotheses, objects):
    representatives = {}
    for program in hypotheses:
        signature = behaviour(program, objects)
        if (signature not in representatives
                or program_size(program) < program_size(representatives[signature])):
            representatives[signature] = program
    return representatives


def print_posterior_summary(hypotheses, probabilities, training_data, objects):
    mass = posterior_mass_by_behaviour(hypotheses, probabilities, objects)
    representatives = shortest_representatives(hypotheses, objects)
    survivors = [h for h in hypotheses if consistent(h, training_data)]
    truth_signature = tuple(hidden_concept(x) for x in objects)
    print(f"Total programs: {len(hypotheses)}")
    print(f"Consistent programs: {len(survivors)}")
    print(f"Distinct consistent behaviors: {len(mass)}")
    print(f"Posterior mass on true function: {mass.get(truth_signature, 0.0):.6f}")
    print("Behavioral classes, ordered by total posterior mass:")
    for rank, (signature, weight) in enumerate(
        sorted(mass.items(), key=lambda item: item[1], reverse=True), 1
    ):
        marker = " <-- TRUE FUNCTION" if signature == truth_signature else ""
        print(f"  {rank}. mass={weight:.4f} program={representatives[signature]}{marker}")
    return mass


# Candidates for which positive-mass programs disagree
def disagreement_queries(hypotheses, probabilities, candidates):
    survivors = [h for h, weight in zip(hypotheses, probabilities) if weight > 0]
    return [
        x for x in candidates
        if len({evaluate_program(h, x) for h in survivors}) > 1
    ]


# 5. ACTIVE LEARNING ---------------------------------------------------------

# Pick an unlabeled disagreement closest to 0.5
def select_query(hypotheses, probabilities, candidates):
    if len(hypotheses) != len(probabilities):
        raise ValueError("One probability is required per hypothesis")
    informative = disagreement_queries(hypotheses, probabilities, candidates)
    if not informative:
        return None
    query = min(
        informative,
        key=lambda x: abs(bayesian_predict(hypotheses, probabilities, x) - 0.5)
    )
    return query, bayesian_predict(hypotheses, probabilities, query)


# Repeatedly ask oracle for one label, update and stop at agreement
def active_learning(hypotheses, initial_data, objects, oracle):
    data = list(initial_data)
    history = []
    while True:
        probabilities = posterior(hypotheses, data, length_prior=True)
        observed = {x for x, _ in data}
        candidates = [x for x in objects if x not in observed]
        selection = select_query(hypotheses, probabilities, candidates)
        if selection is None:
            print("STOP: no unobserved query distinguishes surviving functions.")
            return data, probabilities, history

        query, p_true = selection
        label = oracle(query)  # The ONLY oracle call in the learning loop.
        data.append((query, label))
        updated = posterior(hypotheses, data, length_prior=True)
        updated_masses = posterior_mass_by_behaviour(hypotheses, updated, objects)
        history.append((query, p_true, label, len(updated_masses)))
        print(f"Query {len(history)}: {query}, prior P(True)={p_true:.4f}, "
              f"oracle label={label}, behaviors remaining={len(updated_masses)}")
        print_posterior_summary(hypotheses, updated, data, objects)



# ---- TESTS -----

def run_tests():
    assert len(OBJECTS) == 16 and len(TRAINING_DATA) == 6 and len(TEST_OBJECTS) == 10
    x = (1, 1, 0, 1)
    cases = [
        (("var", 0), True),
        (("not", ("var", 0)), False),
        (("not", ("not", ("var", 0))), True),
        (("and", ("var", 0), ("var", 1)), True),
        (("and", ("var", 0), ("var", 2)), False),
        (("or", ("var", 0), ("var", 2)), True),
        (("and", ("or", ("var", 0), ("var", 1)), ("not", ("var", 0))), False),
    ]
    for program, expected in cases:
        assert evaluate_program(program, x) is expected

    manual = [
        ("var", 0), ("var", 1),
        ("and", ("var", 0), ("var", 1)),
        ("or", ("var", 0), ("var", 1)),
    ]
    fixture = [
        ((1, 1, 0, 0), True),
        ((1, 0, 0, 1), False),
        ((0, 1, 0, 1), False),
    ]
    assert [consistent(h, fixture) for h in manual] == [False, False, True, False]
    assert posterior(manual, fixture, length_prior=False) == [0, 0, 1, 0]
    assert posterior(manual, fixture[:1], length_prior=False) == [0.25] * 4
    assert [program_size(h) for h in manual] == [1, 1, 3, 3]
    assert posterior(manual, fixture[:1], length_prior=True) == [0.4, 0.4, 0.1, 0.1]
    assert bayesian_predict(manual, [0.25] * 4, (1, 0, 0, 0)) == 0.5

    hypotheses, cache = enumerate_hypotheses()
    assert [len(cache[size]) for size in range(1, 6)] == [4, 4, 36, 100, 708]
    assert len(hypotheses) == 852 and len(set(hypotheses)) == 852
    assert all(program_size(h) == size for size in range(1, 6) for h in cache[size])
    probabilities = posterior(hypotheses, TRAINING_DATA, length_prior=True)
    assert isclose(sum(probabilities), 1.0, abs_tol=1e-12)
    assert sum(consistent(h, TRAINING_DATA) for h in hypotheses) == 32
    mass = posterior_mass_by_behaviour(hypotheses, probabilities, OBJECTS)
    assert len(mass) == 3
    target = tuple(hidden_concept(x) for x in OBJECTS)
    assert isclose(mass[target], 15 / 19, abs_tol=1e-12)

    # If every hypothesis already agrees, do NOT request a redundant label.
    assert select_query([("var", 0)], [1.0], OBJECTS) is None
    # The active learner must not leak labels into the query choice.
    selection = select_query(hypotheses, probabilities, TEST_OBJECTS)
    assert selection is not None
    query, p_true = selection
    assert query in TEST_OBJECTS and 0 < p_true < 1
    assert query in disagreement_queries(hypotheses, probabilities, TEST_OBJECTS)
    print("Bayesian tests passed")
    return hypotheses, cache


def run_passive_experiment(hypotheses, cache):
    print("\n=== PASSIVE LEARNING: fixed six examples ===")
    print("size | programs | distinct behaviors | cumulative distinct")
    seen = set()
    for size in range(1, MAX_SIZE + 1):
        unique = {behaviour(h, OBJECTS) for h in cache[size]}
        seen.update(unique)
        print(f"{size:4} | {len(cache[size]):8} | {len(unique):18} | {len(seen):19}")

    probabilities = posterior(hypotheses, TRAINING_DATA, length_prior=True)
    print("\nFixed-data posterior:")
    print_posterior_summary(hypotheses, probabilities, TRAINING_DATA, OBJECTS)
    correct = 0
    print("\nquery          truth  P(True)  prediction")
    for x in TEST_OBJECTS:
        p_true = bayesian_predict(hypotheses, probabilities, x)
        prediction = p_true >= 0.5
        truth = hidden_concept(x)  # Scoring ONLY, not inference.
        correct += prediction == truth
        print(f"{str(x):14} {str(truth):5}  {p_true:7.4f}  {prediction}")
    print(f"Passive accuracy: {correct}/{len(TEST_OBJECTS)}")
    return probabilities


def run_active_experiment(hypotheses):
    print("\n=== ACTIVE LEARNING: extra labels are allowed ===")
    original_data = list(TRAINING_DATA)
    final_data, probabilities, history = active_learning(
        hypotheses, TRAINING_DATA, OBJECTS, oracle=hidden_concept
    )
    assert TRAINING_DATA == original_data  # No accidental mutation of baseline.
    print(f"Queries requested: {len(history)}")
    print(f"Fixed dataset still contains {len(TRAINING_DATA)} examples")
    print(f"Active dataset contains {len(final_data)} examples")
    return final_data, probabilities, history


if __name__ == "__main__":
    hypotheses, cache = run_tests()
    run_passive_experiment(hypotheses, cache)
    run_active_experiment(hypotheses)
