# -------------------------
# ITERATIVE DEEPENING SEARCH (IDS)
# -------------------------

# Runs depth-limited DFS repeatedly with growing depth limit. Benefits: 
# BFS optimality (shallowest goal) with DFS memory (O(d)).

# Variants:
# 1- Tree only - targeted - ids_tree
# 2- Graph     - targeted - ids_graph


from collections import defaultdict

class Graph:
    def __init__(self):
        self.graph = defaultdict(list)

    def add_edge(self, u, v, undirected=False):
        self.graph[u].append(v)
        if undirected:
            self.graph[v].append(u)

    # -------- Tree ------
    # O(d) memory (call stack only), O(b^d) time
    # No visited set - trees have no cycles

    def ids_tree(self, start, end, max_depth):
        def dls(node, limit):
            if node == end:
                return [node]
            if limit == 0:
                return None
            for child in self.graph[node]:
                result = dls(child, limit - 1)
                if result:
                    return [node] + result
            return None

        for limit in range(max_depth + 1):
            result = dls(start, limit)
            if result:
                return result
        return None

    # -------- Graph ------
    # O(d) memory (call stack + path-local visited set of size ≤ d)
    # Path-local visited: add on entry, remove on exit (choose/un-choose)

    def ids_graph(self, start, end, max_depth):
        def dls(node, limit, path):
            if node == end:
                return [node]
            if limit == 0:
                return None
            path.add(node)
            try:
                for child in self.graph[node]:
                    if child in path:
                        continue  # skip nodes on current path (cycle)
                    result = dls(child, limit - 1, path)
                    if result:
                        return [node] + result
                return None
            finally:
                path.remove(node)  # un-choose on every return path

        for limit in range(max_depth + 1):
            path = set()
            result = dls(start, limit, path)  # fresh set per pass
            if result:
                return result
        return None


# ---- Tests ----

if __name__ == "__main__":
    print("\n----- TREE ------\n")

    # same tree as DFS/BFS: A -> B,C ; B -> D,E ; C -> F,G
    tree = Graph()
    tree.add_edge('A','B'); tree.add_edge('A','C')
    tree.add_edge('B','D'); tree.add_edge('B','E')
    tree.add_edge('C','F'); tree.add_edge('C','G')

    print("tree version:")
    print("  A -> F, depth 5:", tree.ids_tree('A', 'F', max_depth=5))
    print("  A -> F, depth 1 (too shallow, F is 2 hops away):", tree.ids_tree('A', 'F', max_depth=1))
    print("  A -> Z:", tree.ids_tree('A', 'Z', max_depth=5))

    print("\n----- GRAPH (with cycles) ------\n")

    # same cyclic graph as DFS/BFS: A -- B -- C -- A ; C -- D
    cyc = Graph()
    cyc.add_edge('A','B', undirected=True)
    cyc.add_edge('B','C', undirected=True)
    cyc.add_edge('C','A', undirected=True)
    cyc.add_edge('C','D', undirected=True)

    print("graph version:")
    print("  A -> D, depth 5:", cyc.ids_graph('A', 'D', max_depth=5))
    print("  A -> D, depth 0 (too shallow, D is 2 hops away):", cyc.ids_graph('A', 'D', max_depth=0))
    print("  A -> Z:", cyc.ids_graph('A', 'Z', max_depth=5))
