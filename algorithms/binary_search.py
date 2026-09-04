# -------------------
# BINARY SEARCH
# -------------------

def binary_search(my_list, item):
    low = 0
    high = len(my_list) - 1

    while low <= high:
        mid = int((low + high) / 2)
        guess = my_list[mid]

        # print(f"mid: {mid}")
        # print(f"guess: {guess}")

        if guess == item:
            return mid
        if guess > item:
            high = mid - 1
        if guess < item:
            low = mid + 1
    return None

if __name__ == "__main__":
    my_list = [1, 2, 3, 4, 5, 6, 7, 8]

    print(binary_search(my_list, 8))

    # Output
    # 7