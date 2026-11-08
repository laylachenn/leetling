"""Blind 75, part 2: Trees → Tries (problems 25–38)."""
from common import E, P, TREE_DEF, rand_bst, rand_ints, rand_str, rand_tree, runner

# =================================================================== Trees


def _trees(r, sizes, lo=-100, hi=100, distinct=False):
    return [[rand_tree(r, n, lo, hi, distinct)] for n in sizes]


P(id=25, slug="invert-binary-tree", title="Invert Binary Tree", lc=226, difficulty="Easy", category="Trees",
  method="invertTree", params=["root"],
  description="""Given the `root` of a binary tree, **invert** it (mirror it left-to-right) and return its root.

(Trees are written as level-order arrays, where `null` means a missing child — the runner builds real `TreeNode`s for you.)""",
  examples=[E([4, 2, 7, 1, 3, 6, 9], out=[4, 7, 2, 9, 6, 3, 1]), E([2, 1, 3], out=[2, 3, 1]), E([], out=[])],
  constraints=["0 <= number of nodes <= 100", "-100 <= Node.val <= 100"],
  starter=TREE_DEF + '''class Solution:
    def invertTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        pass
''',
  hints=["Mirroring a tree = swap the left and right child of *every* node.",
         "Recursion fits naturally: invert the left subtree, invert the right subtree, then swap them. What's the base case?",
         "`if not root: return None`. Then `root.left, root.right = self.invertTree(root.right), self.invertTree(root.left)` and return `root`."],
  solution=TREE_DEF + r'''class Solution:
    def invertTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        if not root:
            return None
        root.left, root.right = self.invertTree(root.right), self.invertTree(root.left)
        return root
''',
  complexity="O(n) time, O(h) space for recursion",
  driver='''def drive(args):
    return tree_to_arr(Solution().invertTree(build_tree(args[0])))
''',
  gen=lambda r: [[[1]], [[1, 2]], [[1, None, 2]]] + _trees(r, [4, 8, 15, 40, 100]))


P(id=26, slug="maximum-depth-of-binary-tree", title="Maximum Depth of Binary Tree", lc=104, difficulty="Easy", category="Trees",
  method="maxDepth", params=["root"],
  description="""Given the `root` of a binary tree, return its **maximum depth**: the number of nodes along the longest path from the root down to the farthest leaf.""",
  examples=[E([3, 9, 20, None, None, 15, 7], out=3), E([1, None, 2], out=2)],
  constraints=["0 <= number of nodes <= 10^4", "-100 <= Node.val <= 100"],
  starter=TREE_DEF + '''class Solution:
    def maxDepth(self, root: Optional[TreeNode]) -> int:
        pass
''',
  hints=["How does the depth of a tree relate to the depths of its two subtrees?",
         "depth(node) = 1 + the larger of depth(left) and depth(right). An empty tree has depth 0.",
         "`if not root: return 0` then `return 1 + max(self.maxDepth(root.left), self.maxDepth(root.right))`. (Or BFS level by level and count the levels.)"],
  solution=TREE_DEF + r'''class Solution:
    def maxDepth(self, root: Optional[TreeNode]) -> int:
        if not root:
            return 0
        return 1 + max(self.maxDepth(root.left), self.maxDepth(root.right))
''',
  complexity="O(n) time, O(h) space",
  driver='''def drive(args):
    return Solution().maxDepth(build_tree(args[0]))
''',
  gen=lambda r: [[[]], [[0]]] + _trees(r, [3, 7, 20, 60, 500]))


def _same_gen(r):
    cases = [[[], []], [[1], []], [[1], [1]], [[1, 2, 3], [1, 2, 4]]]
    for n in [3, 6, 12, 30, 80]:
        t = rand_tree(r, n, -5, 5)
        if r.random() < 0.5:
            cases.append([t, list(t)])
        else:
            u = list(t)
            i = r.randrange(len(u))
            u[i] = 99 if u[i] is not None else u[i]
            cases.append([t, u if u != t else rand_tree(r, n, -5, 5)])
    return cases


