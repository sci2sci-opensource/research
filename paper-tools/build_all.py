#!/usr/bin/env python3
"""Build every registered paper in the repository.

A paper is any *.md file with a `title:` in YAML front matter (README/CLAUDE/notes files
without front matter are skipped automatically). Runs compile_paper.py on each.

    python paper-tools/build_all.py [--pdf] [--html] [--arxiv]
"""

import subprocess
import sys
from pathlib import Path

from compile_paper import read_front_matter

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
SKIP_DIRS = {".git", "arxiv_submission", "runs", "__pycache__", "node_modules"}


def papers():
    for md in sorted(REPO.rglob("*.md")):
        if any(part in SKIP_DIRS for part in md.parts):
            continue
        if "title" in read_front_matter(md):
            yield md


def main():
    flags = sys.argv[1:]
    found = list(papers())
    if not found:
        sys.exit("no papers with front matter found")
    print(f"{len(found)} paper(s):")
    failed = []
    for p in found:
        print(f"\n== {p.relative_to(REPO)}")
        r = subprocess.run([sys.executable, str(TOOLS / "compile_paper.py"), str(p), *flags])
        if r.returncode != 0:
            failed.append(p)
    if failed:
        print("\nFAILED:")
        for p in failed:
            print(f"  {p.relative_to(REPO)}")
        sys.exit(1)
    print("\nall papers built")


if __name__ == "__main__":
    main()
