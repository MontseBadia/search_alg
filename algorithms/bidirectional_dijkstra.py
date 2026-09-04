# -------------------------
# BIDIRECTIONAL DIJKSTRA
# -------------------------

# Runs two dijkstra simultaneously: one forward and one backward. When they meet
# in the middle, they combine their partial paths into full shortest path.
# On large graphs, it's faster and uses far less memory.
# Requires non-negative weights.


from collections import defaultdict


class Graph:
    def __init__(self):
        self.graph = defaultdict(dict)

    def add_edge(self, u, v, weight, undirected=False):
        self.graph[u][v] = weight
        if undirected:
            self.graph[v][u] = weight

    # -------- Bidirectional Dijkstra (directed + undirected) --------
    # check memory!

    def bidirectional_dijkstra(self, start, end):
        if start == end:
            return {"path": [start], "cost": 0, "meeting_node": start}

        # Backward search must follow edges in reverse: u -> v (w) becomes v -> u (w).
        reverse_graph = defaultdict(dict)
        for u in self.graph:
            for v, w in self.graph[u].items():
                reverse_graph[v][u] = w

        # Two mirror-image searches, each with its own frontier + bookkeeping.
        queue_f, queue_b = {start: 0}, {end: 0}
        distance_f, distance_b = {start: 0}, {end: 0}
        parent_f, parent_b = {start: None}, {end: None}

        best_cost = float("inf")
        best_meeting_node = None

        def expand(queue, distance, parent, graph, other_distance):
            nonlocal best_cost, best_meeting_node
            node = min(queue, key=queue.get)
            cost = queue.pop(node)

            for child, weight in graph[node].items():
                new_cost = cost + weight
                if child not in distance or new_cost < distance[child]:
                    distance[child] = new_cost
                    queue[child] = new_cost
                    parent[child] = node

                    # MEETING DETECTION: the other search has this node's cost.
                    # Their sum is a valid start->end path length via `child`.
                    if child in other_distance:
                        candidate = new_cost + other_distance[child]
                        if candidate < best_cost:
                            best_cost = candidate
                            best_meeting_node = child

        while queue_f and queue_b:
            expand(queue_f, distance_f, parent_f, self.graph, distance_b)
            expand(queue_b, distance_b, parent_b, reverse_graph, distance_f)

            # TERMINATION: stop when no undiscovered path can beat what we've found.
            if best_meeting_node is not None:
                if not queue_f or not queue_b:
                    break
                if min(queue_f.values()) + min(queue_b.values()) >= best_cost:
                    break

        if best_meeting_node is None:
            return None

        # Reconstruct: start -> meeting via forward parents
        path_f, node = [], best_meeting_node
        while node is not None:
            path_f.append(node)
            node = parent_f[node]
        path_f.reverse()

        # Reconstruct: meeting -> end via backward parents (skip meeting itself)
        path_b, node = [], parent_b[best_meeting_node]
        while node is not None:
            path_b.append(node)
            node = parent_b[node]

        return {
            "path": path_f + path_b,
            "cost": best_cost,
            "meeting_node": best_meeting_node,
        }


# ---- Tests ----

if __name__ == "__main__":
    print("\n----- BIDIRECTIONAL DIJKSTRA ------\n")

    # same graph as dijkstra.py, for a direct comparison:
    # A->B(4), A->C(1), C->B(2), B->D(5), C->D(8), D->E(3)
    g = Graph()
    g.add_edge('A', 'B', 4)
    g.add_edge('A', 'C', 1)
    g.add_edge('C', 'B', 2)
    g.add_edge('B', 'D', 5)
    g.add_edge('C', 'D', 8)
    g.add_edge('D', 'E', 3)

    result = g.bidirectional_dijkstra('A', 'E')
    print("A -> E:", result)
    # expect cost 11 -- same as dijkstra_targeted('A','E') in dijkstra.py
    assert result["cost"] == 11

    print("\n----- EDGE CASE: start == end ------\n")

    print("A -> A:", g.bidirectional_dijkstra('A', 'A'))

    print("\n----- UNREACHABLE ------\n")

    print("A -> Z (no edges to/from Z):", g.bidirectional_dijkstra('A', 'Z'))
