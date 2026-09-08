# -------------------------
# DEPTH FIRST SEARCH
# -------------------------

# DFS does not ensure shortest path.

# Variants:
# 1 - Recursive - Tree - dfs_recursive_tree
# 2 - Recursive - Graph - dfs_recursive_graph
# 3 - Recursive - Either - dfs_recursive_traversal - no goal
# 4 - Iterative - Tree - dfs_iterative_tree
# 5 - Iterative - Graph - dfs_iterative_graph
# 6 - Iterative - Either - dfs_iterative_traversal - no goal

from collections import defaultdict, deque

class Graph:
    def __init__(self):
        self.graph = defaultdict(list)

    def add_edge(self, u, v, undirected=False):
        self.graph[u].append(v)

        if undirected:
            self.graph[v].append(u)

    # -------- Recursive Tree ------
    # Tree only, no visited set
    # O(d): only current path lives on the call stack

    def dfs_recursive_tree(self, node, end):
        if node == end:
            return [node]

        for child in self.graph[node]:
            result = self.dfs_recursive_tree(child, end)
            if result:
                return [node] + result

        return None

    # -------- Recursive Graph ------
    # Graph with cycle handling
    # O(n): more than above because it maintains visited set

    def dfs_recursive_graph(self, start, end):
        visited = set()

        def dfs(node):
            if node == end:
                return [node]

            visited.add(node)

            for child in self.graph[node]:
                if child in visited:
                    continue # skip cycle

                result = dfs(child)
                if result:
                    return [node] + result

            return None

        return dfs(start)

    # -------- Recursive Traversal (Tree + Graph) ------
    # O(n)
    def dfs_recursive_traversal(self, start):
        visited = []
        seen = set()

        def dfs(node):
            if node in seen:
                return
            seen.add(node)
            visited.append(node)
            for child in self.graph[node]:
                dfs(child)

        dfs(start)
        return visited

    # -------- Iterative Tree ------
    # O(d)
    # Path stored per stack entry, no parent dict
    
    def dfs_iterative_tree(self, start, end):
        stack = deque([(start, [start])])

        while stack:
            node, path = stack.pop() # pops from the right = LIFO

            if node == end:
                return path

            for child in self.graph[node]:
                stack.append((child, path + [child]))
        
        return None

    # -------- Iterative Graph ------
    # Graph with cycle handling
    # O(n) because visited/parent grow with the graph
    # Path stored in parent dict, cheaper when visited set already in use

    def dfs_iterative_graph(self, start, end):
        visited = { start }
        stack = deque([start])
        parent = { start: None }

        while stack:
            node = stack.pop() # Right element

            if node == end:
                path, n = [], node
                while n is not None:
                    path.append(n)
                    n = parent[n]
                return path[::-1] # Reversed path

            for child in self.graph[node]:
                if child not in visited:
                    visited.add(child)
                    stack.append(child)
                    parent[child] = node
        
        return None

    # -------- Iterative Traversal (Tree + Graph) ------
    # O(n)

    def dfs_iterative_traversal(self, start):
        visited = []
        seen = { start }
        stack = deque([start])

        while stack:
            node = stack.pop()
            visited.append(node)

            for child in self.graph[node]:
                if child not in seen:
                    seen.add(child)
                    stack.append(child)

        return visited
        

# ---- Tests ----

if __name__ == "__main__":
    print("\n----- RECURSIVE ------\n")

    # tree: A -> B,C ; B -> D,E ; C -> F,G
    tree = Graph()
    tree.add_edge('A','B'); tree.add_edge('A','C')
    tree.add_edge('B','D'); tree.add_edge('B','E')
    tree.add_edge('C','F'); tree.add_edge('C','G')

    print("tree version:")
    print("  A -> F:", tree.dfs_recursive_tree('A', 'F'))
    print("  A -> A:", tree.dfs_recursive_tree('A', 'A'))
    print("  A -> Z:", tree.dfs_recursive_tree('A', 'Z'))

    # cyclic graph: A -- B -- C -- A ; C -- D
    cyc = Graph()
    cyc.add_edge('A','B', undirected=True)
    cyc.add_edge('B','C', undirected=True)
    cyc.add_edge('C','A', undirected=True)
    cyc.add_edge('C','D', undirected=True)

    print("\ngraph version (with cycles):")
    print("  A -> D:", cyc.dfs_recursive_graph('A', 'D'))
    print("  A -> Z:", cyc.dfs_recursive_graph('A', 'Z'))

    print("\n----- ITERATIVE ------\n")

    tree = Graph()
    tree.add_edge('A','B'); tree.add_edge('A','C')
    tree.add_edge('B','D'); tree.add_edge('B','E')
    tree.add_edge('C','F'); tree.add_edge('C','G')

    print("tree version:")
    print("  A -> F:", tree.dfs_iterative_tree('A', 'F'))
    print("  A -> A:", tree.dfs_iterative_tree('A', 'A'))
    print("  A -> Z:", tree.dfs_iterative_tree('A', 'Z'))

    cyc = Graph()
    cyc.add_edge('A','B', undirected=True)
    cyc.add_edge('B','C', undirected=True)
    cyc.add_edge('C','A', undirected=True)
    cyc.add_edge('C','D', undirected=True)

    print("\ngraph version (with cycles):")
    print("  A -> D:", cyc.dfs_iterative_graph('A', 'D'))
    print("  A -> Z:", cyc.dfs_iterative_graph('A', 'Z'))

    print("\n----- RECURSIVE TRAVERSAL ------\n")

    tree = Graph()
    tree.add_edge('A','B'); tree.add_edge('A','C')
    tree.add_edge('B','D'); tree.add_edge('B','E')
    tree.add_edge('C','F'); tree.add_edge('C','G')

    print("tree version:")
    print("traversal:", tree.dfs_recursive_traversal('A'))
