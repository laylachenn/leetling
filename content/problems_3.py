"""Blind 75, part 3: Heap → Advanced Graphs (problems 39–48)."""
from common import E, P, rand_ints, rand_str

# ==================================================== Heap / Priority Queue


def _median_gen(r):
    cases = []
    for n in [3, 6, 12, 30, 200]:
        ops, args = ["MedianFinder"], [[]]
        for _ in range(n):
            if r.random() < 0.6 or ops[-1] == "MedianFinder":
                ops.append("addNum")
                args.append([r.randint(-10**5, 10**5)])
            else:
                ops.append("findMedian")
                args.append([])
        ops.append("findMedian")
        args.append([])
        cases.append([ops, args])
    return cases


P(id=39, slug="find-median-from-data-stream", title="Find Median from Data Stream", lc=295, difficulty="Hard",
  category="Heap / Priority Queue", params=["operations", "arguments"], compare="float",
  description="""The **median** is the middle value of a sorted list. If the list has an even length, it's the average of the two middle values (so the median of `[2, 3]` is `2.5`).

Implement `MedianFinder`:

- `MedianFinder()` creates the object.
- `addNum(num)` adds an integer from the stream.
- `findMedian()` returns the median of everything added so far (answers within `1e-5` are accepted).""",
  examples=[E(["MedianFinder", "addNum", "addNum", "findMedian", "addNum", "findMedian"],
              [[], [1], [2], [], [3], []], out=[None, None, None, 1.5, None, 2.0])],
  constraints=["-10^5 <= num <= 10^5", "findMedian is only called after at least one addNum.", "At most 5 * 10^4 calls."],
  starter='''class MedianFinder:
    def __init__(self):
        pass

    def addNum(self, num: int) -> None:
        pass

    def findMedian(self) -> float:
        pass
''',
  hints=["Keeping one sorted list makes `addNum` O(n). The median only depends on the middle — what if you split the numbers into a 'small half' and a 'large half'?",
         "Use two heaps: a **max-heap** for the smaller half and a **min-heap** for the larger half. Keep their sizes within 1 of each other. (Python's `heapq` is a min-heap — store negatives for the max-heap.)",
         "addNum: push `-num` onto `small`; then move the largest of `small` over to `large` (`heappush(large, -heappop(small))`); if `large` gets bigger than `small`, move its smallest back. findMedian: if `small` is bigger return `-small[0]`, else return `(-small[0] + large[0]) / 2`."],
  solution=r'''class MedianFinder:
    def __init__(self):
        self.small = []  # max-heap (negated values)
        self.large = []  # min-heap

    def addNum(self, num: int) -> None:
        heapq.heappush(self.small, -num)
        heapq.heappush(self.large, -heapq.heappop(self.small))
        if len(self.large) > len(self.small):
            heapq.heappush(self.small, -heapq.heappop(self.large))

    def findMedian(self) -> float:
        if len(self.small) > len(self.large):
            return float(-self.small[0])
        return (-self.small[0] + self.large[0]) / 2
''',
  complexity="addNum O(log n), findMedian O(1)",
  driver='''def drive(args):
    return run_design(MedianFinder, args[0], args[1])
''',
  gen=_median_gen)

# ============================================================ Backtracking


def _combo_gen(r):
    cases = [[[2], 2], [[1], 3], [[3, 5], 4], [[8, 7, 4, 3], 11]]
    for k, t in [(3, 10), (4, 15), (5, 20), (6, 25)]:
        cases.append([r.sample(range(2, 16), k), t])
    return cases