P(id=27, slug="same-tree", title="Same Tree", lc=100, difficulty="Easy", category="Trees",
  method="isSameTree", params=["p", "q"],
  description="""Given the roots of two binary trees `p` and `q`, return `True` if they are the **same**: identical shape, with equal values in matching nodes.""",
  examples=[E([1, 2, 3], [1, 2, 3], out=True), E([1, 2], [1, None, 2], out=False), E([1, 2, 1], [1, 1, 2], out=False)],
  constraints=["0 <= number of nodes in each tree <= 100", "-10^4 <= Node.val <= 10^4"],
  starter=TREE_DEF + '''class Solution:
    def isSameTree(self, p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:
        pass
''',
  hints=["Two trees are the same if their roots match *and* their left subtrees are the same *and* their right subtrees are the same.",
         "Handle the base cases first: both empty → same; exactly one empty → different; values differ → different.",
         "`if not p and not q: return True`; `if not p or not q or p.val != q.val: return False`; `return self.isSameTree(p.left, q.left) and self.isSameTree(p.right, q.right)`."],
  solution=TREE_DEF + r'''class Solution:
    def isSameTree(self, p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:
        if not p and not q:
            return True
        if not p or not q or p.val != q.val:
            return False
        return self.isSameTree(p.left, q.left) and self.isSameTree(p.right, q.right)
''',
  complexity="O(n) time, O(h) space",
  driver='''def drive(args):
    return Solution().isSameTree(build_tree(args[0]), build_tree(args[1]))
''',
  gen=_same_gen)


def _subtree_gen(r):
    cases = [[[1, 1], [1]], [[1], [1]], [[1, 2, 3], [2, 3]], [[3, 4, 5, 1, None, 2], [3, 1, 2]]]
    for n in [5, 10, 20, 50]:
        t = rand_tree(r, n, 0, 3)
        root = runner.build_tree(t)
        nodes = []
        stack = [root]
        while stack:
            x = stack.pop()
            if x:
                nodes.append(x)
                stack += [x.left, x.right]
        sub = runner.tree_to_arr(r.choice(nodes))
        if r.random() < 0.4:
            sub = sub + [r.randint(0, 3)]
        cases.append([t, sub])
    return cases


P(id=28, slug="subtree-of-another-tree", title="Subtree of Another Tree", lc=572, difficulty="Easy", category="Trees",
  method="isSubtree", params=["root", "subRoot"],
  description="""Given the roots of two binary trees `root` and `subRoot`, return `True` if `root` contains a subtree with exactly the same structure and values as `subRoot`.

A subtree of a node is that node plus **all** of its descendants. A tree also counts as a subtree of itself.""",
  examples=[E([3, 4, 5, 1, 2], [4, 1, 2], out=True),
            E([3, 4, 5, 1, 2, None, None, None, None, 0], [4, 1, 2], out=False,
              why="The node 4 in root has an extra descendant (0), so its subtree isn't identical.")],
  constraints=["1 <= nodes in root <= 2000", "1 <= nodes in subRoot <= 1000", "-10^4 <= Node.val <= 10^4"],
  starter=TREE_DEF + '''class Solution:
    def isSubtree(self, root: Optional[TreeNode], subRoot: Optional[TreeNode]) -> bool:
        pass
''',
  hints=["You've solved 'Same Tree' — reuse it! At which nodes should you check?",
         "Try every node in `root` as a potential match for `subRoot`.",
         "`if not root: return False`; `if same(root, subRoot): return True`; otherwise `return self.isSubtree(root.left, subRoot) or self.isSubtree(root.right, subRoot)`."],
  solution=TREE_DEF + r'''class Solution:
    def isSubtree(self, root: Optional[TreeNode], subRoot: Optional[TreeNode]) -> bool:
        def same(a, b):
            if not a and not b:
                return True
            if not a or not b or a.val != b.val:
                return False
            return same(a.left, b.left) and same(a.right, b.right)

        if not root:
            return False
        return same(root, subRoot) or self.isSubtree(root.left, subRoot) or self.isSubtree(root.right, subRoot)
''',
  complexity="O(m · n) time, O(h) space",
  driver='''def drive(args):
    return Solution().isSubtree(build_tree(args[0]), build_tree(args[1]))
''',
  gen=_subtree_gen)


def _lca_gen(r):
    cases = []
    for n in [2, 3, 6, 12, 30, 100]:
        arr, vals = rand_bst(r, n, 0, 10**4)
        p, q = r.sample(vals, 2)
        cases.append([arr, p, q])
    return cases


