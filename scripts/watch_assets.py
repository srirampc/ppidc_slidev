#!/usr/bin/env python3
"""
scripts/watch_assets.py

Watch the ppidc/ Python source for changes and re-run scripts/build_assets.py.
Use this alongside `cd slides && pnpm dev` for a full Manim + Slidev
edit-build-view loop.

Usage:
    uv run --group dev python scripts/watch_assets.py
    uv run --group dev python scripts/watch_assets.py --quality l
    uv run --group dev python scripts/watch_assets.py --scene TransposeTransform
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from watchfiles import watch

ROOT = Path(__file__).resolve().parent.parent
PPIDC = ROOT / "ppidc"


def build(args: argparse.Namespace) -> None:
    cmd = ["uv", "run", "python", "scripts/build_assets.py"]
    if args.quality:
        cmd.extend(["--quality", args.quality])
    if args.scene:
        cmd.extend(["--scene", args.scene])
    print(f"→ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=ROOT, check=False)
    if result.returncode != 0:
        print(f"  ✗ build_assets.py failed (exit {result.returncode})", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Watch ppidc/*.py and re-run scripts/build_assets.py on change.",
    )
    parser.add_argument(
        "--quality",
        choices=["l", "m", "h", "k"],
        default="l",
        help="quality passed to build_assets.py: l=480p15 (fast, default), m=720p30, h=1080p60, k=2160p60",
    )
    parser.add_argument(
        "--scene",
        default=None,
        help="only render one scene, passed through to build_assets.py",
    )
    args = parser.parse_args()

    print(f"Watching {PPIDC.relative_to(ROOT)} for changes.")
    print("Run `cd slides && pnpm dev` in another terminal to see the deck.")
    print("Press Ctrl+C to stop.\n")

    build(args)

    for changes in watch(PPIDC):
        changed = {Path(c[1]) for c in changes}
        py_changes = [p for p in changed if p.suffix == ".py"]
        if py_changes:
            print(f"Changed: {', '.join(str(p.relative_to(ROOT)) for p in py_changes)}")
            build(args)
            print()


if __name__ == "__main__":
    main()
