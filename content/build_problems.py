#!/usr/bin/env python3
"""Builds Resources/problems.json from the problem catalog.

For every problem it:
  1. runs the reference solution through the real harness to compute expected outputs,
  2. checks the reference agrees with each hand-written example `out`,
  3. submits the reference solution and requires "accepted",
  4. checks the starter code compiles and is NOT accepted.

Run:  python3 content/build_problems.py
"""
import json
import random
import sys

import common
from common import CATEGORIES, PROBLEMS, ROOT, runner

import problems_1  # noqa: F401  (registers problems via P())
import problems_2  # noqa: F401
import problems_3  # noqa: F401
import problems_4  # noqa: F401


def build():
    failures = []
    out = []
    ids = sorted(p["id"] for p in PROBLEMS)
    assert ids == list(range(1, 76)), f"expected ids 1..75, got {ids}"

    for p in sorted(PROBLEMS, key=lambda p: p["id"]):
        r = random.Random(1000 + p["id"])
        harness = {"driver": p["driver"], "params": p["params"], "compare": p["compare"]}
        ns = runner.prepare(harness, p["solution"])

        def expected_for(args):
            got, _ = runner.run_case(ns, args, timeout=None)
            return runner.jsonable(got)

        tests, examples = [], []
        for ex in p["examples"]:
            got = expected_for(ex["args"])
            if ex["has_out"]:
                if not runner.compare(ex["out"], got, p["compare"], ex["args"]) and not runner.compare(got, ex["out"], p["compare"], ex["args"]):
                    failures.append(f"#{p['id']} {p['title']}: example {ex['args']} expected {ex['out']!r}, reference gave {got!r}")
                shown = ex["out"]
            else:
                shown = got
            tests.append({"args": ex["args"], "expected": shown, "hidden": False})
            examples.append({
                "input": runner.format_input(p["params"], ex["args"]),
                "output": runner.fmt(shown, 2000),
                "explanation": ex["why"],
            })
        for args in (p["gen"](r) if p["gen"] else []):
            tests.append({"args": args, "expected": expected_for(args), "hidden": True})

        record = {
            "id": p["id"], "slug": p["slug"], "title": p["title"], "lc": p["lc"],
            "difficulty": p["difficulty"], "category": p["category"],
            "params": p["params"], "description": p["description"], "examples": examples,
            "constraints": p["constraints"], "starter": p["starter"], "hints": p["hints"],
            "solution": p["solution"], "complexity": p["complexity"],
            "driver": p["driver"], "compare": p["compare"], "tests": tests,
        }

        verdict = runner.run(record, p["solution"], "submit")
        if verdict["status"] != "accepted":
            failures.append(f"#{p['id']} {p['title']}: reference solution got {verdict['status']}: "
                            f"{json.dumps(verdict['results'][-1:] or verdict['message'])[:600]}")
        starter = runner.run(record, p["starter"], "run")
        if starter["status"] in ("accepted", "syntax_error"):
            failures.append(f"#{p['id']} {p['title']}: starter code status {starter['status']} {starter['message']}")
        out.append(record)
        print(f"  ✓ {p['id']:>2} {p['title']:<58} {len(tests):>2} tests  {verdict.get('runtime_ms', 0):>5} ms")

    cats = {p["category"] for p in out}
    assert cats == set(CATEGORIES), cats ^ set(CATEGORIES)
    if failures:
        print("\n".join(["", "FAILURES:"] + failures))
        sys.exit(1)

    dest = ROOT / "Resources" / "problems.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    counts = {d: sum(p["difficulty"] == d for p in out) for d in ("Easy", "Medium", "Hard")}
    print(f"\nWrote {dest.relative_to(ROOT)} ({dest.stat().st_size // 1024} KB) — {counts}")


if __name__ == "__main__":
    build()
