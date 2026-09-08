# -------------------------
# BEAM SEARCH
# -------------------------

# Beam search is BFS with top-k most promising nodes at each level. k = beam width.
# Each iteration processes entire beam at once, not one node at a time.
# Does not necessarily return the optimal answer. Trades optimality for speed.

# k = 1 -> greedy
# k = infinity -> bfs


from collections import defaultdict


class Graph:
    def __init__(self):
        self.graph = defaultdict(dict)

    def add_edge(self, u, v, weight, undirected=False):
        self.graph[u][v] = weight
        if undirected:
            self.graph[v][u] = weight

    # -------- Beam Search --------

    def beam_search(self, start, end, k, max_iter=100):
        beam = [(start, 0)]                   # current beam: list of (state, cost)
        distance = {start: 0}                 # best-known cost per node ever
        parent = {start: None}

        for _ in range(max_iter):
            candidates = []

            # 1) Expand EVERY node in the current beam, pool their children
            for state, cost in beam:
                if state == end:
                    path, node = [], state
                    while node is not None:
                        path.append(node)
                        node = parent[node]
                    return path[::-1], cost

                for child, weight in self.graph[state].items():
                    new_cost = cost + weight
                    # Skip if we've already reached this child cheaper before
                    if child not in distance or new_cost < distance[child]:
                        candidates.append((child, new_cost, state))

            if not candidates:
                return None

            # 2) Dedupe by state (two beam nodes may generate the same child)
            best_by_state = {}
            for child, new_cost, from_node in candidates:
                best_by_state[child] = min(
                    best_by_state.get(child, (float("inf"), None)),
                    (new_cost, from_node),
                )

            # 3) Trim GLOBALLY to top k across the whole candidate pool
            trimmed = sorted(best_by_state.items(), key=lambda x: x[1][0])[:k]

            # 4) Commit as the next beam and update bookkeeping
            beam = []
            for child, (new_cost, from_node) in trimmed:
                distance[child] = new_cost
                parent[child] = from_node
                beam.append((child, new_cost))

        return None



# ---- Tests ----

if __name__ == "__main__":
    print("\n----- BEAM WIDTH TRADEOFF ------\n")

    g = Graph()
    g.add_edge('A', 'B', 1)
    g.add_edge('A', 'X', 2)
    g.add_edge('B', 'C', 9)
    g.add_edge('B', 'GOAL', 20)
    g.add_edge('X', 'Y', 1)
    g.add_edge('Y', 'GOAL', 1)

    print("k=1 (keeps only B, the locally cheaper first step):")
    print(" ", g.beam_search('A', 'GOAL', k=1))
    # the beam prunes toward the dead end and never recovers -- NOT COMPLETE.

    print("k=2 (keeps both B and X, so X survives to be explored):")
    print(" ", g.beam_search('A', 'GOAL', k=2))
    # X survives the first trim and reaches the true optimal path A-X-Y-GOAL, cost 4
