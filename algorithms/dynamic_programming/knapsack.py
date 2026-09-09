# -----------------------
# KNAPSACK - DYNAMIC PROGRAMMING
# -----------------------

def knapsack(weights, values, capacity):
    n = len(weights)
    # table represents the best value i can get if only allowed to take i items, and bag holds w kgs max
    # table is initialised with zero rows and zero columns
    table = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(capacity + 1):

            # value of element on top in the table
            skip = table[i - 1][w]

            if weights[i - 1] <= w:
                # values[i - 1] -> value of the item in this row
                # weights[i - 1] -> weight of the item in this row
                # w - weights[i - 1] -> room left in the bag after item goes in
                # table[i - 1][...] -> looking at row above for an earlier item for that leftover space
                take = values[i - 1] + table[i - 1][w - weights[i - 1]]
                table[i][w] = max(skip, take)
            else:
                table[i][w] = skip
    
    return table[n][capacity]



# ---- Tests -----

if __name__ == "__main__":
    weights = [5, 4, 3, 2]
    values  = [60, 50, 40, 30]
    print(knapsack(weights, values, 10))   # 130

    # | items ↓ \ bag →.  | 0 | 1 | 2  | 3  | 4  | 5  | 6  | 7  | 8   |  9  | 10  |
    # |-------------------|-------|--- |--- |--- |--- |--- |--- |---  |---  |---  |
    # | **(none)**        | 0 | 0 | 0  | 0  | 0  | 0  | 0  | 0  | 0   | 0   | 0   |
    # | **+A** (5kg, $60) | 0 | 0 | 0  | 0  | 0  | 60 | 60 | 60 | 60  | 60  | 60  |
    # | **+B** (4kg, $50) | 0 | 0 | 0  | 0  | 50 | 60 | 60 | 60 | 60  | 110 | 110 |
    # | **+C** (3kg, $40) | 0 | 0 | 0  | 40 | 50 | 60 | 60 | 90 | 100 | 110 | 110 |
    # | **+D** (2kg, $30) | 0 | 0 | 30 | 40 | 50 | 70 | 80 | 90 | 100 | 120 | **130** | -> SOLUTION