P(id=29, slug="lowest-common-ancestor-of-a-binary-search-tree", title="Lowest Common Ancestor of a BST", lc=235,
  difficulty="Medium", category="Trees", method="lowestCommonAncestor", params=["root", "p", "q"],
  description="""Given a **binary search tree** and two of its nodes `p` and `q`, return their **lowest common ancestor** (LCA): the deepest node that has both `p` and `q` as descendants. A node counts as a descendant of itself.

The examples show `p` and `q` by value; your function receives the actual `TreeNode`s and should return a `TreeNode`.""",
  examples=[E([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5], 2, 8, out=6),
            E([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5], 2, 4, out=2, why="2 is an ancestor of 4, and a node can be its own descendant."),
            E([2, 1], 2, 1, out=2)],
  constraints=["2 <= number of nodes <= 10^5", "All values are unique.", "p != q, and both exist in the BST."],
  starter=TREE_DEF + '''class Solution:
    def lowestCommonAncestor(self, root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:
        pass
''',
  hints=["Use the BST property: everything left of a node is smaller, everything right is larger.",
         "If both `p` and `q` are smaller than the current node, the LCA must be in the left subtree. Both larger → right subtree. Otherwise…?",
         "Start at `root`. While true: if `p.val` and `q.val` are both `< cur.val` go left; both `> cur.val` go right; otherwise they split here (or one *is* here), so return `cur`."],
  solution=TREE_DEF + r'''class Solution:
    def lowestCommonAncestor(self, root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:
        cur = root
        while cur:
            if p.val < cur.val and q.val < cur.val:
                cur = cur.left
            elif p.val > cur.val and q.val > cur.val:
                cur = cur.right
            else:
                return cur
''',
  complexity="O(h) time, O(1) space",
  driver='''def drive(args):
    root = build_tree(args[0])
    node = Solution().lowestCommonAncestor(root, find_node(root, args[1]), find_node(root, args[2]))
    return node.val if node is not None else None
''',
  gen=_lca_gen)


P(id=30, slug="binary-tree-level-order-traversal", title="Binary Tree Level Order Traversal", lc=102, difficulty="Medium",
  category="Trees", method="levelOrder", params=["root"],
  description="""Given the `root` of a binary tree, return the **level order traversal** of its values: a list of levels, top to bottom, with each level's values from left to right.""",
  examples=[E([3, 9, 20, None, None, 15, 7], out=[[3], [9, 20], [15, 7]]), E([1], out=[[1]]), E([], out=[])],
  constraints=["0 <= number of nodes <= 2000", "-1000 <= Node.val <= 1000"],
  starter=TREE_DEF + '''class Solution:
    def levelOrder(self, root: Optional[TreeNode]) -> List[List[int]]:
        pass
''',
  hints=["Visiting nodes level by level is exactly what breadth-first search (BFS) does.",
         "Use a queue (`collections.deque`). The trick to grouping by level: at the start of each round, the queue holds exactly one full level.",
         "While the queue isn't empty: `level = []`; repeat `len(queue)` times: pop a node, add its value to `level`, push its non-null children. Append `level` to the result."],
  solution=TREE_DEF + r'''class Solution:
    def levelOrder(self, root: Optional[TreeNode]) -> List[List[int]]:
        result = []
        queue = deque([root] if root else [])
        while queue:
            level = []
            for _ in range(len(queue)):
                node = queue.popleft()
                level.append(node.val)
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
            result.append(level)
        return result
''',
  complexity="O(n) time, O(n) space",
  driver='''def drive(args):
    return Solution().levelOrder(build_tree(args[0]))
''',
  gen=lambda r: [[[1, 2]], [[1, None, 2, None, 3]]] + _trees(r, [4, 9, 20, 60, 300], -1000, 1000))


def _valid_bst_gen(r):
    cases = [[[1]], [[2, 2, 2]], [[1, None, 1]], [[3, 1, 5, 0, 2, 4, 6]], [[3, 1, 5, 0, 4]], [[32, 26, 47, 19, None, None, 56, None, 27]]]
    for n in [5, 10, 25, 80]:
        arr, _ = rand_bst(r, n, -1000, 1000)
        if r.random() < 0.5:
            i = r.choice([i for i, v in enumerate(arr) if v is not None])
            arr[i] = arr[i] + r.choice([-300, 300])
        cases.append([arr])
    return cases


