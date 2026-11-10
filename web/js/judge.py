"""Browser-side glue around Resources/runner.py (loaded into Pyodide by runner-worker.js).

runner.py is shared with the Mac app unchanged. The differences in the browser:
- There's no SIGALRM, so per-test timeouts are off (timeout=0). The worker enforces a
  hard time limit instead by terminating itself from the main thread.
- WebAssembly has a much smaller stack than CPython on macOS, so the recursion limit is
  lowered from runner.py's 20000 to something the browser can survive.
"""
import functools
import json
import sys

import runner

# Python-to-Python recursion is cheap in 3.13, but unwinding a RecursionError still uses the
# C stack; ~5500 levels crashed Pyodide in testing, so leave a margin.
sys.setrecursionlimit(4000)

BROWSER_NOTE = ("\n(Leetling on the web has a smaller stack than the Mac app, so very deep recursion "
                "can hit this even when your logic is right. An iterative version will always work 🌷)")


# The C lru_cache recurses through the C stack, and in WebAssembly that overflows at
# only ~250 levels, which breaks everyday DP solutions. Python-to-Python calls don't use the
# C stack in 3.13, so a pure-Python cache handles 10k+ levels. Same API, but always unbounded.
def _lru_cache(maxsize=128, typed=False):
    def decorate(fn):
        memo = {}
        hits = misses = 0
        kwd_mark = object()

        def wrapper(*args, **kwargs):
            nonlocal hits, misses
            key = args if not kwargs else args + (kwd_mark,) + tuple(sorted(kwargs.items()))
            if typed:
                key += tuple(type(a) for a in args)
            if key in memo:
                hits += 1
                return memo[key]
            misses += 1
            value = fn(*args, **kwargs)
            if maxsize != 0:
                memo[key] = value
            return value

        def cache_info():
            return functools._CacheInfo(hits, misses, maxsize, len(memo))

        def cache_clear():
            nonlocal hits, misses
            memo.clear()
            hits = misses = 0

        wrapper.cache_info = cache_info
        wrapper.cache_clear = cache_clear
        return functools.update_wrapper(wrapper, fn)

    if callable(maxsize) and not isinstance(maxsize, bool):  # used bare: @lru_cache
        fn, maxsize = maxsize, 128
        return decorate(fn)
    return decorate


functools.lru_cache = _lru_cache
functools.cache = lambda fn: _lru_cache(None)(fn)

PROBLEMS = {}

# Freeing a long linked list (or a tall tree) makes CPython deallocate node -> next -> next…
# recursively, and a few thousand levels overflows the WebAssembly stack and kills Pyodide.
# So every node is kept alive in a registry and torn down iteratively: unlink every node
# first, then drop them all, so each deallocation is shallow.
_NODES = []


def _track(cls):
    original = cls.__init__

    def __init__(self, *args, **kwargs):
        original(self, *args, **kwargs)
        _NODES.append(self)

    cls.__init__ = __init__


for _cls in (runner.ListNode, runner.TreeNode, runner.Node):
    _track(_cls)


def _release_nodes():
    for node in _NODES:
        d = getattr(node, "__dict__", None)
        if d:
            d.clear()
    _NODES.clear()


_original_run_case = runner.run_case


def _run_case(ns, args, timeout):
    # The previous case's output has already been compared and formatted by now.
    _release_nodes()
    return _original_run_case(ns, args, timeout)


runner.run_case = _run_case


def load(text):
    global PROBLEMS
    PROBLEMS = {p["id"]: p for p in json.loads(text)}
    return len(PROBLEMS)


def judge(pid, code, mode):
    problem = PROBLEMS[int(pid)]
    # iOS "smart punctuation" can sneak curly quotes into code typed on a phone.
    code = (code.replace("‘", "'").replace("’", "'")
                .replace("“", '"').replace("”", '"'))
    real_stdout = sys.stdout
    try:
        result = runner.run(problem, code, mode, timeout=0)
    except RecursionError as e:
        result = {"status": "runtime_error", "passed": 0, "total": 0, "results": [],
                  "message": runner.user_error(e) + "\n(Recursion went too deep — is there a missing base case?)"}
    except BaseException as e:  # noqa: BLE001 - user code can raise anything
        result = {"status": "runtime_error", "passed": 0, "total": 0, "results": [], "message": runner.user_error(e)}
    sys.stdout = real_stdout
    _release_nodes()
    for entry in [result] + result.get("results", []):
        for field in ("message", "error"):
            if "recursion depth" in entry.get(field, ""):
                entry[field] += BROWSER_NOTE
    return json.dumps(result)