P(id=40, slug="combination-sum", title="Combination Sum", lc=39, difficulty="Medium", category="Backtracking",
  method="combinationSum", params=["candidates", "target"], compare="nested_unordered",
  description="""Given an array of **distinct** integers `candidates` and a `target`, return all **unique combinations** of candidates that add up to `target`. You may return them in any order.

The same number may be chosen **any number of times**. Two combinations are different if the count of at least one number differs.""",
  examples=[E([2, 3, 6, 7], 7, out=[[2, 2, 3], [7]], why="2 + 2 + 3 = 7 (2 used twice), and 7 = 7."),
            E([2, 3, 5], 8, out=[[2, 2, 2, 2], [2, 3, 3], [3, 5]]), E([2], 1, out=[])],
  constraints=["1 <= candidates.length <= 30", "2 <= candidates[i] <= 40", "All candidates are distinct.", "1 <= target <= 40"],
  starter='''class Solution:
    def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:
        pass
''',
  hints=["Think of building a combination one choice at a time, and 'undoing' choices to explore alternatives — that's backtracking.",
         "To avoid duplicates like [2,3] and [3,2], only ever pick candidates at the current index or later. At each step you can either reuse `candidates[i]` again, or move on to `i + 1`.",
         "`dfs(i, path, total)`: if `total == target`, record `path[:]`; if `i == len(candidates)` or `total > target`, return. Otherwise: append `candidates[i]`, recurse with the **same** `i`; pop it; then recurse with `i + 1`."],
  solution=r'''class Solution:
    def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:
        result, path = [], []

        def dfs(i, total):
            if total == target:
                result.append(path[:])
                return
            if i == len(candidates) or total > target:
                return
            path.append(candidates[i])
            dfs(i, total + candidates[i])
            path.pop()
            dfs(i + 1, total)

        dfs(0, 0)
        return result
''',
  complexity="Exponential — roughly O(2^(target/min))",
  gen=_combo_gen)


def _ws_gen(r):
    cases = [[[["a"]], "a"], [[["a", "b"]], "ba"], [[["a", "a"]], "aaa"], [[["C", "A", "A"], ["A", "A", "A"], ["B", "C", "D"]], "AAB"]]
    for rows, cols in [(2, 2), (3, 4), (4, 4), (5, 5), (6, 6)]:
        board = [[r.choice("ABCE") for _ in range(cols)] for _ in range(rows)]
        if r.random() < 0.6:
            i, j = r.randrange(rows), r.randrange(cols)
            seen, w = {(i, j)}, board[i][j]
            for _ in range(r.randint(1, 8)):
                nbrs = [(i + di, j + dj) for di, dj in ((0, 1), (1, 0), (0, -1), (-1, 0))
                        if 0 <= i + di < rows and 0 <= j + dj < cols and (i + di, j + dj) not in seen]
                if not nbrs:
                    break
                i, j = r.choice(nbrs)
                seen.add((i, j))
                w += board[i][j]
        else:
            w = rand_str(r, r.randint(3, 8), "ABCE")
        cases.append([board, w])
    return cases