P(id=31, slug="validate-binary-search-tree", title="Validate Binary Search Tree", lc=98, difficulty="Medium",
  category="Trees", method="isValidBST", params=["root"],
  description="""Given the `root` of a binary tree, decide whether it's a **valid binary search tree**:

- Every node in a node's **left** subtree has a value strictly **less** than the node's value.
- Every node in a node's **right** subtree has a value strictly **greater** than the node's value.
- Both subtrees are themselves valid BSTs.""",
  examples=[E([2, 1, 3], out=True),
            E([5, 1, 4, None, None, 3, 6], out=False, why="The root is 5, but its right child is 4."),
            E([5, 4, 6, None, None, 3, 7], out=False, why="3 is in 5's right subtree, but 3 < 5 — checking only parent/child isn't enough!")],
  constraints=["1 <= number of nodes <= 10^4", "-2^31 <= Node.val <= 2^31 - 1"],
  starter=TREE_DEF + '''class Solution:
    def isValidBST(self, root: Optional[TreeNode]) -> bool:
        pass
''',
  hints=["Comparing each node only with its direct children isn't enough — look at example 3. Every node must fit within bounds set by *all* of its ancestors.",
         "Pass down a valid range `(low, high)`. Going left, the upper bound becomes the current value; going right, the lower bound becomes the current value.",
         "`def ok(node, low, high)`: empty → `True`; if not `low < node.val < high` → `False`; return `ok(node.left, low, node.val) and ok(node.right, node.val, high)`. Start with `ok(root, -inf, inf)`. (Alternative: an in-order traversal must be strictly increasing.)"],
  solution=TREE_DEF + r'''class Solution:
    def isValidBST(self, root: Optional[TreeNode]) -> bool:
        def ok(node, low, high):
            if not node:
                return True
            if not (low < node.val < high):
                return False
            return ok(node.left, low, node.val) and ok(node.right, node.val, high)

        return ok(root, float("-inf"), float("inf"))
''',
  complexity="O(n) time, O(h) space",
  driver='''def drive(args):
    return Solution().isValidBST(build_tree(args[0]))
''',
  gen=_valid_bst_gen)


def _kth_gen(r):
    cases = []
    for n in [1, 2, 5, 10, 30, 200]:
        arr, vals = rand_bst(r, n, 0, 10**4)
        cases.append([arr, r.randint(1, n)])
    return cases


P(id=32, slug="kth-smallest-element-in-a-bst", title="Kth Smallest Element in a BST", lc=230, difficulty="Medium",
  category="Trees", method="kthSmallest", params=["root", "k"],
  description="""Given the `root` of a binary search tree and an integer `k`, return the **k-th smallest** value (1-indexed) among all the nodes.""",
  examples=[E([3, 1, 4, None, 2], 1, out=1), E([5, 3, 6, 2, 4, None, None, 1], 3, out=3)],
  constraints=["1 <= k <= n <= 10^4", "0 <= Node.val <= 10^4"],
  starter=TREE_DEF + '''class Solution:
    def kthSmallest(self, root: Optional[TreeNode], k: int) -> int:
        pass
''',
  hints=["Which traversal order visits a BST's values in sorted order?",
         "In-order traversal (left, node, right) produces ascending values. You can stop as soon as you've visited k nodes.",
         "Iterative in-order with a stack: go left as far as possible pushing nodes; pop one, decrement `k` — if it hits 0 return that value; then move to its right child and repeat."],
  solution=TREE_DEF + r'''class Solution:
    def kthSmallest(self, root: Optional[TreeNode], k: int) -> int:
        stack, cur = [], root
        while stack or cur:
            while cur:
                stack.append(cur)
                cur = cur.left
            cur = stack.pop()
            k -= 1
            if k == 0:
                return cur.val
            cur = cur.right
''',
  complexity="O(h + k) time, O(h) space",
  driver='''def drive(args):
    return Solution().kthSmallest(build_tree(args[0]), args[1])
''',
  gen=_kth_gen)


def _build_gen(r):
    cases = []
    for n in [1, 2, 3, 6, 12, 40, 300]:
        root = runner.build_tree(rand_tree(r, n, -3000, 3000, distinct=True))
        pre, ino = [], []

        def walk(node):
            if node:
                pre.append(node.val)
                walk(node.left)
                ino.append(node.val)
                walk(node.right)

        walk(root)
        cases.append([pre, ino])
    return cases


