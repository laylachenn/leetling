#!/usr/bin/env python3
"""Leetling test runner.

Runs a user's Python solution against a problem's test cases, LeetCode style.

Usage:
    python3 runner.py <problems.json> <problem_id> <solution.py> <run|submit> <out.json>

The result is written as JSON to <out.json> so that anything the user print()s
can't corrupt it. This module is also imported by content/build_problems.py to
compute expected outputs from the reference solutions.
"""
import bisect
import collections
import contextlib
import copy
import functools
import heapq
import io
import itertools
import json
import linecache
import math
import random
import re
import signal
import string
import sys
import time
import traceback
import typing

sys.setrecursionlimit(20000)

# ---------------------------------------------------------------- data types


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

    def __repr__(self):
        return f"ListNode({self.val})"


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

    def __repr__(self):
        return f"TreeNode({self.val})"


class Node:
    """Graph node (Clone Graph)."""

    def __init__(self, val=0, neighbors=None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []

    def __repr__(self):
        return f"Node({self.val})"


# ------------------------------------------------------------------- helpers


def build_list(arr):
    dummy = ListNode()
    cur = dummy
    for v in arr:
        cur.next = ListNode(v)
        cur = cur.next
    return dummy.next


def list_to_arr(head, limit=200000):
    out = []
    while head is not None:
        if not hasattr(head, "val"):
            raise TypeError(f"expected a ListNode but got {type(head).__name__}")
        out.append(head.val)
        head = head.next
        if len(out) > limit:
            raise AssertionError("your linked list seems to have a cycle (it never ends!)")
    return out


def build_cycle(arr, pos):
    head = build_list(arr)
    if pos < 0 or head is None:
        return head
    nodes = []
    cur = head
    while cur:
        nodes.append(cur)
        cur = cur.next
    nodes[-1].next = nodes[pos]
    return head


def build_tree(arr):
    if not arr or arr[0] is None:
        return None
    root = TreeNode(arr[0])
    queue = collections.deque([root])
    i = 1
    while queue and i < len(arr):
        node = queue.popleft()
        if i < len(arr) and arr[i] is not None:
            node.left = TreeNode(arr[i])
            queue.append(node.left)
        i += 1
        if i < len(arr) and arr[i] is not None:
            node.right = TreeNode(arr[i])
            queue.append(node.right)
        i += 1
    return root


def tree_to_arr(root, limit=200000):
    if root is None:
        return []
    out = []
    queue = collections.deque([root])
    while queue:
        node = queue.popleft()
        if node is None:
            out.append(None)
            continue
        if not hasattr(node, "val"):
            raise TypeError(f"expected a TreeNode but got {type(node).__name__}")
        out.append(node.val)
        queue.append(node.left)
        queue.append(node.right)
        if len(out) > limit:
            raise AssertionError("your tree seems to loop back on itself")
    while out and out[-1] is None:
        out.pop()
    return out


def find_node(root, val):
    stack = [root]
    while stack:
        node = stack.pop()
        if node is None:
            continue
        if node.val == val:
            return node
        stack.append(node.left)
        stack.append(node.right)
    return None


def build_graph(adj):
    if not adj:
        return None
    nodes = [Node(i + 1) for i in range(len(adj))]
    for i, nbrs in enumerate(adj):
        nodes[i].neighbors = [nodes[j - 1] for j in nbrs]
    return nodes[0]


def collect_graph(node):
    if node is None:
        return []
    seen = {id(node): node}
    queue = collections.deque([node])
    while queue:
        cur = queue.popleft()
        for nb in cur.neighbors:
            if id(nb) not in seen:
                seen[id(nb)] = nb
                queue.append(nb)
    return list(seen.values())


def graph_to_adj(node):
    nodes = collect_graph(node)
    if not nodes:
        return []
    by_val = {n.val: n for n in nodes}
    return [[nb.val for nb in by_val[v].neighbors] if v in by_val else [] for v in range(1, max(by_val) + 1)]


def run_design(cls, ops, arglists):
    obj = cls(*arglists[0])
    out = [None]
    for op, a in zip(ops[1:], arglists[1:]):
        out.append(getattr(obj, op)(*a))
    return out


HELPERS = {
    "ListNode": ListNode,
    "TreeNode": TreeNode,
    "Node": Node,
    "build_list": build_list,
    "list_to_arr": list_to_arr,
    "build_cycle": build_cycle,
    "build_tree": build_tree,
    "tree_to_arr": tree_to_arr,
    "find_node": find_node,
    "build_graph": build_graph,
    "collect_graph": collect_graph,
    "graph_to_adj": graph_to_adj,
    "run_design": run_design,
}


def base_namespace():
    """Everything LeetCode pre-imports for Python, plus the harness helpers."""
    ns = {"__name__": "solution", "__builtins__": __builtins__}
    for name in ("List", "Optional", "Dict", "Set", "Tuple", "Deque", "Any", "Union"):
        ns[name] = getattr(typing, name)
    for mod in (collections, heapq, math, functools, itertools, bisect, string, re, random):
        ns[mod.__name__] = mod
    ns.update(
        deque=collections.deque,
        defaultdict=collections.defaultdict,
        Counter=collections.Counter,
        OrderedDict=collections.OrderedDict,
        lru_cache=functools.lru_cache,
        cache=functools.cache,
        reduce=functools.reduce,
        heappush=heapq.heappush,
        heappop=heapq.heappop,
        heapify=heapq.heapify,
        inf=math.inf,
    )
    ns.update(HELPERS)
    return ns


# ---------------------------------------------------------------- comparison


def jsonable(v):
    if isinstance(v, bool) or v is None or isinstance(v, (int, str)):
        return v
    if isinstance(v, float):
        if math.isfinite(v):
            return v
        return repr(v)
    if isinstance(v, (list, tuple)):
        return [jsonable(x) for x in v]
    if isinstance(v, (set, frozenset)):
        items = [jsonable(x) for x in v]
        try:
            return sorted(items)
        except TypeError:
            return items
    if isinstance(v, dict):
        return {str(k): jsonable(x) for k, x in v.items()}
    if isinstance(v, ListNode):
        return list_to_arr(v)
    if isinstance(v, TreeNode):
        return tree_to_arr(v)
    return repr(v)


def fmt(v, limit=600):
    s = json.dumps(jsonable(v), separators=(",", ":"), ensure_ascii=False)
    if len(s) > limit:
        s = s[: limit - 1] + "…"
    return s


def _sorted_safe(items):
    try:
        return sorted(items)
    except TypeError:
        return sorted(items, key=lambda x: json.dumps(x, sort_keys=True))


def _approx(a, b):
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_approx(x, y) for x, y in zip(a, b))
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) and not isinstance(b, bool):
        return abs(a - b) <= 1e-5 * max(1.0, abs(b))
    return a == b


