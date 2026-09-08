# -----------------------
# FIBONACCI - DYNAMIC PROGRAMMING
# -----------------------

# Smallest problem where Dynamic Programming appears.
# DP searches over a graph of subproblems: node is subproblem, edges are recursive calls.

# Variants:
# - Fibonacci Brute Force - top-down
# - Fibonacci Memoizing - top-down
# - Fibonacci Tabulation - bottom up
# - Fibonacci Tabulation with Space Optimisation - bottom up


# Used to compare functions
# recursive_call_count and loop_count are not the same measurement, but similar
recursive_call_count = 0
loop_count = 0


# --- Fibonacci Brute Force ----
# recursion stack only, no table
# time: O(φⁿ), space O(n)

def fib_brute_force(n):
    global recursive_call_count
    recursive_call_count += 1

    if n <= 1:
        return n

    return fib_brute_force(n - 1) + fib_brute_force(n - 2)


# --- Fibonacci Memoizing ----
# memo array + O(n) stack
# time O(n), space O(n)

def fib_m(n, memory):
    global recursive_call_count
    recursive_call_count += 1

    if n <= 1:
        return n

    # Setting negative number because fibonacci is positive
    if memory[n] != -1:
        return memory[n]

    memory[n] = fib_m(n - 1, memory) + fib_m(n - 2, memory)
    return memory[n]

def fib_memoizing(n):
    memory = [-1] * (n + 1)
    return fib_m(n, memory)


# --- Fibonacci Tabulation ----
# table, no stack, reducible to O(1)
# time O(n), space O(n)

def fib_tabulation(n):
    global loop_count

    tab = [0] * (n + 1)
    if n >= 1: tab[1] = 1

    for i in range(2, n + 1):
        loop_count += 1
        tab[i] = tab[i - 1] + tab[i - 2]

    return tab[n]


# --- Fibonacci Tabulation with Space Optimisation ---
# no need to store an array as we only use previous and current
# same result as above but less space
# time O(n), space O(1)

def fib_tabulation_optimisation(n):
    global loop_count

    if n <= 1:
        return n

    previous, current = 0, 1

    for _ in range(2, n + 1):
        loop_count += 1
        previous, current = current, previous + current

    return current



# --- Tests ------

if __name__ == "__main__":
    n = 5
    print(fib_brute_force(n))
    print(fib_memoizing(n))
    print(fib_tabulation(n))
    print(fib_tabulation_optimisation(n))

    # Check if all methods agree on result
    for n in range(0, 20):
        assert fib_brute_force(n) == fib_memoizing(n) == fib_tabulation(n) == fib_tabulation_optimisation(n)

    print()
    print(f"{'n':>4} {'brute':>12} {'memo':>8} {'tab':>6}  {'tab_optimised':>6}")
    for n in (10, 20, 25, 30):
        recursive_call_count = 0
        fib_brute_force(n)
        brute = recursive_call_count

        recursive_call_count = 0
        fib_memoizing(n)
        memo = recursive_call_count

        loop_count = 0
        fib_tabulation(n)
        tab = loop_count

        loop_count = 0
        fib_tabulation_optimisation(n)
        tab_optimised = loop_count

        print(f"{n:>4} {brute:>12,} {memo:>8,} {tab:>6,}  {tab_optimised:>13,}")

        # Results
        #  n        brute     memo    tab  tab_optimised
        # 10          177       19      9       9
        # 20       21,891       39     19      19
        # 25      242,785       49     24      24
        # 30    2,692,537       59     29      29