P(id=33, slug="construct-binary-tree-from-preorder-and-inorder-traversal", title="Construct Binary Tree from Preorder and Inorder Traversal",
  lc=105, difficulty="Medium", category="Trees", method="buildTree", params=["preorder", "inorder"],
  description="""Given two integer arrays `preorder` and `inorder` — the preorder and inorder traversals of the same binary tree with **unique** values — rebuild the tree and return its root.""",
  examples=[E([3, 9, 20, 15, 7], [9, 3, 15, 20, 7], out=[3, 9, 20, None, None, 15, 7]), E([-1], [-1], out=[-1])],
  constraints=["1 <= preorder.length <= 3000", "inorder.length == preorder.length", "All values are unique."],
  starter=TREE_DEF + '''class Solution:
    def buildTree(self, preorder: List[int], inorder: List[int]) -> Optional[TreeNode]:
        pass
''',
  hints=["The first value in `preorder` is always the root. Where does that root sit in `inorder`, and what does that tell you?",
         "Everything left of the root in `inorder` belongs to the left subtree; everything right belongs to the right subtree. The *size* of the left part tells you how to split `preorder` too.",
         "Store `index = {v: i for i, v in enumerate(inorder)}`. Recurse on inorder ranges `(lo, hi)` while consuming preorder values left to right with a shared pointer: make the node, build its left from `(lo, mid-1)`, then right from `(mid+1, hi)`."],
  solution=TREE_DEF + r'''class Solution:
    def buildTree(self, preorder: List[int], inorder: List[int]) -> Optional[TreeNode]:
        index = {v: i for i, v in enumerate(inorder)}
        pos = 0

        def build(lo, hi):
            nonlocal pos
            if lo > hi:
                return None
            val = preorder[pos]
            pos += 1
            node = TreeNode(val)
            mid = index[val]
            node.left = build(lo, mid - 1)
            node.right = build(mid + 1, hi)
            return node

        return build(0, len(inorder) - 1)
''',
  complexity="O(n) time, O(n) space",
  driver='''def drive(args):
    return tree_to_arr(Solution().buildTree(args[0], args[1]))
''',
  gen=_build_gen)


P(id=34, slug="binary-tree-maximum-path-sum", title="Binary Tree Maximum Path Sum", lc=124, difficulty="Hard", category="Trees",
  method="maxPathSum", params=["root"],
  description="""A **path** in a binary tree is a sequence of nodes where each adjacent pair is connected by an edge. A node can appear at most once, and the path doesn't have to pass through the root. A path's **sum** is the sum of its node values.

Given the `root` of a non-empty binary tree, return the maximum path sum of any non-empty path.""",
  examples=[E([1, 2, 3], out=6, why="The path 2 → 1 → 3 sums to 6."),
            E([-10, 9, 20, None, None, 15, 7], out=42, why="The path 15 → 20 → 7 sums to 42."),
            E([-3], out=-3)],
  constraints=["1 <= number of nodes <= 3 * 10^4", "-1000 <= Node.val <= 1000"],
  starter=TREE_DEF + '''class Solution:
    def maxPathSum(self, root: Optional[TreeNode]) -> int:
        pass
''',
  hints=["Every path has one 'highest' node where it bends (or ends). At that node, the path is: best downward chain on the left + node + best downward chain on the right.",
         "Write a DFS that returns the best *downward* chain sum starting at a node (it can only continue into ONE child). While you're there, update a global answer with the 'bent' path through that node.",
         "In `dfs(node)`: `left = max(dfs(node.left), 0)`, `right = max(dfs(node.right), 0)` (drop negative branches). Update `best = max(best, node.val + left + right)`. Return `node.val + max(left, right)`."],
  solution=TREE_DEF + r'''class Solution:
    def maxPathSum(self, root: Optional[TreeNode]) -> int:
        best = root.val

        def dfs(node):
            nonlocal best
            if not node:
                return 0
            left = max(dfs(node.left), 0)
            right = max(dfs(node.right), 0)
            best = max(best, node.val + left + right)
            return node.val + max(left, right)

        dfs(root)
        return best
''',
  complexity="O(n) time, O(h) space",
  driver='''def drive(args):
    return Solution().maxPathSum(build_tree(args[0]))
''',
  gen=lambda r: [[[2, -1]], [[-2, -1]], [[1, -2, 3]], [[5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1]]]
  + _trees(r, [3, 7, 15, 40, 200, 2000], -1000, 1000))


