#!/usr/bin/env python3
"""
scripts/watch_scene.py

Watch the ppidc/ Python source for changes and re-render a single Manim scene
with `manim -ql`. Use this for the fastest animation-only edit-build-view loop.

For viewing, keep a browser or video player open on the rendered file and
refresh it after each render. The script prints the output path every time.

Usage:
    uv run --group dev python scripts/watch_scene.py TransposeTransform
    uv run --group dev python scripts/watch_scene.py proof_walkthrough.ProofWalkthrough
    uv run --group dev python scripts/watch_scene.py TransposeTransform --quality m
"""
from __future__ import annotations

import argparse
import ast
import subprocess
import sys
from pathlib import Path

from watchfiles import watch

ROOT = Path(__file__).resolve().parent.parent
PPIDC = ROOT / "ppidc"
MEDIA_DIR = ROOT / "media"

SCENE_BASE_HINTS = ("Scene",)
QUALITY_DIR = {
    "l": "480p15",
    "m": "720p30",
    "h": "1080p60",
    "k": "2160p60",
}


def discover_scene(selector: str) -> tuple[Path, str] | tuple[None, None]:
    """Find the ppidc/*.py file that defines the requested scene class."""
    if "." in selector:
        want_file, want_class = selector.rsplit(".", 1)
    else:
        want_file, want_class = None, selector

    for py_file in sorted(PPIDC.rglob("*.py")):
        if py_file.name.startswith("_"):
            continue
        if want_file and py_file.stem != want_file:
            continue

        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        except SyntaxError as e:
            print(f"  ! skipping {py_file}: syntax error ({e})", file=sys.stderr)
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            base_names = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    base_names.append(base.id)
                elif isinstance(base, ast.Attribute):
                    base_names.append(base.attr)
            if any(hint in b for b in base_names for hint in SCENE_BASE_HINTS):  # noqa: SIM102
                if node.name == want_class:
                    return py_file, node.name

    return None, None


def render_scene(py_file: Path, class_name: str, quality: str) -> Path | None:
    cmd = ["uv", "run", "manim", "render", f"-q{quality}", str(py_file), class_name]
    print(f"→ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=ROOT, check=False)
    if result.returncode != 0:
        print(f"  ✗ manim render failed (exit {result.returncode})", file=sys.stderr)
        return None

    output = MEDIA_DIR / "videos" / py_file.stem / QUALITY_DIR[quality] / f"{class_name}.mp4"
    if output.exists():
        print(f"  ✓ rendered: {output.relative_to(ROOT)}")
    else:
        print(f"  ! expected output not found: {output}", file=sys.stderr)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Watch ppidc/*.py and re-render a single Manim scene on change.",
    )
    parser.add_argument("scene", help="scene class name, e.g. TransposeTransform or slides.TransposeTransform")
    parser.add_argument(
        "--quality",
        choices=["l", "m", "h", "k"],
        default="l",
        help="manim render quality: l=480p15 (fast, default), m=720p30, h=1080p60, k=2160p60",
    )
    args = parser.parse_args()

    py_file, class_name = discover_scene(args.scene)
    if py_file is None:
        sys.exit(f"Scene not found: {args.scene}")
    if class_name is None:
        sys.exit(f"Class not found for scene: {args.scene}")

    print(f"Watching {PPIDC.relative_to(ROOT)} for changes to {class_name}")
    print(f"Source: {py_file.relative_to(ROOT)}")
    print("Keep a browser/video player open on the output file and refresh it after each render.")
    print("Press Ctrl+C to stop.\n")

    output = render_scene(py_file, class_name, args.quality)
    if output:
        print(f"Output: {output}\n")

    for changes in watch(PPIDC):
        changed = {Path(c[1]) for c in changes}
        py_changes = [p for p in changed if p.suffix == ".py"]
        if py_changes:
            print(f"Changed: {', '.join(str(p.relative_to(ROOT)) for p in py_changes)}")
            output = render_scene(py_file, class_name, args.quality)
            if output:
                print(f"Output: {output}\n")


if __name__ == "__main__":
    main()
