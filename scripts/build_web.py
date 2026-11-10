#!/usr/bin/env python3
"""Prepare web/data/ for the Leetling web app (the iPhone / browser version).

Copies the judge and splits the catalog in two:
- problems.json       everything the UI needs (no tests/driver), small enough to load fast
- problems-full.json  the full catalog, loaded only by the Python worker for judging

Run it after rebuilding Resources/problems.json. scripts/serve_web.sh and the Pages
deploy workflow both call it.
"""
import json
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "web" / "data"

UI_FIELDS = ["id", "slug", "title", "lc", "difficulty", "category", "params", "description",
             "examples", "constraints", "starter", "hints", "solution", "complexity"]


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    problems = json.loads((ROOT / "Resources" / "problems.json").read_text(encoding="utf-8"))
    lite = [{k: p[k] for k in UI_FIELDS} for p in problems]
    (DATA / "problems.json").write_text(json.dumps(lite, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    shutil.copyfile(ROOT / "Resources" / "problems.json", DATA / "problems-full.json")
    shutil.copyfile(ROOT / "Resources" / "runner.py", DATA / "runner.py")
    print(f"web/data: {len(lite)} problems")


if __name__ == "__main__":
    main()