P(id=35, slug="serialize-and-deserialize-binary-tree", title="Serialize and Deserialize Binary Tree", lc=297, difficulty="Hard",
  category="Trees", params=["root"],
  description="""**Serialization** turns a data structure into a string so it can be saved or sent somewhere, then rebuilt later.

Design a `Codec` with `serialize(root) -> str` and `deserialize(data) -> TreeNode` for binary trees. Any format is fine, as long as a tree can be serialized to a string and that string turned back into the **exact** original tree.

The runner does: `Codec().deserialize(Codec().serialize(root))` and compares the result to the original.""",
  examples=[E([1, 2, 3, None, None, 4, 5], out=[1, 2, 3, None, None, 4, 5]), E([], out=[])],
  constraints=["0 <= number of nodes <= 10^4", "-1000 <= Node.val <= 1000"],
  starter=TREE_DEF + '''class Codec:
    def serialize(self, root: Optional[TreeNode]) -> str:
        """Encodes a tree to a single string."""
        pass

    def deserialize(self, data: str) -> Optional[TreeNode]:
        """Decodes your encoded data to a tree."""
        pass
''',
  hints=["A preorder traversal alone loses information about shape. What if you also wrote down a marker every time you hit a missing child?",
         "Preorder with null markers, e.g. `\"1,2,N,N,3,4,N,N,5,N,N\"`, describes a tree uniquely.",
         "serialize: DFS — append `'N'` for `None`, else append `str(node.val)` then recurse left and right; join with commas. deserialize: split on commas and consume tokens with a pointer, recursively: `'N'` → `None`; otherwise make the node, then build its left and right."],
  solution=TREE_DEF + r'''class Codec:
    def serialize(self, root: Optional[TreeNode]) -> str:
        out = []

        def dfs(node):
            if not node:
                out.append("N")
                return
            out.append(str(node.val))
            dfs(node.left)
            dfs(node.right)

        dfs(root)
        return ",".join(out)

    def deserialize(self, data: str) -> Optional[TreeNode]:
        tokens = iter(data.split(","))

        def build():
            tok = next(tokens)
            if tok == "N":
                return None
            node = TreeNode(int(tok))
            node.left = build()
            node.right = build()
            return node

        return build()
''',
  complexity="O(n) time and space for both",
  driver='''def drive(args):
    data = Codec().serialize(build_tree(args[0]))
    if not isinstance(data, str):
        raise TypeError(f"serialize() should return a str, but returned {type(data).__name__}")
    return tree_to_arr(Codec().deserialize(data))
''',
  gen=lambda r: [[[1]], [[1, None, 2, None, 3]], [[-1000, 1000]]] + _trees(r, [5, 12, 40, 300], -1000, 1000))

# =================================================================== Tries


def _trie_gen(r):
    cases = []
    for n in [5, 10, 20, 40, 150]:
        ops, args, words = ["Trie"], [[]], []
        for _ in range(n):
            kind = r.choice(["insert", "insert", "search", "startsWith"])
            if kind == "insert":
                w = rand_str(r, r.randint(1, 6), "abc")
                words.append(w)
            else:
                w = r.choice(words) if words and r.random() < 0.5 else rand_str(r, r.randint(1, 5), "abc")
                if kind == "startsWith" and r.random() < 0.5 and len(w) > 1:
                    w = w[: r.randint(1, len(w) - 1)]
            ops.append(kind)
            args.append([w])
        cases.append([ops, args])
    return cases