_WS_BOARD = [["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]]

P(id=41, slug="word-search", title="Word Search", lc=79, difficulty="Medium", category="Backtracking",
  method="exist", params=["board", "word"],
  description="""Given an `m x n` grid of characters `board` and a string `word`, return `True` if `word` exists in the grid.

The word must be built from letters of sequentially **adjacent** cells (horizontally or vertically). The same cell can't be used more than once.""",
  examples=[E(_WS_BOARD, "ABCCED", out=True), E(_WS_BOARD, "SEE", out=True), E(_WS_BOARD, "ABCB", out=False, why="You'd need to reuse the B cell.")],
  constraints=["1 <= m, n <= 6", "1 <= word.length <= 15", "board and word contain only English letters."],
  starter='''class Solution:
    def exist(self, board: List[List[str]], word: str) -> bool:
        pass
''',
  hints=["Try starting from every cell. From a cell, the next letter of the word must be in one of its 4 neighbors.",
         "Use DFS with backtracking: mark a cell as 'in use' while exploring from it, and un-mark it when you return so other paths can use it.",
         "`dfs(r, c, i)`: if `i == len(word)` return `True`; if out of bounds, or `board[r][c] != word[i]`, return `False`. Temporarily set `board[r][c] = '#'`, try the 4 neighbors with `i + 1`, restore the letter, and return whether any worked."],
  solution=r'''class Solution:
    def exist(self, board: List[List[str]], word: str) -> bool:
        rows, cols = len(board), len(board[0])

        def dfs(r, c, i):
            if i == len(word):
                return True
            if not (0 <= r < rows and 0 <= c < cols) or board[r][c] != word[i]:
                return False
            board[r][c] = "#"
            found = dfs(r + 1, c, i + 1) or dfs(r - 1, c, i + 1) or dfs(r, c + 1, i + 1) or dfs(r, c - 1, i + 1)
            board[r][c] = word[i]
            return found

        return any(dfs(r, c, 0) for r in range(rows) for c in range(cols))
''',
  complexity="O(m · n · 4^L) time, O(L) space",
  gen=_ws_gen)

# ================================================================== Graphs


def _grid(r, rows, cols, p):
    return [["1" if r.random() < p else "0" for _ in range(cols)] for _ in range(rows)]


P(id=42, slug="number-of-islands", title="Number of Islands", lc=200, difficulty="Medium", category="Graphs",
  method="numIslands", params=["grid"],
  description="""Given an `m x n` grid where `"1"` is land and `"0"` is water, return the **number of islands**.

An island is a group of land cells connected horizontally or vertically, surrounded by water. Assume everything outside the grid is water.""",
  examples=[E([["1", "1", "1", "1", "0"], ["1", "1", "0", "1", "0"], ["1", "1", "0", "0", "0"], ["0", "0", "0", "0", "0"]], out=1),
            E([["1", "1", "0", "0", "0"], ["1", "1", "0", "0", "0"], ["0", "0", "1", "0", "0"], ["0", "0", "0", "1", "1"]], out=3)],
  constraints=["1 <= m, n <= 300", "grid[i][j] is '0' or '1'."],
  starter='''class Solution:
    def numIslands(self, grid: List[List[str]]) -> int:
        pass
''',
  hints=["Scan the grid. Whenever you find land you haven't explored yet, you've discovered a new island.",
         "When you discover an island, 'sink' (or mark as visited) every land cell connected to it with DFS or BFS, so you don't count it again.",
         "Loop over every cell; if it's `\"1\"`, increment the count and run `dfs(r, c)`, which sets the cell to `\"0\"` and recurses into its 4 neighbors that are in bounds and `\"1\"`."],
  solution=r'''class Solution:
    def numIslands(self, grid: List[List[str]]) -> int:
        rows, cols = len(grid), len(grid[0])
        count = 0
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == "1":
                    count += 1
                    stack = [(r, c)]
                    grid[r][c] = "0"
                    while stack:
                        i, j = stack.pop()
                        for ni, nj in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                            if 0 <= ni < rows and 0 <= nj < cols and grid[ni][nj] == "1":
                                grid[ni][nj] = "0"
                                stack.append((ni, nj))
        return count
''',
  complexity="O(m · n) time, O(m · n) worst-case space",
  gen=lambda r: [[[["0"]]], [[["1"]]], [[["1", "0", "1", "0", "1"]]]]
  + [[_grid(r, a, b, p)] for a, b, p in [(3, 3, 0.5), (5, 5, 0.4), (8, 10, 0.45), (20, 20, 0.5), (100, 100, 0.55)]])


def _clone_gen(r):
    cases = [[[[2], [1]]]]
    for n in [3, 4, 6, 10, 30]:
        edges = set()
        for v in range(2, n + 1):
            edges.add((r.randint(1, v - 1), v))
        for _ in range(n):
            a, b = r.sample(range(1, n + 1), 2)
            edges.add((min(a, b), max(a, b)))
        adj = [[] for _ in range(n)]
        for a, b in edges:
            adj[a - 1].append(b)
            adj[b - 1].append(a)
        cases.append([[sorted(x) for x in adj]])
    return cases


P(id=43, slug="clone-graph", title="Clone Graph", lc=133, difficulty="Medium", category="Graphs",
  method="cloneGraph", params=["adjList"],
  description="""You're given a reference to one node of a **connected, undirected graph**. Return a **deep copy** (clone) of the graph: brand new nodes with the same values and the same connections.

Each node has a `val` (an int) and `neighbors` (a list of nodes). In the tests, node values are `1..n` and the graph is written as an adjacency list: `adjList[i]` lists the neighbors of the node with value `i + 1`. You're given the node with value 1.

The runner also checks that you didn't hand back any of the original nodes.""",
  examples=[E([[2, 4], [1, 3], [2, 4], [1, 3]], out=[[2, 4], [1, 3], [2, 4], [1, 3]]),
            E([[]], out=[[]], why="A single node with no neighbors."), E([], out=[], why="An empty graph — the input node is None.")],
  constraints=["0 <= number of nodes <= 100", "1 <= Node.val <= 100, and values are unique.", "No repeated edges or self-loops; the graph is connected."],
  starter='''# Definition for a Node.
# class Node:
#     def __init__(self, val = 0, neighbors = None):
#         self.val = val
#         self.neighbors = neighbors if neighbors is not None else []

class Solution:
    def cloneGraph(self, node: Optional['Node']) -> Optional['Node']:
        pass
''',
  hints=["You need to visit every node (DFS or BFS) and create a copy of each one exactly once — even though the graph has cycles.",
         "Keep a dictionary `old_node → new_node`. Before cloning a node, check whether it's already in there.",
         "`def clone(n)`: if `n in copies` return `copies[n]`; make `copy = Node(n.val)`, store `copies[n] = copy` **before** recursing, then `copy.neighbors = [clone(nb) for nb in n.neighbors]` and return `copy`. Handle `node is None`."],
  solution=r'''class Solution:
    def cloneGraph(self, node: Optional['Node']) -> Optional['Node']:
        copies = {}

        def clone(n):
            if n in copies:
                return copies[n]
            copy = Node(n.val)
            copies[n] = copy
            copy.neighbors = [clone(nb) for nb in n.neighbors]
            return copy

        return clone(node) if node else None
''',
  complexity="O(V + E) time, O(V) space",
  driver='''def drive(args):
    node = build_graph(args[0])
    original_ids = {id(n) for n in collect_graph(node)}
    copy = Solution().cloneGraph(node)
    for n in collect_graph(copy):
        if id(n) in original_ids:
            raise AssertionError("cloneGraph returned an original node — it must be a brand-new deep copy")
    return graph_to_adj(copy)
''',
  gen=_clone_gen)


P(id=44, slug="pacific-atlantic-water-flow", title="Pacific Atlantic Water Flow", lc=417, difficulty="Medium", category="Graphs",
  method="pacificAtlantic", params=["heights"], compare="unordered",
  description="""An `m x n` island borders the **Pacific Ocean** on its top and left edges, and the **Atlantic Ocean** on its bottom and right edges. `heights[r][c]` is the height of each cell.

Rain water flows from a cell to a neighboring cell (up/down/left/right) if the neighbor's height is **less than or equal to** the current height. Water flows from edge cells straight into the adjacent ocean.

Return a list of all coordinates `[r, c]` from which rain water can reach **both** oceans, in any order.""",
  examples=[E([[1, 2, 2, 3, 5], [3, 2, 3, 4, 4], [2, 4, 5, 3, 1], [6, 7, 1, 4, 5], [5, 1, 1, 2, 4]],
              out=[[0, 4], [1, 3], [1, 4], [2, 2], [3, 0], [3, 1], [4, 0]]),
            E([[1]], out=[[0, 0]])],
  constraints=["1 <= m, n <= 200", "0 <= heights[r][c] <= 10^5"],
  starter='''class Solution:
    def pacificAtlantic(self, heights: List[List[int]]) -> List[List[int]]:
        pass
''',
  hints=["Checking every cell separately is slow. Flip the question around: start from the *oceans* and see which cells water could have come from.",
         "From the ocean edges, walk 'uphill' (to neighbors with height >= current). Do one search from all Pacific edge cells and another from all Atlantic edge cells.",
         "Make sets `pac` and `atl`. DFS from every top-row and left-column cell into `pac`, and from every bottom-row and right-column cell into `atl`, only stepping to neighbors with `heights[nr][nc] >= heights[r][c]`. Answer: cells in both sets."],
  solution=r'''class Solution:
    def pacificAtlantic(self, heights: List[List[int]]) -> List[List[int]]:
        rows, cols = len(heights), len(heights[0])

        def reach(starts):
            seen = set(starts)
            stack = list(starts)
            while stack:
                r, c = stack.pop()
                for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                    if (0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in seen
                            and heights[nr][nc] >= heights[r][c]):
                        seen.add((nr, nc))
                        stack.append((nr, nc))
            return seen

        pac = reach([(0, c) for c in range(cols)] + [(r, 0) for r in range(rows)])
        atl = reach([(rows - 1, c) for c in range(cols)] + [(r, cols - 1) for r in range(rows)])
        return [[r, c] for r, c in pac & atl]
''',
  complexity="O(m · n) time and space",
  gen=lambda r: [[[[1, 1], [1, 1], [1, 1]]], [[[3, 3, 3], [3, 1, 3], [0, 2, 4]]]]
  + [[[rand_ints(r, b, 0, 9) for _ in range(a)]] for a, b in [(2, 3), (4, 4), (6, 5), (10, 10), (60, 60)]])


def _course_gen(r):
    cases = [[1, []], [3, [[1, 0], [2, 1], [0, 2]]], [3, [[0, 1], [0, 2], [1, 2]]], [2, [[0, 0]]]]
    for n in [4, 6, 10, 30, 300]:
        order = list(range(n))
        r.shuffle(order)
        pos = {c: i for i, c in enumerate(order)}
        edges = set()
        for _ in range(n * 2):
            a, b = r.sample(range(n), 2)
            if pos[a] > pos[b]:
                edges.add((a, b))
        if r.random() < 0.5 and n > 2:
            a, b = r.sample(range(n), 2)
            edges.add((a, b) if pos[a] < pos[b] else (b, a))
        cases.append([n, [list(e) for e in edges]])
    return cases


P(id=45, slug="course-schedule", title="Course Schedule", lc=207, difficulty="Medium", category="Graphs",
  method="canFinish", params=["numCourses", "prerequisites"],
  description="""There are `numCourses` courses labeled `0` to `numCourses - 1`. `prerequisites[i] = [a, b]` means you must take course `b` **before** course `a`.

Return `True` if it's possible to finish every course, otherwise `False`.""",
  examples=[E(2, [[1, 0]], out=True, why="Take course 0, then course 1."),
            E(2, [[1, 0], [0, 1]], out=False, why="Each course needs the other first — a cycle!")],
  constraints=["1 <= numCourses <= 2000", "0 <= prerequisites.length <= 5000", "All pairs are unique."],
  starter='''class Solution:
    def canFinish(self, numCourses: int, prerequisites: List[List[int]]) -> bool:
        pass
''',
  hints=["Model courses as a directed graph (an edge from prerequisite → course). When is it *impossible* to finish?",
         "It's impossible exactly when the graph has a **cycle**. Detect one with DFS (track nodes on the current path) or with Kahn's topological sort.",
         "Kahn's algorithm: count each course's incoming edges (`indegree`). Put all courses with indegree 0 in a queue; pop one, count it as taken, and decrement the indegree of courses that depend on it, enqueuing any that reach 0. Return `taken == numCourses`."],
  solution=r'''class Solution:
    def canFinish(self, numCourses: int, prerequisites: List[List[int]]) -> bool:
        graph = defaultdict(list)
        indegree = [0] * numCourses
        for course, pre in prerequisites:
            graph[pre].append(course)
            indegree[course] += 1
        queue = deque(c for c in range(numCourses) if indegree[c] == 0)
        taken = 0
        while queue:
            c = queue.popleft()
            taken += 1
            for nxt in graph[c]:
                indegree[nxt] -= 1
                if indegree[nxt] == 0:
                    queue.append(nxt)
        return taken == numCourses
''',
  complexity="O(V + E) time and space",
  gen=_course_gen)


def _rand_edges(r, n, m):
    edges = set()
    while len(edges) < m:
        a, b = r.sample(range(n), 2)
        edges.add((min(a, b), max(a, b)))
    return [list(e) for e in edges]


P(id=46, slug="number-of-connected-components-in-an-undirected-graph", title="Number of Connected Components in an Undirected Graph",
  lc=323, difficulty="Medium", category="Graphs", method="countComponents", params=["n", "edges"],
  description="""You have a graph of `n` nodes labeled `0` to `n - 1`, and a list `edges` where `edges[i] = [a, b]` is an undirected edge between `a` and `b`.

Return the number of **connected components** in the graph.""",
  examples=[E(5, [[0, 1], [1, 2], [3, 4]], out=2), E(5, [[0, 1], [1, 2], [2, 3], [3, 4]], out=1)],
  constraints=["1 <= n <= 2000", "0 <= edges.length <= 5000", "No repeated edges or self-loops."],
  starter='''class Solution:
    def countComponents(self, n: int, edges: List[List[int]]) -> int:
        pass
''',
  hints=["Each component is a group of nodes you can reach from one another. You could DFS from every unvisited node and count how many times you start a new search.",
         "Union-Find (disjoint set) is also great: start with n separate groups, and every edge that joins two *different* groups reduces the count by one.",
         "`parent = list(range(n))`. `find(x)` follows parents to the root (with path compression). For each edge, if `find(a) != find(b)`, link one root to the other and do `n -= 1`. Return `n`."],
  solution=r'''class Solution:
    def countComponents(self, n: int, edges: List[List[int]]) -> int:
        parent = list(range(n))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        components = n
        for a, b in edges:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb
                components -= 1
        return components
''',
  complexity="O(E · α(n)) time, O(n) space",
  gen=lambda r: [[1, []], [3, []], [4, [[0, 1], [2, 3], [1, 2]]]]
  + [[n, _rand_edges(r, n, m)] for n, m in [(6, 3), (10, 6), (20, 15), (50, 30), (1000, 900)]])


def _tree_gen(r):
    cases = [[1, []], [2, [[1, 0]]], [2, []], [4, [[0, 1], [2, 3]]], [3, [[0, 1], [1, 2], [2, 0]]]]
    for n in [5, 8, 15, 40, 500]:
        edges = [[r.randrange(v), v] for v in range(1, n)]
        kind = r.random()
        if kind < 0.33:
            edges.pop(r.randrange(len(edges)))
            edges.append(r.sample(range(n), 2))
            if len({tuple(sorted(e)) for e in edges}) != len(edges):
                edges.pop()
        elif kind < 0.66:
            a, b = r.sample(range(n), 2)
            if [a, b] not in edges and [b, a] not in edges:
                edges.append([a, b])
        r.shuffle(edges)
        cases.append([n, edges])
    return cases


P(id=47, slug="graph-valid-tree", title="Graph Valid Tree", lc=261, difficulty="Medium", category="Graphs",
  method="validTree", params=["n", "edges"],
  description="""You have `n` nodes labeled `0` to `n - 1` and a list of undirected `edges`.

Return `True` if these edges form a **valid tree**: every node is connected, and there are no cycles.""",
  examples=[E(5, [[0, 1], [0, 2], [0, 3], [1, 4]], out=True), E(5, [[0, 1], [1, 2], [2, 3], [1, 3], [1, 4]], out=False, why="1 → 2 → 3 → 1 is a cycle.")],
  constraints=["1 <= n <= 2000", "0 <= edges.length <= 5000", "No self-loops or repeated edges."],
  starter='''class Solution:
    def validTree(self, n: int, edges: List[List[int]]) -> bool:
        pass
''',
  hints=["A tree with n nodes always has exactly n − 1 edges. Is that enough on its own?",
         "With exactly n − 1 edges, the graph is a tree if and only if it's connected (or, equivalently, has no cycle).",
         "Return `False` if `len(edges) != n - 1`. Otherwise, DFS/BFS from node 0 and check that you visit all n nodes — or use Union-Find and return `False` if any edge connects two nodes already in the same set."],
  solution=r'''class Solution:
    def validTree(self, n: int, edges: List[List[int]]) -> bool:
        if len(edges) != n - 1:
            return False
        graph = defaultdict(list)
        for a, b in edges:
            graph[a].append(b)
            graph[b].append(a)
        seen = {0}
        stack = [0]
        while stack:
            node = stack.pop()
            for nb in graph[node]:
                if nb not in seen:
                    seen.add(nb)
                    stack.append(nb)
        return len(seen) == n
''',
  complexity="O(V + E) time and space",
  gen=_tree_gen)

# ========================================================= Advanced Graphs


def _alien_gen(r):
    cases = [[["z", "z"]], [["ab", "adc"]], [["ac", "ab", "zc", "zb"]], [["aba"]], [["z", "x", "a", "zb", "zx"]]]
    for n, alpha in [(3, 4), (5, 5), (8, 6), (15, 8), (40, 12)]:
        letters = r.sample("abcdefghijklmnopqrstuvwxyz", alpha)
        rank = {c: i for i, c in enumerate(letters)}
        words = sorted({"".join(r.choice(letters) for _ in range(r.randint(1, 5))) for _ in range(n)},
                       key=lambda w: [rank[c] for c in w])
        if r.random() < 0.3 and len(words) > 2:
            i = r.randrange(len(words) - 1)
            words[i], words[i + 1] = words[i + 1], words[i]
        cases.append([words])
    return cases


P(id=48, slug="alien-dictionary", title="Alien Dictionary", lc=269, difficulty="Hard", category="Advanced Graphs",
  method="alienOrder", params=["words"], compare="alien",
  description="""An alien language uses lowercase English letters, but in an unknown **order**.

You're given a list of `words` from the alien dictionary, **sorted** by the rules of that language. Return a string of the language's unique letters in a valid order. If no order is consistent with the list, return `""`. If several orders work, return any of them.

Ordering rules: comparing two words, the first position where they differ decides the order. If there's no difference in the shorter length, the shorter word comes first — so `"abc"` before `"ab"` is invalid.""",
  examples=[E(["wrt", "wrf", "er", "ett", "rftt"], out="wertf"), E(["z", "x"], out="zx"),
            E(["z", "x", "z"], out="", why="z < x and x < z can't both be true."),
            E(["abc", "ab"], out="", why="A word can't come before its own prefix.")],
  constraints=["1 <= words.length <= 100", "1 <= words[i].length <= 100", "words[i] is lowercase English letters."],
  starter='''class Solution:
    def alienOrder(self, words: List[str]) -> str:
        pass
''',
  hints=["Comparing each pair of *adjacent* words gives you at most one fact: the first differing letters `a`, `b` mean `a` comes before `b`.",
         "Those facts form a directed graph of letters. A valid alphabet is a topological ordering of that graph; a cycle means there's no answer. Don't forget the prefix rule!",
         "Add every letter as a node. For each adjacent pair, find the first differing letters and add edge `a → b` (if `w1` is longer and `w2` is its prefix, return `\"\"`). Then run Kahn's algorithm; if you can't output every letter, return `\"\"`."],
  solution=r'''class Solution:
    def alienOrder(self, words: List[str]) -> str:
        graph = {c: set() for w in words for c in w}
        for w1, w2 in zip(words, words[1:]):
            for a, b in zip(w1, w2):
                if a != b:
                    graph[a].add(b)
                    break
            else:
                if len(w1) > len(w2):
                    return ""
        indegree = {c: 0 for c in graph}
        for c in graph:
            for nxt in graph[c]:
                indegree[nxt] += 1
        queue = deque(c for c in graph if indegree[c] == 0)
        order = []
        while queue:
            c = queue.popleft()
            order.append(c)
            for nxt in graph[c]:
                indegree[nxt] -= 1
                if indegree[nxt] == 0:
                    queue.append(nxt)
        return "".join(order) if len(order) == len(graph) else ""
''',
  complexity="O(total characters) time, O(1) space (≤ 26 letters)",
  gen=_alien_gen)