def _check_alien(got, expected, args):
    words = args[0]
    if expected == "":
        return got == ""
    if not isinstance(got, str):
        return False
    letters = set("".join(words))
    if len(got) != len(set(got)) or set(got) != letters:
        return False
    rank = {c: i for i, c in enumerate(got)}
    for w1, w2 in zip(words, words[1:]):
        for a, b in zip(w1, w2):
            if a != b:
                if rank[a] > rank[b]:
                    return False
                break
    return True


def _check_palindrome(got, expected, args):
    s = args[0]
    return isinstance(got, str) and len(got) == len(expected) and got == got[::-1] and got in s


def _check_min_window(got, expected, args):
    s, t = args
    if expected == "":
        return got == ""
    if not isinstance(got, str) or len(got) != len(expected) or got not in s:
        return False
    need = collections.Counter(t)
    have = collections.Counter(got)
    return all(have[c] >= k for c, k in need.items())


CUSTOM_CHECKS = {
    "alien": _check_alien,
    "palindrome": _check_palindrome,
    "min_window": _check_min_window,
}


def compare(got, expected, mode, args):
    if mode in CUSTOM_CHECKS:
        try:
            return CUSTOM_CHECKS[mode](got, expected, args)
        except Exception:
            return False
    g = jsonable(got)
    if mode == "exact":
        return g == expected
    if mode == "float":
        return _approx(g, expected)
    if not isinstance(g, list):
        return False
    if mode == "unordered":
        return _sorted_safe(g) == _sorted_safe(expected)
    if mode == "nested_unordered":
        try:
            return _sorted_safe([_sorted_safe(x) for x in g]) == _sorted_safe([_sorted_safe(x) for x in expected])
        except TypeError:
            return False
    raise ValueError(f"unknown compare mode {mode}")


# -------------------------------------------------------------------- running


class TimeLimitExceeded(BaseException):
    pass


