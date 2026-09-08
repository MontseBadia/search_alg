# -------------------------
# GREEDY BEST-FIRST SEARCH
# -------------------------

# Best-first search with f(n) = heuristic. Same skeleton as dijkstra / a*. Ignores cost.
# Does not ensure optimal path.


from collections import defaultdict


class Graph:
    def __init__(self):
        self.graph = defaultdict(dict)

    def add_edge(self, u, v, weight, undirected=False):
        self.graph[u][v] = weight
        if undirected:
            self.graph[v][u] = weight

    # -------- Targeted --------
    # Returns some path start->end and its cost.
    # `visited` is required — greedy will loop forever on cyclic graphs
    # without it, because it has no cost-based reason to stop revisiting.

    def greedy_best_first(self, start, end, heuristic):
        def h(n):
            return heuristic.get(n, 0)

        queue = {start}                       # frontier: set of nodes to try
        visited = {start}                     # nodes already expanded
        parent = {start: None}
        cost_to = {start: 0}                  # g(n), kept only for reporting

        while queue:
            item = min(queue, key=h)
            queue.remove(item)

            if item == end:
                path, node = [], item
                while node is not None:
                    path.append(node)
                    node = parent[node]
                return path[::-1], cost_to[end]

            for child, weight in self.graph[item].items():
                if child not in visited:
                    visited.add(child)
                    queue.add(child)
                    parent[child] = item
                    cost_to[child] = cost_to[item] + weight

        return None, float("inf")


# ---- Tests ----

if __name__ == "__main__":
    print("\n----- GREEDY VS OPTIMAL ------\n")

    # the failure case:
    # A --1--> B --1--> C --1--> D --1--> GOAL   (true shortest, cost 4)
    # A --10-> X --1--> GOAL                      (decoy, cost 11)
    g = Graph()
    g.add_edge('A', 'B', 1); g.add_edge('B', 'C', 1)
    g.add_edge('C', 'D', 1); g.add_edge('D', 'GOAL', 1)
    g.add_edge('A', 'X', 10); g.add_edge('X', 'GOAL', 1)

    heuristic = {'A': 5, 'B': 4, 'C': 3, 'D': 1, 'X': 1, 'GOAL': 0}

    path, cost = g.greedy_best_first('A', 'GOAL', heuristic)
    print("A -> GOAL:", path, "cost:", cost)
    # Greedy picks X first (h=1) over B (h=4), then reaches GOAL via cost 11.
    # A* picks B first because f(X) = 10+1 = 11 > f(B) = 1+4 = 5, and follows
    # the true optimal route of cost 4.

    assert path == ['A', 'X', 'GOAL'] and cost == 11
