# -------------------------
# BACKTRACKING
# -------------------------

# Backtracking is a pattern, not an algorithm. It's DFS for building solutions
# incrementally. Uses pruning to release candidates that lead nowhere.
# Every algorithm follows the principle: CHOOSE, EXPLORE AND UN-CHOOSE


# -------- Example 1: Subsets (no constraints — pure structural) --------

def all_subsets(nums):
    result, current = [], []

    def backtrack(index):
        if index == len(nums):
            result.append(current[:])       # copy!
            return
        # Two choices at each element: include it, or don't
        # Skip
        backtrack(index + 1)
        # Include
        current.append(nums[index])          # choose
        backtrack(index + 1)                 # explore
        current.pop()                        # un-choose

    backtrack(0)
    return result


# -------- Example 2: Permutations (uses a "used" set as constraint) --------

def all_permutations(nums):
    result, current, used = [], [], set()

    def backtrack():
        if len(current) == len(nums):
            result.append(current[:])
            return
        for num in nums:
            if num in used:                  # prune: can't reuse
                continue
            used.add(num); current.append(num)     # choose
            backtrack()                             # explore
            used.remove(num); current.pop()        # un-choose

    backtrack()
    return result


# -------- Example 3: N-Queens (constraint-heavy) --------

def n_queens(n):
    result, board = [], []

    def is_safe(row, col):
        for r, c in enumerate(board):
            if c == col or abs(r - row) == abs(c - col):
                return False
        return True

    def backtrack(row):
        if row == n:
            result.append(board[:])
            return
        for col in range(n):
            if is_safe(row, col):            # prune: no attacks
                board.append(col)             # choose
                backtrack(row + 1)            # explore
                board.pop()                   # un-choose

    backtrack(0)
    return result


# -------- Example 4: Sudoku (multi-constraint) --------
# Shows constraints from multiple sources (row, column, box) combining
# to create severe pruning. Shows the "first-empty-cell" variant.

def solve_sudoku(board):
    def find_empty():
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    return r, c
        return None

    def is_valid(row, col, num):
        if num in board[row]: return False
        if any(board[r][col] == num for r in range(9)): return False
        br, bc = (row // 3) * 3, (col // 3) * 3
        for r in range(br, br + 3):
            for c in range(bc, bc + 3):
                if board[r][c] == num: return False
        return True

    def backtrack():
        spot = find_empty()
        if spot is None:
            return True                       # solved
        r, c = spot
        for num in range(1, 10):
            if is_valid(r, c, num):
                board[r][c] = num             # choose
                if backtrack(): return True   # explore
                board[r][c] = 0               # un-choose
        return False

    return backtrack()


# ---- Tests ----

if __name__ == "__main__":
    print("\n----- SUBSETS ------\n")

    subsets = all_subsets([1, 2, 3])
    print("all_subsets([1,2,3]):", subsets)
    print("count:", len(subsets), "(expected 2^3 = 8)")

    print("\n----- PERMUTATIONS ------\n")

    perms = all_permutations([1, 2, 3])
    print("all_permutations([1,2,3]):", perms)
    print("count:", len(perms), "(expected 3! = 6)")

    print("\n----- N-QUEENS ------\n")

    # board[row] = col -- one queen per row, board's index IS the row
    for n in (4, 6, 8):
        solutions = n_queens(n)
        print(f"n_queens({n}): {len(solutions)} solutions")
    print("first 4-queens solution (col per row):", n_queens(4)[0])

    print("\n----- SUDOKU ------\n")

    # classic example puzzle, 0 = empty cell
    puzzle = [
        [5, 3, 0,  0, 7, 0,  0, 0, 0],
        [6, 0, 0,  1, 9, 5,  0, 0, 0],
        [0, 9, 8,  0, 0, 0,  0, 6, 0],
        [8, 0, 0,  0, 6, 0,  0, 0, 3],
        [4, 0, 0,  8, 0, 3,  0, 0, 1],
        [7, 0, 0,  0, 2, 0,  0, 0, 6],
        [0, 6, 0,  0, 0, 0,  2, 8, 0],
        [0, 0, 0,  4, 1, 9,  0, 0, 5],
        [0, 0, 0,  0, 8, 0,  0, 7, 9],
    ]
    solved = solve_sudoku(puzzle)
    print("solved:", solved)
    for row in puzzle:
        print(row)
