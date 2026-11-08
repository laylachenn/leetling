"""Shared helpers for authoring the Blind 75 problem catalog.

Each problem is registered with P(...). Expected outputs for every test are
computed by running the problem's reference `solution` through the exact same
harness the app uses (Resources/runner.py), so tests and solutions can't drift.
If an example lists `out`, the build asserts the reference agrees with it.
"""
import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("leetling_runner", ROOT / "Resources" / "runner.py")
runner = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(runner)

PROBLEMS = []

CATEGORIES = [
    "Arrays & Hashing",
    "Two Pointers",
    "Sliding Window",
    "Stack",
    "Binary Search",
    "Linked List",
    "Trees",
    "Tries",
    "Heap / Priority Queue",
    "Backtracking",
    "Graphs",
    "Advanced Graphs",
    "1-D Dynamic Programming",
    "2-D Dynamic Programming",
    "Greedy",
    "Intervals",
    "Math & Geometry",
    "Bit Manipulation",
]

LIST_DEF = """# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
"""

TREE_DEF = """# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
"""


def P(**kw):
    required = ["id", "slug", "title", "lc", "difficulty", "category", "params", "description",
                "examples", "starter", "hints", "solution", "complexity"]
    for k in required:
        assert k in kw, f"{kw.get('title')}: missing {k}"
    assert kw["category"] in CATEGORIES, kw["category"]
    assert kw["difficulty"] in ("Easy", "Medium", "Hard")
    assert len(kw["hints"]) == 3, kw["title"]
    kw.setdefault("compare", "exact")
    kw.setdefault("constraints", [])
    kw.setdefault("gen", None)
    if "driver" not in kw:
        kw["driver"] = f"def drive(args):\n    return Solution().{kw['method']}(*args)\n"
    PROBLEMS.append(kw)


def E(*args, out=None, why=None, has_out=None):
    """An example test case. `out` is the known-correct answer (checked at build time)."""
    return {"args": list(args), "out": out, "has_out": has_out if has_out is not None else out is not None, "why": why}


# ------------------------------------------------------------- generators


def rand_ints(r, n, lo, hi):
    return [r.randint(lo, hi) for _ in range(n)]


def rand_str(r, n, alphabet="abcdefghijklmnopqrstuvwxyz"):
    return "".join(r.choice(alphabet) for _ in range(n))


def rand_tree(r, n, lo=-100, hi=100, distinct=False):
    """Random binary tree (as a LeetCode level-order array) with n nodes."""
    if n == 0:
        return []
    vals = r.sample(range(lo, hi + 1), n) if distinct else [r.randint(lo, hi) for _ in range(n)]
    root = runner.TreeNode(vals[0])
    nodes = [root]
    for v in vals[1:]:
        while True:
            parent = r.choice(nodes)
            side = r.choice(("left", "right"))
            if getattr(parent, side) is None:
                child = runner.TreeNode(v)
                setattr(parent, side, child)
                nodes.append(child)
                break
    return runner.tree_to_arr(root)


def rand_bst(r, n, lo=0, hi=1000):
    vals = r.sample(range(lo, hi + 1), n)
    root = None

    def insert(node, v):
        if node is None:
            return runner.TreeNode(v)
        if v < node.val:
            node.left = insert(node.left, v)
        else:
            node.right = insert(node.right, v)
        return node

    for v in vals:
        root = insert(root, v)
    return runner.tree_to_arr(root), vals
