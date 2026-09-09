# -----------------------
# COIN CHANGE - DYNAMIC PROGRAMMING
# -----------------------

# Find fewest coins that add up to amount, you can repeat each coin.
# State is not handled like it happened in fibonacci. State = remaining, amount still owed
# Greedy returns worse answers here. Coins [1,3,4] amount 6, it takes 4+1+1

# Variants:
# 1- Brute Force
# 2- Memoizing
# 3- Tabulation

# Used to compare functions
# recursive_call_count and loop_count are not the same measurement, but similar
recursive_call_count = 0
loop_count = 0


# -- Brute Force --
# No dynamic programming yet, recalculating best(n) multiple times

# coins = [1, 3, 4]
# amount = 6
# change(6)
# │
# ├─ coin 1
# │   └─ change(5)
# │       ├─ coin 1 → change(4)
# │       ├─ coin 3 → change(2)
# │       └─ coin 4 → change(1)
# │
# ├─ coin 3
# │   └─ change(3)
# │       ├─ coin 1 → change(2)
# │       ├─ coin 3 → change(0) ✓
# │       └─ coin 4 → change(-1) ✗
# │
# └─ coin 4
#     └─ change(2)
#         ├─ coin 1 → change(1)
#         ├─ coin 3 → change(-1) ✗
#         └─ coin 4 → change(-2) ✗

def coin_change_brute_force(coins, amount):
    if not coins: return -1

    def best(rem):
        global recursive_call_count
        recursive_call_count += 1

        if rem == 0:
            return 0
        if rem < 0:
            return float("inf") # Infinity

        return 1 + min(best(rem - c) for c in coins)

    result = best(amount)
    return -1 if result == float("inf") else result


# -- Memoizing --
def coin_change_memoizing(coins, amount):
    if not coins: return -1

    def best(rem, memory):
        global recursive_call_count
        recursive_call_count += 1

        if rem == 0:
            return 0
        if rem < 0:
            return float("inf") # Infinity

        if rem in memory:
            return memory[rem]

        memory[rem] = 1 + min(best(rem - c, memory) for c in coins)
        return memory[rem]

    memory = {}
    result = best(amount, memory)
    return -1 if result == float("inf") else result


# -- Tabulation --
# Ascending order. Topological order
def coin_change_tabulation(coins, amount):
    global loop_count

    best = [float("inf")] * (amount + 1)
    best[0] = 0

    for i in range(1, amount + 1):
        for c in coins:
            # no negative index generated
            if c <= i:
                loop_count += 1
                best[i] = min(best[i], 1 + best[i - c])

    result = best[amount]
    return -1 if result == float("inf") else result



# ---- Tests -----

if __name__ == "__main__":
    # (coins, amount, expected)
    cases = [
        ([1, 2, 5], 11, 3),
        ([1, 3, 4], 6, 2),
        ([1, 7, 10], 14, 2),
        ([3, 5], 11, 3),
        ([5, 7], 13, -1),
        ([2, 4], 7, -1),
        ([2], 3, -1),
        ([1], 0, 0),
        ([], 5, -1),
        ([1, 5, 10, 25], 63, 6),
    ]

    # Limiting brute force
    BRUTE_LIMIT = 14

    for coins, amount, expected in cases:
        assert coin_change_memoizing(coins, amount) == expected, (coins, amount) # Error info
        assert coin_change_tabulation(coins, amount) == expected, (coins, amount)
        if amount <= BRUTE_LIMIT:
            assert coin_change_brute_force(coins, amount) == expected, (coins, amount)

    print(f"all variants agree on {len(cases)} cases")

    print()
    print(f"{'coins':<16} {'amount':>7} {'best':>5} {'brute':>9} {'memo':>6} {'tab':>5}")

    for coins, amount, expected in cases:
        recursive_call_count = 0
        coin_change_memoizing(coins, amount)
        memo = recursive_call_count

        loop_count = 0
        coin_change_tabulation(coins, amount)
        tab = loop_count

        if amount <= BRUTE_LIMIT:
            recursive_call_count = 0
            coin_change_brute_force(coins, amount)
            brute = f"{recursive_call_count:,}"
        else:
            brute = "skipped"

        print(f"{str(coins):<16} {amount:>7} {expected:>5} {brute:>9} {memo:>6,} {tab:>5,}")