P(id=36, slug="implement-trie-prefix-tree", title="Implement Trie (Prefix Tree)", lc=208, difficulty="Medium", category="Tries",
  params=["operations", "arguments"],
  description="""A **trie** (say "try") is a tree for storing strings that makes prefix lookups fast — handy for autocomplete and spellcheckers.

Implement the `Trie` class:

- `Trie()` creates an empty trie.
- `insert(word)` adds `word` to the trie.
- `search(word)` returns `True` if `word` was inserted before.
- `startsWith(prefix)` returns `True` if some inserted word starts with `prefix`.

The tests list method calls and their arguments; the expected output lists each call's return value (`null` for none).""",
  examples=[E(["Trie", "insert", "search", "search", "startsWith", "insert", "search"],
              [[], ["apple"], ["apple"], ["app"], ["app"], ["app"], ["app"]],
              out=[None, None, True, False, True, None, True])],
  constraints=["1 <= word.length, prefix.length <= 2000", "Only lowercase English letters.", "At most 3 * 10^4 calls in total."],
  starter='''class Trie:
    def __init__(self):
        pass

    def insert(self, word: str) -> None:
        pass

    def search(self, word: str) -> bool:
        pass

    def startsWith(self, prefix: str) -> bool:
        pass
''',
  hints=["Each trie node represents a prefix. It needs links to its children (one per next letter) and a flag saying 'a word ends here'.",
         "A node can be a tiny class with `children = {}` (letter → node) and `end = False`. Insert and search both walk letter by letter from the root.",
         "insert: walk/create child nodes for each letter, then set `end = True` on the last one. search: walk; if a letter is missing return `False`; at the end return `node.end`. startsWith: same walk, but return `True` at the end."],
  solution=r'''class TrieNode:
    def __init__(self):
        self.children = {}
        self.end = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.end = True

    def _walk(self, s):
        node = self.root
        for ch in s:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def search(self, word: str) -> bool:
        node = self._walk(word)
        return node is not None and node.end

    def startsWith(self, prefix: str) -> bool:
        return self._walk(prefix) is not None
''',
  complexity="O(length) per operation, O(total characters) space",
  driver='''def drive(args):
    return run_design(Trie, args[0], args[1])
''',
  gen=_trie_gen)


def _wd_gen(r):
    cases = []
    for n in [6, 12, 25, 60, 200]:
        ops, args, words = ["WordDictionary"], [[]], []
        for _ in range(n):
            if r.random() < 0.45 or not words:
                w = rand_str(r, r.randint(1, 5), "abcd")
                words.append(w)
                ops.append("addWord")
            else:
                w = r.choice(words) if r.random() < 0.6 else rand_str(r, r.randint(1, 5), "abcd")
                w = "".join("." if r.random() < 0.3 else c for c in w)
                ops.append("search")
            args.append([w])
        cases.append([ops, args])
    return cases


P(id=37, slug="design-add-and-search-words-data-structure", title="Design Add and Search Words Data Structure", lc=211,
  difficulty="Medium", category="Tries", params=["operations", "arguments"],
  description="""Design a data structure that stores words and can check whether a pattern matches any stored word.

Implement `WordDictionary`:

- `WordDictionary()` creates the empty structure.
- `addWord(word)` stores `word`.
- `search(word)` returns `True` if any stored word matches `word`. The pattern may contain dots `.` — a dot matches **any single letter**.""",
  examples=[E(["WordDictionary", "addWord", "addWord", "addWord", "search", "search", "search", "search"],
              [[], ["bad"], ["dad"], ["mad"], ["pad"], ["bad"], [".ad"], ["b.."]],
              out=[None, None, None, None, False, True, True, True])],
  constraints=["1 <= word.length <= 25", "addWord words are lowercase letters; search words are lowercase letters or '.'",
               "At most 2 dots per search query.", "At most 10^4 calls."],
  starter='''class WordDictionary:
    def __init__(self):
        pass

    def addWord(self, word: str) -> None:
        pass

    def search(self, word: str) -> bool:
        pass
''',
  hints=["Store the words in a trie. Plain letters walk the trie exactly like 'Implement Trie'.",
         "A `.` could be *any* child, so you have to try every child at that position. That's a DFS/backtracking search.",
         "`dfs(i, node)`: if `i == len(word)` return `node.end`. If `word[i] == '.'`, return `True` if `dfs(i+1, child)` works for any child. Otherwise follow `node.children.get(word[i])` (return `False` if missing)."],
  solution=r'''class WordDictionary:
    def __init__(self):
        self.root = {}

    def addWord(self, word: str) -> None:
        node = self.root
        for ch in word:
            node = node.setdefault(ch, {})
        node["$"] = True

    def search(self, word: str) -> bool:
        def dfs(i, node):
            if i == len(word):
                return "$" in node
            ch = word[i]
            if ch == ".":
                return any(dfs(i + 1, child) for key, child in node.items() if key != "$")
            return ch in node and dfs(i + 1, node[ch])

        return dfs(0, self.root)
''',
  complexity="addWord O(L); search O(L) without dots, up to O(26^dots · L) with them",
  driver='''def drive(args):
    return run_design(WordDictionary, args[0], args[1])
''',
  gen=_wd_gen)