def _alarm(signum, frame):
    raise TimeLimitExceeded()


def user_error(exc):
    """Format an exception showing only frames from the user's solution."""
    frames = [f for f in traceback.extract_tb(exc.__traceback__) if f.filename == "solution.py"]
    lines = []
    for f in frames[-3:]:
        lines.append(f"Line {f.lineno} in {f.name}: {(f.line or '').strip()}")
    lines.append(f"{type(exc).__name__}: {exc}")
    return "\n".join(lines)


def prepare(problem, code):
    ns = base_namespace()
    # Let tracebacks show the user's source lines.
    linecache.cache["solution.py"] = (len(code), None, code.splitlines(True), "solution.py")
    compiled = compile(code, "solution.py", "exec")
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compiled, ns)
    exec(compile(problem["driver"], "<driver>", "exec"), ns)
    return ns


def run_case(ns, args, timeout):
    a = copy.deepcopy(args)
    buf = io.StringIO()
    if timeout:
        signal.signal(signal.SIGALRM, _alarm)
        signal.setitimer(signal.ITIMER_REAL, timeout)
    try:
        with contextlib.redirect_stdout(buf):
            got = ns["drive"](a)
    finally:
        if timeout:
            signal.setitimer(signal.ITIMER_REAL, 0)
    out = buf.getvalue()
    if len(out) > 3000:
        out = out[:3000] + "\n… (output trimmed)"
    return got, out


def format_input(params, args):
    return "\n".join(f"{p} = {fmt(a, 400)}" for p, a in zip(params, args))


def run(problem, code, mode, timeout=4.0):
    tests = problem["tests"]
    if mode == "run":
        tests = [t for t in tests if not t["hidden"]]
    started = time.perf_counter()
    result = {"status": "accepted", "passed": 0, "total": len(tests), "results": [], "message": ""}

    try:
        ns = prepare(problem, code)
    except SyntaxError as e:
        result["status"] = "syntax_error"
        result["message"] = f"Line {e.lineno}: {e.msg}\n{(e.text or '').rstrip()}"
        return result
    except BaseException as e:  # noqa: BLE001 - user code can raise anything
        result["status"] = "runtime_error"
        result["message"] = user_error(e)
        return result

    for i, t in enumerate(tests):
        entry = {
            "index": i,
            "hidden": t["hidden"],
            "input": format_input(problem["params"], t["args"]),
            "expected": fmt(t["expected"]),
            "output": "",
            "stdout": "",
            "error": "",
            "passed": False,
        }
        try:
            got, out = run_case(ns, t["args"], timeout)
            entry["stdout"] = out
            entry["output"] = fmt(got)
            entry["passed"] = compare(got, t["expected"], problem["compare"], t["args"])
        except TimeLimitExceeded:
            entry["error"] = f"Time Limit Exceeded (took longer than {timeout:g}s on this input)"
            entry["status"] = "time_limit"
        except RecursionError as e:
            entry["error"] = user_error(e) + "\n(Recursion went too deep — is there a missing base case?)"
            entry["status"] = "runtime_error"
        except BaseException as e:  # noqa: BLE001
            entry["error"] = user_error(e)
            entry["status"] = "runtime_error"

        if entry["passed"]:
            result["passed"] += 1
        else:
            entry.setdefault("status", "wrong_answer")
            if result["status"] == "accepted":
                result["status"] = entry["status"]

        # Always show visible tests; for hidden tests, only show the first failure.
        if not t["hidden"] or not entry["passed"]:
            result["results"].append(entry)
        if not entry["passed"] and (mode == "submit" or entry["status"] == "time_limit"):
            break

    result["runtime_ms"] = int((time.perf_counter() - started) * 1000)
    return result


def main(argv):
    problems_path, pid, solution_path, mode, out_path = argv[1:6]
    with open(problems_path, encoding="utf-8") as f:
        problems = json.load(f)
    problem = next(p for p in problems if p["id"] == int(pid))
    with open(solution_path, encoding="utf-8") as f:
        code = f.read()
    real_stdout = sys.stdout
    try:
        result = run(problem, code, mode)
    except BaseException as e:  # noqa: BLE001
        result = {"status": "runtime_error", "passed": 0, "total": 0, "results": [], "message": user_error(e)}
    sys.stdout = real_stdout
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f)


if __name__ == "__main__":
    main(sys.argv)
