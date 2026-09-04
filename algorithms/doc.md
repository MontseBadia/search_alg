## ALGORITHM DESIGN CHOICES

Search algorithms are templates, not fixed procedures. 

### Universal Axes

These are the design choices every algorithm has.

#### Implementation (recursive vs iterative)

Any algorithm using a stack or queue can be expressed either way. Recursive is elegant but has language-imposed depth limits; iterative is more verbose but unbounded and often more efficient.

#### Graph structure (tree vs general graph)

Whether cycles can occur. A tree lets you skip the visited bookkeeping; a graph requires it.

#### Goal mode (targeted vs full-traversal)

Stopping at a goal or exploring everywhere. It makes little sense for A* or greedy but still applicable: you could run Dijkstra without goal to compute shortest distances to all nodes.

#### Return type (path / order / distance map / structure)

You can return: node, a map with the distance to every node, a spanning tree, a boolean, etc.

#### Direction (forwdard vs reversed edges)

Follow edges outward or backward. Irrelevant on undirected ones.

#### Multi-source vs single-source

Start from one node, or many. Common for "distance from any wall to each cell". Common for "count the islands" problem.

#### Weighted vs unweighted

Whether edges carry cost. Unweighted graphs suit BFS; weighted ones require Dijkstra or A*. If weights can be negative, use Bellmand-Ford instead.

#### Directed vs undirected

How edges are stored. Undirected graphs need both directions in the adjacency list.

#### Cycle-prevention strategy (none / global visited / path-local visited)

Whether you track visits and how. The choice is algorithm specific:
- DFS/BFS/Dijkstra: global visited (never revisit)
- Iterative deepening: path-local (allows re-discovery across passes)
- Backtracking: path-local (allows revisiting)

#### Goal-test timing (on generation vs on pop)

Any algorithm that separates "discover a node" from "expand a node" has this choice. BFS can safely test on generation; Dijkstra and A* must test on pop, otherwise they return suboptimal paths.

#### Duplicate handling in the frontier

When you re-discover a node with a better cost, you can update the existing frontier entry, add a duplicate and skip stale ones on pop, or reject the new entry.

#### Path storage strategy (parent dict vs path-per-node vs recursion)

How to reconstruct the answer

#### Approximate vs optimal

Whether an algorithm guarantees the true best answer or a good-enough one. Optimal (BFS, Dijkstra, A*, IDS, backtracking); approximate by design (beam search, greedy). Trading optimality buys speed or bounded memory.

### Family Specific Axes

These apply only to certain algorithm families.

#### Order of processing (pre-order vs post-order vs both)

DFS specific. 

#### Priority function (f)

Best-first family specific. Defining axis of Dijkstra (f = g) / greedy (f = h) / A* (f = g + h).

#### Heuristic function (h)

A* and greedy specific. Requires domain knowledge.

#### Bidirectional strategy (single-source vs meet-in-middle)

Applies to any goal directed algorithm (BFS, Dijkstra, A*, etc)

#### Depth limit (bounded vs unbounded)

DFS family specific

#### Beam width (k)

Beam-search specific.

