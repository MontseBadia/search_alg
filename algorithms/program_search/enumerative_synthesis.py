# -------------------------
# BOTTOM-UP ENUMERATIVE PROGRAM SYNTHESIS
# -------------------------
# (BARE SEARCH)

from time import perf_counter

# This is like iterative deepening search over program space instead of a graph.
# AST node count is the program cost
# Search returns smallest program, the one with minimum AST size
# seen_behaviours is like visited used in other files

# Variants:
# Each searcher is a loop over one enumerator. Enumerator is the variant:
# 1- Raw enumeration      - no pruning          - test_candidates              - program_by_size
# 2- Observational equiv. - dedupe by behaviour - test_candidates_by_behaviour - program_by_size_by_behaviour
# 3- Same, levels cached  - dedupe + memo       - test_candidates_by_behaviour_improved    - program_by_size_by_behaviour_improved

# EXAMPLE
# examples = [
#     (1, 3),
#     (2, 5),
#     (3, 7),
#     (4, 9),
# ]
# Synthetizer return value is something like:
# (x * (1 + 1)) + 1

# bare enumeration
# → observational equivalence
# → full synthesizer + measurements
# → typed DSL
# → richer primitives
# → cost-guided enumeration
# → ARC-style DSL
# maybe adding more operators later

# AST representation
# → interpreter
# → AST cost
# → bottom-up enumeration
# → synthesis goal test
# → measured combinatorial explosion
# → observational equivalence pruning
# → cached DP-style enumeration
# → bounded failure behavior

# WHY THIS CANNOT SCALE TO ARC
# Program space grows exponentially in program size, and ARC needs composition that
# are much bigger than anything here, and pruning does not reduce enough.


# 1------
# Represent expression as AST
# (x * 2) + 1

expression = (
    "add",
        ("mul",
            ("var",),
            ("const", 2)),
        ("const", 1)
    )

# 2------
# Write interpreter

def evaluate_program(program, x):
    operation = program[0]

    if operation == "var":
        return x

    if operation == "const":
        return program[1]

    if operation == "add":
        return evaluate_program(program[1], x) + evaluate_program(program[2], x)

    if operation == "mul":
        return evaluate_program(program[1], x) * evaluate_program(program[2], x)

    if operation == "sub": # Subtraction
        return evaluate_program(program[1], x) - evaluate_program(program[2], x)

    raise ValueError(f"Unknown operation: {operation}")

# 3------
# Calculate program AST size

def program_size(program):
    operation = program[0]

    if operation in ("var", "const"):
        return 1

    if operation in ("add", "mul", "sub"):
        return (1 + program_size(program[1]) + program_size(program[2]))

    raise ValueError(f"Unknown operation: {operation}")

# 4------
# Create programs by AST size

# helper
def construct_op(op, value1 = None, value2 = None):
    if op == "var":
        return ("var",)

    if op == "const":
        return ("const", value1)

    if op == "add":
        return ("add", value1, value2)
    
    if op == "mul":
        return ("mul", value1, value2)

    if op == "sub":
        return ("sub", value1, value2)

    raise ValueError(f"Unknown operation: {op}")

CONSTANTS = [0, 1, 2]

def terminal_programs():
    return [construct_op("var")] + [construct_op("const", c) for c in CONSTANTS]

def program_by_size(size):
    programs = {}
    programs[1] = terminal_programs()

    if size == 1:
        return programs[1]

    if size % 2 == 0:
        return []

    # 3, 5, 7...
    for i in range(3, size + 1, 2):
        programs[i] =  []

        for op in ("add", "mul", "sub"):
            for left_size in range(1, i - 1, 2):
                right_size = i - 1 - left_size
        
                for left in programs[left_size]:
                    for right in programs[right_size]:
                        programs[i].append(construct_op(op, left, right))

    return programs[size]

    # i=7
    # left=1, right=5
    # left=3, right=3
    # left=5, right=1

# 5------
# Test candidates against input/output examples

def program_solved(program, examples):
    for example in examples:
        if evaluate_program(program, example[0]) != example[1]:
            return False 
    return True

def test_candidates(examples, max_size = 9):
    # Count over ODD NUMBERS
    # max_size caps the search so unsolvable examples don't keep hanging
    for size in range(1, max_size + 1, 2):
        for program in program_by_size(size):
            if program_solved(program, examples):
                return program

    return None


# 6------
# Watch combinatorial explosion (by adding depth levels and also by adding operators - I added "sub")
# search space grows extremely fast, eventually running out of memory

# Note
# Caching comes with its own bookkeeping overhead
# This is why for size 11, cached takes slightly longer than pruned
# Memoizing only pays off when recomputed work exceeds bookkeeping overhead

def measure_explosion(examples, sizes = (1, 3, 5, 7, 9, 11)):
    print(f"{'size':>6} {'raw':>12} {'pruned':>10} {'cached':>10}"
          f"{'raw s':>10} {'pruned s':>10} {'cached s':>10}")

    searcher = Searcher()

    for size in sizes:
        raw_start = perf_counter()
        raw = program_by_size(size)
        raw_time = perf_counter() - raw_start

        pruned_start = perf_counter()
        pruned = program_by_size_by_behaviour(size, examples)
        pruned_time = perf_counter() - pruned_start

        cached_start = perf_counter()
        cached = program_by_size_by_behaviour_improved(size, examples, searcher)
        cached_time = perf_counter() - cached_start

        print(f"{size:>6} {len(raw):>12,} {len(pruned):>10,} {len(cached):>10,}"
              f"{raw_time:>10.4f} {pruned_time:>10.4f} {cached_time:>10.4f}")