def _ws2_gen(r):
    cases = [[[["a"]], ["a"]], [[["a", "a"]], ["aaa"]], [[["a", "b"], ["c", "d"]], ["ab", "cb", "ad", "bd", "ac", "ca", "da", "bc", "db", "adcb", "dabc", "abb", "acb"]]]
    for rows, cols, nw in [(2, 3, 5), (3, 3, 8), (4, 4, 12), (5, 6, 20), (8, 8, 60)]:
        board = [[r.choice("abcde") for _ in range(cols)] for _ in range(rows)]
        words = set()
        for _ in range(nw):
            if r.random() < 0.6:
                i, j = r.randrange(rows), r.randrange(cols)
                seen, w = {(i, j)}, board[i][j]
                for _ in range(r.randint(0, 6)):
                    nbrs = [(i + di, j + dj) for di, dj in ((0, 1), (1, 0), (0, -1), (-1, 0))
                            if 0 <= i + di < rows and 0 <= j + dj < cols and (i + di, j + dj) not in seen]
                    if not nbrs:
                        break
                    i, j = r.choice(nbrs)
                    seen.add((i, j))
                    w += board[i][j]
                words.add(w)
            else:
                words.add(rand_str(r, r.randint(1, 6), "abcde"))
        cases.append([board, sorted(words)])
    return cases


P(id=38, slug="word-search-ii", title="Word Search II", lc=212, difficulty="Hard", category="Tries",
  method="findWords", params=["board", "words"], compare="unordered",
  description="""Given an `m x n` grid of letters `board` and a list of strings `words`, return **all words that appear on the board**, in any order.

A word is formed from letters of sequentially adjacent cells (up, down, left, right). The same cell can't be used more than once within a single word.""",
  examples=[E([["o", "a", "a", "n"], ["e", "t", "a", "e"], ["i", "h", "k", "r"], ["i", "f", "l", "v"]],
              ["oath", "pea", "eat", "rain"], out=["eat", "oath"]),
            E([["a", "b"], ["c", "d"]], ["abcb"], out=[])],
  constraints=["1 <= m, n <= 12", "board[i][j] is a lowercase English letter.", "1 <= words.length <= 3 * 10^4",
               "1 <= words[i].length <= 10", "All words are unique."],
  starter='''class Solution:
    def findWords(self, board: List[List[str]], words: List[str]) -> List[str]:
        pass
''',
  hints=["Running a separate 'Word Search' for every word repeats a lot of work. What if you searched for *all* words at once?",
         "Put every word into a trie. Then DFS from each cell, walking the trie alongside the board — stop as soon as the current path isn't a prefix of any word.",
         "Trie nodes store `word` at their end. `dfs(r, c, node)`: if `board[r][c]` isn't a child of `node`, stop. Move to that child; if it has a `word`, add it to results (and clear it to avoid duplicates). Mark the cell as visited (e.g. set it to `'#'`), recurse into 4 neighbors, then restore it."],
  solution=r'''class Solution:
    def findWords(self, board: List[List[str]], words: List[str]) -> List[str]:
        root = {}
        for w in words:
            node = root
            for ch in w:
                node = node.setdefault(ch, {})
            node["$"] = w
        rows, cols = len(board), len(board[0])
        found = []

        def dfs(r, c, parent):
            ch = board[r][c]
            node = parent.get(ch)
            if node is None:
                return
            if "$" in node:
                found.append(node.pop("$"))
            board[r][c] = "#"
            for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != "#":
                    dfs(nr, nc, node)
            board[r][c] = ch
            if not node:
                parent.pop(ch)

        for r in range(rows):
            for c in range(cols):
                dfs(r, c, root)
        return found
''',
  complexity="O(m · n · 4 · 3^(L-1)) worst case, usually far less thanks to trie pruning",
  gen=_ws2_gen)
