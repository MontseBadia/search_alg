# -------------------------
# BREADTH FIRST SEARCH
# -------------------------

# BFS explores shallowest nodes first. Guarantees shortest path. Same as DFS but FIFO 
# instead of LIFO. Recursive is rare because call stack is not FIFO.

# Variants:
# 1- Tree only - targeted - bfs_iterative_tree
# 2- General graph - targeted - bfs_iterative_graph
# 3- Either - traversal - bfs_iterative_traversal
# 4- Either - distances - bfs_distances

# BFS becomes impractical on deep graphs.


from collections import defaultdict, deque

class Graph:
    def __init__(self):
        self.graph = defaultdict(list)

    def add_edge(self, u, v, undirected=False):
        self.graph[u].append(v)

        if undirected:
            self.graph[v].append(u)

    # -------- Iterative Tree ------
    # O(b^d) - must hold an entire layer of the tree
    # Actual memory is worse than O(b^d) alone. It's O(b^d × d) — 
    # each of the b^d entries carries a d-length path
    # Path stored per queue entry, no parent dict
    
    def bfs_iterative_tree(self, start, end):
        queue = deque([(start, [start])])

        while queue:
            node, path = queue.popleft() # pops from the left = FIFO

            if node == end:
                return path

            for child in self.graph[node]:
                queue.append((child, path + [child]))
        
        return None

    # -------- Iterative Graph ------
    # Graph with cycle handling
    # O(n) because visited/parent grow with the graph
    # Path stored in parent dict, cheaper when visited set already in use

    def bfs_iterative_graph(self, start, end):
        visited = { start }
        queue = deque([start])
        parent = { start: None }

        while queue:
            node = queue.popleft() # Left element

            if node == end:
                path, n = [], node
                while n is not None:
                    path.append(n)
                    n = parent[n]
                return path[::-1] # Reversed path

            for child in self.graph[node]:
                if child not in visited:
                    visited.add(child)
                    queue.append(child)
                    parent[child] = node
        
        return None

    # -------- Iterative Traversal (Tree + Graph) ------
    # O(n) - all actions inside loop are o(1) but we loop over n nodes
    # therefore we have o(n) and visited, seen and queue hold n nodes
    # Seen set is only present for O(1) membership check. If visited was
    # used, check would become O(n), turning whole traversal into O(n^2)

    def bfs_iterative_traversal(self, start):
        visited = []
        seen = { start }
        queue = deque([start])

        while queue:
            node = queue.popleft()
            visited.append(node)

            for child in self.graph[node]:
                if child not in seen:
                    seen.add(child)
                    queue.append(child)

        return visited

    # -------- Traversal Returning Distances ------
    # BFS specific

    def bfs_distances(self, start):
        distance = { start: 0 }
        queue = deque([start])

        while queue:
            node = queue.popleft()
            for child in self.graph[node]:
                if child not in distance:
                    distance[child] = distance[node] + 1
                    queue.append(child)

        return distance


# ---- Tests ----

if __name__ == "__main__":
    print("\n----- ITERATIVE TREE ------\n")

    # same tree as DFS: A -> B,C ; B -> D,E ; C -> F,G
    tree = Graph()
    tree.add_edge('A','B'); tree.add_edge('A','C')
    tree.add_edge('B','D'); tree.add_edge('B','E')
    tree.add_edge('C','F'); tree.add_edge('C','G')

    print("tree version:")
    print("  A -> F:", tree.bfs_iterative_tree('A', 'F'))
    print("  A -> A:", tree.bfs_iterative_tree('A', 'A'))
    print("  A -> Z:", tree.bfs_iterative_tree('A', 'Z'))

    print("\n----- ITERATIVE GRAPH ------\n")

    # same cyclic graph as DFS: A -- B -- C -- A ; C -- D
    cyc = Graph()
    cyc.add_edge('A','B', undirected=True)
    cyc.add_edge('B','C', undirected=True)
    cyc.add_edge('C','A', undirected=True)
    cyc.add_edge('C','D', undirected=True)

    print("graph version (with cycles):")
    print("  A -> D:", cyc.bfs_iterative_graph('A', 'D'))
    print("  A -> Z:", cyc.bfs_iterative_graph('A', 'Z'))

    print("\n----- TRAVERSAL + DISTANCES ------\n")

    print("traversal:", tree.bfs_iterative_traversal('A'))
    print("distances from A:", tree.bfs_distances('A'))

    # Same tree DFS used: DFS visits A,B,D,E,C,F,G (dives deep first); BFS visits
    # A,B,C,D,E,F,G (layer by layer). Same graph, opposite exploration order.