# 7------
# Add semantic/observational deduplication
# Observational equivalence pruning

def program_by_size_by_behaviour(size, examples):
    if size % 2 == 0:
        return []

    # Prune on same inputs we are solving
    # observational equivalence with respect to examples
    input_checks = [x for x, _ in examples]

    def behaviour(program):
        # Behaviour should be ordered so we can compare correctly
        return tuple(evaluate_program(program, x) for x in input_checks)

    programs = { 1: [] }
    seen_behaviours = set()

    for program in terminal_programs():
        candidate_behaviour = behaviour(program)

        if candidate_behaviour not in seen_behaviours:
            seen_behaviours.add(candidate_behaviour)
            programs[1].append(program)

    if size == 1:
        return programs[1]

    # 3, 5, 7...
    for i in range(3, size + 1, 2):
        programs[i] =  []

        for op in ("add", "mul", "sub"):
            for left_size in range(1, i - 1, 2):
                right_size = i - 1 - left_size
        
                for left in programs[left_size]:
                    for right in programs[right_size]:
                        candidate_op = construct_op(op, left, right)
                        candidate_behaviour = behaviour(candidate_op)

                        if candidate_behaviour not in seen_behaviours:
                            seen_behaviours.add(candidate_behaviour)
                            programs[i].append(candidate_op)

    return programs[size]

# 8------
# Test candidates by behaviour

def test_candidates_by_behaviour(examples, max_size = 9):
    # Count over ODD NUMBERS
    # max_size caps the search so unsolvable examples don't keep hanging
    for size in range(1, max_size + 1, 2):
        for program in program_by_size_by_behaviour(size, examples):
            if program_solved(program, examples):
                return program

    return None


# 9------
# Improve behaviour check by not recomputing same program sizes over and over again

def program_by_size_by_behaviour_improved(size, examples, searcher):
    if size % 2 == 0:
        return []

    input_checks = [x for x, _ in examples]

    def behaviour(program):
        # Behaviour should be ordered so we can compare correctly
        return tuple(evaluate_program(program, x) for x in input_checks)

    def register_candidate(program, program_size):
        candidate_behaviour = behaviour(program)

        if candidate_behaviour not in searcher.seen_behaviours:
            searcher.seen_behaviours.add(candidate_behaviour)
            searcher.programs[program_size].append(program)

    # Base case
    if 1 not in searcher.programs:
        searcher.programs[1] = []

        for program in terminal_programs():
            register_candidate(program, 1)

    # 3, 5, 7...
    for current_size in range(3, size + 1, 2):
        # Design choice: one searcher instance belongs to one fixed set of examples
        # If need to test across different tasks, this needs fixing
        if current_size in searcher.programs:
            continue

        searcher.programs[current_size] =  []

        for op in ("add", "mul", "sub"):
            for left_size in range(1, current_size - 1, 2):
                right_size = current_size - 1 - left_size
        
                for left in searcher.programs[left_size]:
                    for right in searcher.programs[right_size]:

                        candidate = construct_op(op, left, right)
                        register_candidate(candidate, current_size)

    return searcher.programs[size]


# 10------
# Test candidates by behaviour improved
# Integrates behaviour-pruned enumerator with synthesis

class Searcher:
    def __init__(self):
        self.programs = {}
        self.seen_behaviours = set()

def test_candidates_by_behaviour_improved(examples, max_size = 9):
    # Count over ODD NUMBERS
    searcher = Searcher()

    for size in range(1, max_size + 1, 2):
        for program in program_by_size_by_behaviour_improved(size, examples, searcher):
            if program_solved(program, examples):
                return program

    return None


# 11------
# DSL should be typed so it can accept different types








# --- Tests------

if __name__ == "__main__":
    program1 = (
        "add",
        ("mul", ("var",), ("const", 2)),
        ("const", 1),
    )

    program2 = (
        "mul",
            ("var",),
            ("var",)
        )

    print(f"\nprogram1 evaluate: {evaluate_program(program1, 3)}")
    print(f"program1 size: {program_size(program1)}\n")
    print(f"program2 evaluate: {evaluate_program(program2, 3)}")
    print(f"program2 size: {program_size(program2)}\n")
    print(f"program by size 1: {program_by_size(1)}\n")

    examples = [
        (1, 3),
        (2, 5),
        (3, 7),
        (4, 9),
    ]

    # See combinatorial explosion, and what each pruning step does to it
    print("combinatorial explosion ----\n")
    measure_explosion(examples)

    print("\ntest candidates ----")
    print(f"{test_candidates(examples)}")
    # result test candidates: ('add', ('var',), ('add', ('var',), ('const', 1)))
    # (x * (1 + 1)) + 1
    # x + x + 1

    print("\ntest candidates by behaviour ----")
    print(f"{test_candidates_by_behaviour(examples)}")

    print("\ntest candidates by behaviour improved ----")
    print(f"{test_candidates_by_behaviour_improved(examples)}")

    # FAILURE CASE
    unsolvable = [
        (1, 2),
        (2, 3),
        (3, 100),
    ]

    print("\nunsolvable examples ----")
    print(f"raw:      {test_candidates(unsolvable)}")
    print(f"pruned:   {test_candidates_by_behaviour(unsolvable)}")
    print(f"cached:   {test_candidates_by_behaviour_improved(unsolvable)}")

    assert test_candidates(unsolvable) is None
    assert test_candidates_by_behaviour(unsolvable) is None
    assert test_candidates_by_behaviour_improved(unsolvable) is None
