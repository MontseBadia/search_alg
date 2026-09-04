# -------------------------
# A* SEARCH
# -------------------------

# A* = dijkstra + heuristic that estimates remaining distance to goal.
# Heuristic directs the search toward the goal so it typically expands fewer
# nodes than dijkstra while returning same optimal path.
# h must never overestimate (admissibility requirement)

# Variants:
# 1- Targeted - dict + min - a_star_dict
# 2- Targeted - heap       - a_star_heap


from collections import defaultdict
import heapq


class Graph:
    def __init__(self):
        self.graph = defaultdict(dict)

    def add_edge(self, u, v, weight, undirected=False):
        self.graph[u][v] = weight
        if undirected:
            self.graph[v][u] = weight

    # -------- Targeted --------
    # O(V²) time, O(V) memory - check!

    def a_star_dict(self, start, end, heuristic):
        def h(n):
            return heuristic.get(n, 0)

        queue = {start: 0}          # node -> g(n), real cost from start
        distance = {start: 0}       # best-known g(n) per node
        parent = {start: None}

        while queue:
            # ONLY DIFFERENCE FROM DIJKSTRA: pick smallest f = g + h
            item = min(queue, key=lambda n: queue[n] + h(n))
            cost = queue.pop(item)   # cost is g(item)

            if item == end:
                path, node = [], item
                while node is not None:
                    path.append(node)
                    node = parent[node]
                return path[::-1], cost

            for child, weight in self.graph[item].items():
                new_cost = cost + weight        # accumulate g -- NOT g + h
                if child not in distance or new_cost < distance[child]:
                    queue[child] = new_cost
                    distance[child] = new_cost
                    parent[child] = item

        return None, float("inf")

    # -------- Targeted (heap) --------
    # O((V+E) log V) time, O(V) memory. Efficient for prod.

    def a_star_heap(self, start, end, heuristic):
        def h(n):
            return heuristic.get(n, 0)

        distance = {start: 0}       # g(n): real cost from start
        parent = {start: None}
        finalized = set()
        heap = [(h(start), start)]  # priority is f = g + h; g(start)=0

        while heap:
            _, item = heapq.heappop(heap)
            if item in finalized:
                continue
            finalized.add(item)

            if item == end:
                path, node = [], item
                while node is not None:
                    path.append(node)
                    node = parent[node]
                return path[::-1], distance[item]

            for child, weight in self.graph[item].items():
                new_cost = distance[item] + weight
                if child not in distance or new_cost < distance[child]:
                    distance[child] = new_cost
                    parent[child] = item
                    heapq.heappush(heap, (new_cost + h(child), child))

        return None, float("inf")


# ---- Tests ----

if __name__ == "__main__":
    print("\n----- TARGETED (dict + min) ------\n")

    # same graph as dijkstra.py: A->B(4), A->C(1), C->B(2), B->D(5), C->D(8), D->E(3)
    g = Graph()
    g.add_edge('A', 'B', 4)
    g.add_edge('A', 'C', 1)
    g.add_edge('C', 'B', 2)
    g.add_edge('B', 'D', 5)
    g.add_edge('C', 'D', 8)
    g.add_edge('D', 'E', 3)

    # admissible heuristic: never overestimates the true remaining cost to E
    # (true remaining costs are A=11, B=8, C=10, D=3, E=0 -- each h below is <= that)
    heuristic = {'A': 6, 'B': 5, 'C': 6, 'D': 2, 'E': 0}

    path, cost = g.a_star_dict('A', 'E', heuristic)
    print("A -> E:", path, "cost:", cost)
    # same optimal cost as dijkstra.py's dijkstra_targeted('A','E') -> 11

    print("\n----- TARGETED (heap) ------\n")

    path_heap, cost_heap = g.a_star_heap('A', 'E', heuristic)
    print("A -> E:", path_heap, "cost:", cost_heap)

    print("\n----- h=0 DEGENERATES TO DIJKSTRA ------\n")

    path_zero, cost_zero = g.a_star_dict('A', 'E', heuristic={})
    print("A -> E (h=0):", path_zero, "cost:", cost_zero)

    assert cost == cost_heap == cost_zero == 11
    print("\nall three agree on the optimal cost:", cost)
