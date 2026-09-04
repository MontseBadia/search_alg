# -------------------------
# DIJKSTRA'S ALGORITHM
# -------------------------

# Finds shortest path from start to goal (cheapest by total cost). Non negative weights.
# Same as BFS but using PRIORITY QUEUE instead of FIFO.
# Goal test on pop, not on discovery

# Variants:
# 1- Targeted            - dict + min - dijkstra_targeted
# 2- Single-source (all) - dict + min - dijkstra_all
# 3- Single-source (all) - heap       - dijkstra_heap


from collections import defaultdict
import heapq


class Graph:
    def __init__(self):
        # Weighted adjacency: node -> {neighbor: weight}
        self.graph = defaultdict(dict)

    def add_edge(self, u, v, weight, undirected=False):
        self.graph[u][v] = weight
        if undirected:
            self.graph[v][u] = weight

    # -------- Targeted (dict + min) --------
    # O(V²) time, O(V) memory. Returns shortest path start->end.
    # Simplest to read; use for small graphs or learning.

    def dijkstra_targeted(self, start, end):
        queue = {start: 0}          # frontier: node -> best-known cost
        distance = {start: 0}       # best-known cost per node (persistent)
        parent = {start: None}

        while queue:
            item = min(queue, key=queue.get)   # O(V) scan for cheapest
            cost = queue.pop(item)

            if item == end:
                path, node = [], item
                while node is not None:
                    path.append(node)
                    node = parent[node]
                return path[::-1], cost

            for child, weight in self.graph[item].items():
                new_cost = cost + weight
                if child not in distance or new_cost < distance[child]:
                    queue[child] = new_cost
                    distance[child] = new_cost
                    parent[child] = item

        return None, float("inf")   # unreachable

    # -------- Single-source, all nodes (dict + min) --------
    # O(V²) time, O(V) memory. Returns cost + parent for EVERY reachable node.
    # No `end` — runs to completion. Reconstruct any node's path via parents.

    def dijkstra_all(self, start):
        queue = {start: 0}
        distance = {start: 0}
        parent = {start: None}

        while queue:
            item = min(queue, key=queue.get)
            cost = queue.pop(item)

            for child, weight in self.graph[item].items():
                new_cost = cost + weight
                if child not in distance or new_cost < distance[child]:
                    queue[child] = new_cost
                    distance[child] = new_cost
                    parent[child] = item

        return distance, parent     # cost & parent for every reachable node

    # -------- Single-source, all nodes (heap) --------
    # O((V+E) log V) time, O(V) memory. Same result, much faster on large graphs.
    # Heap can hold stale entries; skip them with a `finalized` set.

    def dijkstra_heap(self, start):
        distance = {start: 0}
        parent = {start: None}
        finalized = set()
        heap = [(0, start)]

        while heap:
            cost, item = heapq.heappop(heap)
            if item in finalized:
                continue                    # stale entry, skip
            finalized.add(item)

            for child, weight in self.graph[item].items():
                new_cost = cost + weight
                if child not in distance or new_cost < distance[child]:
                    distance[child] = new_cost
                    parent[child] = item
                    heapq.heappush(heap, (new_cost, child))

        return distance, parent


# Helper for reconstructing a path from a parent map
def reconstruct_path(parent, target):
    if target not in parent:
        return None
    path, node = [], target
    while node is not None:
        path.append(node)
        node = parent[node]
    return path[::-1]


# ---- Tests ----

if __name__ == "__main__":
    print("\n----- TARGETED (dict + min) ------\n")

    # weighted graph where the shortest path isn't the obvious one:
    # A->B(4), A->C(1), C->B(2), B->D(5), C->D(8), D->E(3)
    g = Graph()
    g.add_edge('A', 'B', 4)
    g.add_edge('A', 'C', 1)
    g.add_edge('C', 'B', 2)
    g.add_edge('B', 'D', 5)
    g.add_edge('C', 'D', 8)
    g.add_edge('D', 'E', 3)

    path, cost = g.dijkstra_targeted('A', 'E')
    print("A -> E:", path, "cost:", cost)
    # A-C-B-D-E = 1+2+5+3 = 11, cheaper than the direct-looking A-B-D-E (4+5+3=12)
    # or A-C-D-E (1+8+3=12) -- Dijkstra explores by cost, not by hop count.

    print("\n----- ALL NODES (dict + min) ------\n")

    distances, parent = g.dijkstra_all('A')
    print("distances from A:", distances)
    print("path to E:", reconstruct_path(parent, 'E'))

    print("\n----- ALL NODES (heap) ------\n")

    distances_heap, parent_heap = g.dijkstra_heap('A')
    print("distances from A:", distances_heap)
    print("path to E:", reconstruct_path(parent_heap, 'E'))

    # all three variants should agree -- same algorithm, different bookkeeping
    assert distances['E'] == cost == distances_heap['E']
    print("\nall three variants agree on cost to E:", cost)
