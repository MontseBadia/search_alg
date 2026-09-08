# -------------------------
# CONSTRAINT SATISFACTION PROBLEM
# -------------------------

# MRV decides which cell to try next
# Forward check / AC-3 decides which values are still good after assigning a cell value

from collections import deque
import copy

# -------- Helpers --------

def build_domains(board):
    domains = {}
    all_digits = set(range(1, 10))

    for r in range(9):
        for c in range(9):
            if board[r][c] != 0:
                continue # cell is filled

            row_values = {board[r][cc] for cc in range(9)} - {0}
            column_values = {board[rr][c] for rr in range(9)} - {0}

            box_values = set()
            br, bc = (r // 3) * 3, (c // 3) * 3
            for rr in range(br, br + 3):
                for cc in range(bc, bc + 3):
                    box_values.add(board[rr][cc])
            box_values -= {0}

            forbidden = row_values | column_values | box_values
            domains[(r, c)] = all_digits - forbidden

    return domains

def is_valid(row, col, num, board):
    if num in board[row]: return False
    if any(board[r][col] == num for r in range(9)): return False
    br, bc = (row // 3) * 3, (col // 3) * 3
    for r in range(br, br + 3):
        for c in range(bc, bc + 3):
            if board[r][c] == num: return False
    return True

def affected_cells(r, c, domains):
    cells = set()
    for cc in range(9):
        if (r, cc) in domains and cc != c: cells.add((r, cc))
    for rr in range(9):
        if (rr, c) in domains and rr != r: cells.add((rr, c))
    br, bc = (r // 3) * 3, (c // 3) * 3
    for rr in range(br, br + 3):
        for cc in range(bc, bc + 3):
            if (rr, cc) in domains and (rr, cc) != (r, c): cells.add((rr, cc))
    return cells


# -------- Sudoku (Backtracking) --------

def solve_sudoku_backtracking(board):
    recursive_call_count = 0

    def backtrack(domains):
        nonlocal recursive_call_count
        recursive_call_count += 1

        if not domains:
            print(f"recursive call count: {recursive_call_count}")
            return True # Solved

         # PICKING ANY CELL
        cell = next(iter(domains))
        r, c = cell
        cell_domain = domains[cell]

        for num in cell_domain:
            # PRUNING - REMOVING UNNECESSARY COMPONENTS
            if is_valid(r, c, num, board): # Redundant on first iteration, necessary afterwards
                board[r][c] = num
                del domains[cell]

                if backtrack(domains): return True

                domains[cell] = cell_domain
                board[r][c] = 0

        return False

    domains = build_domains(board)
    return backtrack(domains)


# -------- Sudoku (MRV) --------
# Sudoku solver with smart variable ordering

def solve_sudoku_mrv(board):
    recursive_call_count = 0

    def backtrack(domains):
        nonlocal recursive_call_count
        recursive_call_count += 1

        if not domains:
            print(f"recursive call count: {recursive_call_count}")
            return True # Solved

        # PICKING CELL WITH SMALLEST NUMBER OF DOMAINS
        cell = min(domains, key=lambda k: len(domains[k]) )
        r, c = cell
        cell_domain = domains[cell]

        for num in cell_domain:
            # PRUNING - REMOVING UNNECESSARY COMPONENTS
            if is_valid(r, c, num, board):
                board[r][c] = num
                del domains[cell]

                if backtrack(domains): return True

                domains[cell] = cell_domain
                board[r][c] = 0

        return False

    domains = build_domains(board)
    return backtrack(domains)


# -------- Sudoku (Forward Check) --------
# Forward Checking does one-step propagation

def solve_sudoku_forward_checking(board):
    recursive_call_count = 0

    def restore_domains(saved):
        for item, value in saved.items():
            domains[item] |= value  # Update operator

    def forward_check(cell, num):
        r, c = cell
        saved = {}

        for cell in affected_cells(r, c, domains):
            if cell not in domains:
                continue

            if num in domains[cell]:
                domains[cell].discard(num)
                saved[cell] = {num}

                # PRUNING - REMOVING UNNECESSARY COMPONENTS
                if not domains[cell]:
                    restore_domains(saved)
                    return None

        return saved

    def backtrack(domains):
        nonlocal recursive_call_count
        recursive_call_count += 1

        if not domains:
            print(f"recursive call count: {recursive_call_count}")
            return True # Solved

        cell = min(domains, key=lambda k: len(domains[k]) ) # Cell with smallest number of domains
        r, c = cell
        cell_domain = domains[cell]

        # No need to check if is_valid inside this loop because we update/un-update all cells every time
        for num in cell_domain:
            board[r][c] = num
            del domains[cell]
            saved = forward_check(cell, num)

            if saved is not None:
                if backtrack(domains): return True
                restore_domains(saved)

            domains[cell] = cell_domain
            board[r][c] = 0

        return False

    domains = build_domains(board)
    return backtrack(domains)


# -------- Sudoku (Constraint Propagation) --------
# ARC Consistency - propagates until fixed point
# This can solve hard sudokus sometimes with little backtracking
# Textbook ac3 queues arcs, here i'm queuing cells.

def solve_sudoku_constraint_propagation(board):
    recursive_call_count = 0

    def restore_domains(saved):
        for item, value in saved.items():
            domains[item] |= value

    def ac3_propagate(original_cell):
        saved = {}
        worklist = deque([original_cell])

        while worklist:
            cell = worklist.popleft()
            r, c = cell

            if cell not in domains:
                continue

            if len(domains[cell]) == 1:
                forced_value = next(iter(domains[cell])) # grab only element

                for peer in affected_cells(r, c, domains):
                    if peer not in domains:
                        continue
                    
                    if forced_value in domains[peer]:
                        domains[peer].discard(forced_value)
                        saved.setdefault(peer, set()).add(forced_value)

                        if not domains[peer]:
                            restore_domains(saved)
                            return None

                        # In sudoku, it makes sense to only enqueue when one cell is left in domain
                        if len(domains[peer]) == 1:
                            worklist.append(peer)

        return saved

    def backtrack(domains):
        nonlocal recursive_call_count
        recursive_call_count += 1

        if not domains:
            print(f"recursive call count: {recursive_call_count}")
            return True # Solved

        cell = min(domains, key=lambda k: len(domains[k]) ) # Cell with smallest number of domains
        r, c = cell
        cell_domain = domains[cell]

        # No need to check if is_valid inside this loop because we update/un-update all cells every time
        for num in cell_domain:
            board[r][c] = num
            domains[cell] = {num}
            saved = ac3_propagate(cell)
            del domains[cell]

            if saved is not None:
                if backtrack(domains): return True
                restore_domains(saved)

            domains[cell] = cell_domain
            board[r][c] = 0

        return False

    domains = build_domains(board)
    return backtrack(domains)




# ---- Tests ----

if __name__ == "__main__":
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

    harder_puzzle = [
        [0,0,0, 6,0,0, 4,0,0],
        [7,0,0, 0,0,3, 6,0,0],
        [0,0,0, 0,9,1, 0,8,0],
        [0,0,0, 0,0,0, 0,0,0],
        [0,5,0, 1,8,0, 0,0,3],
        [0,0,0, 3,0,6, 0,4,5],
        [0,4,0, 2,0,0, 0,6,0],
        [9,0,3, 0,0,0, 0,0,0],
        [0,2,0, 0,0,0, 1,0,0],
    ]

    puzzle1 = copy.deepcopy(puzzle)
    puzzle2 = copy.deepcopy(puzzle)
    puzzle3 = copy.deepcopy(puzzle)
    puzzle4 = copy.deepcopy(puzzle)

    harder_puzzle3 = copy.deepcopy(harder_puzzle)
    harder_puzzle4 = copy.deepcopy(harder_puzzle)

    # Example of domains
    # domains: {(0, 2): {1, 2, 4}, (0, 3): {2, 6}, (0, 5): {8, 2, 4, 6}}

    solved1 = solve_sudoku_backtracking(puzzle1)
    print("backtracking solved:", solved1)
    for row in puzzle1:
        print(row)

    solved2 = solve_sudoku_mrv(puzzle2)
    print("mrv solved:", solved2)
    for row in puzzle2:
        print(row)

    solved3 = solve_sudoku_forward_checking(puzzle3)
    print("forward checking solved:", solved3)
    for row in puzzle3:
        print(row)

    solved4 = solve_sudoku_constraint_propagation(puzzle4)
    print("ac3 solved:", solved4)
    for row in puzzle4:
        print(row)

    # Harder puzzle

    hardersolved3 = solve_sudoku_forward_checking(harder_puzzle3)
    print("forward checking solved:", hardersolved3)
    for row in harder_puzzle3:
        print(row)

    hardersolved4 = solve_sudoku_constraint_propagation(harder_puzzle4)
    print("ac3 solved:", hardersolved4)
    for row in harder_puzzle4:
        print(row)

    # === EASY (51 empty) ===
    #   backtracking    solved=True calls=  4354 valid_grid=True
    #   mrv             solved=True calls=   111 valid_grid=True
    #   forward_check   solved=True calls=    52 valid_grid=True
    #   ac3             solved=True calls=    52 valid_grid=True

    # === HARDER (60 empty) ===
    #   backtracking    solved=True calls=11088840 valid_grid=True
    #   mrv             solved=True calls=908188 valid_grid=True
    #   forward_check   solved=True calls=  4001 valid_grid=True
    #   ac3             solved=True calls=   991 valid_grid=True

    # empty cells: easy = 51  harder = 58
