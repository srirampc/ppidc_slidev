#!/usr/bin/env python3
"""
build_assets.py

Discovers Manim Scene subclasses under `MANIM_SRC`, renders each with
`--save_sections` (so multi-part animations produce one clip per
next_section() checkpoint), and copies the resulting clips + a
per-scene manifest into `slides/public/videos/` for Slidev to consume.

Each scene is also rendered a second time with `--save_last_frame` (manim's
`-s`) and that final frame is copied to `slides/public/videos/<slug>/poster.png`.
The second render is required because `-s` forces manim's
write_to_movie=False, so the image can't share the video render. Pass
`--no-poster` to skip poster generation.

`--theme` selects the deck's color theme (dark/light) — the package's
default-ThemeType global defaults to `dark`. The theme is passed to the
manim subprocess through the `PPIDC_THEME` environment variable, which
`ppidc/__init__.py` reads to seed its default config.

Also writes ready-to-paste Slidev markdown snippets to `slides/snippets/`
for each scene, one for "auto-start on slide enter" and one for "wait for
a click", each with the correct `clicks:` frontmatter value already
computed from the clip count (so it can't drift out of sync).

Usage:
    uv run python scripts/build_assets.py
    uv run python scripts/build_assets.py --quality h
    uv run python scripts/build_assets.py --scene proof_walkthrough.ProofWalkthrough
    uv run python scripts/build_assets.py --clean
    uv run python scripts/build_assets.py --no-poster   # videos only, no last-frame images
    uv run python scripts/build_assets.py --theme light # render with the light color theme

Requires manim to be a dependency in your uv-managed project
(`uv add manim`).
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent  # project root, assuming scripts/build_assets.py
MANIM_SRC = ROOT / "ppidc"
MEDIA_DIR = ROOT / "media"
SLIDES_PUBLIC_VIDEOS = ROOT / "slides" / "public" / "videos"
SLIDES_COMPONENTS_GENERATED = ROOT / "slides" / "components" / "generated"

# manim quality flag -> (flag, resolution dir name it writes under media/videos/<file>/)
QUALITY_MAP = {
    "l": ("-ql", "480p15"),
    "m": ("-qm", "720p30"),
    "h": ("-qh", "1080p60"),
    "k": ("-qk", "2160p60"),
}

SCENE_BASE_HINTS = ("Scene",)  # matches Scene, MovingCameraScene, ThreeDScene, etc.


@dataclass
class SceneRef:
    file: Path       # MANIM_SRC/foo.py
    class_name: str  # e.g. "ProofWalkthrough"

    @property
    def slug(self) -> str:
        # unique-ish output folder name: <filestem>_<ClassName>
        return f"{self.file.stem}_{self.class_name}"


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

def discover_scenes(root: Path) -> list[SceneRef]:
    """Walk MANIM_SRC/*.py and find classes that look like Manim Scenes via AST,
    so we don't have to import manim just to enumerate scenes."""
    scenes: list[SceneRef] = []
    for py_file in sorted(root.rglob("*.py")):
        if py_file.name.startswith("_"):
            continue
        try:
            tree = ast.parse(py_file.read_text(), filename=str(py_file))
        except SyntaxError as e:
            print(f"  ! skipping {py_file}: syntax error ({e})", file=sys.stderr)
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            base_names = []
            for base in node.bases:
                # handles `Scene`, `manim.Scene`, `mn.MovingCameraScene`, etc.
                if isinstance(base, ast.Name):
                    base_names.append(base.id)
                elif isinstance(base, ast.Attribute):
                    base_names.append(base.attr)
            if any(hint in b for b in base_names for hint in SCENE_BASE_HINTS):
                scenes.append(SceneRef(file=py_file, class_name=node.name))

    return scenes


def filter_scenes(scenes: list[SceneRef], selector: str | None) -> list[SceneRef]:
    if not selector:
        return scenes
    # accept "ClassName" or "filename.ClassName"
    if "." in selector:
        want_file, want_class = selector.rsplit(".", 1)
    else:
        want_file, want_class = None, selector
    out = [
        s for s in scenes
        if s.class_name == want_class and (want_file is None or s.file.stem == want_file)
    ]
    if not out:
        print(f"No scene matched selector {selector!r}", file=sys.stderr)
    return out


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def _manim_env(theme: str) -> dict[str, str]:
    """Environment for `manim render` subprocesses: the caller's env plus
    PPIDC_THEME, which ppidc/__init__.py reads to seed its default config
    (the theme is a Python-level global, not a manim config option)."""
    env = os.environ.copy()
    env["PPIDC_THEME"] = theme
    return env


def render_scene(scene: SceneRef, quality_flag: str, theme: str) -> Path:
    """Runs `uv run manim render --save_sections ...` for one scene.
    Returns the path to the sections/ dir manim wrote."""
    print(f"→ rendering {scene.file.relative_to(ROOT)}::{scene.class_name}")

    cmd = [
        "uv", "run", "manim", "render",
        quality_flag,
        "--save_sections",
        str(scene.file),
        scene.class_name,
    ]
    result = subprocess.run(cmd, cwd=ROOT, env=_manim_env(theme))  # noqa: PLW1510
    if result.returncode != 0:
        raise RuntimeError(f"manim render failed for {scene.slug} (exit {result.returncode})")

    res_dir = QUALITY_MAP[quality_flag.lstrip("-q")][1]
    sections_dir = MEDIA_DIR / "videos" / scene.file.stem / res_dir / "sections"
    if not sections_dir.exists():
        raise FileNotFoundError(
            f"expected sections dir not found: {sections_dir}\n"
            "(check that the scene actually calls self.next_section(), and that "
            "MEDIA_DIR / quality dir naming matches your manim config)"
        )
    return sections_dir


def render_poster(scene: SceneRef, quality_flag: str, theme: str) -> Path:
    """Runs `uv run manim render --save_last_frame ...` for one scene to save
    its final frame as a PNG. A second manim invocation is required because
    `-s` forces write_to_movie=False, so it can't share the video render.

    `-o poster.png` pins the output name: without it manim suffixes the file
    with _ManimCE_v<version>, which would make the path unpredictable.

    Returns the path manim wrote:
    media/images/<filestem>/poster.png."""
    print(f"→ rendering poster {scene.file.relative_to(ROOT)}::{scene.class_name}")

    cmd = [
        "uv", "run", "manim", "render",
        quality_flag,
        "--save_last_frame",
        "-o", "poster.png",
        str(scene.file),
        scene.class_name,
    ]
    result = subprocess.run(cmd, cwd=ROOT, env=_manim_env(theme))  # noqa: PLW1510
    if result.returncode != 0:
        raise RuntimeError(
            f"manim poster render failed for {scene.slug} (exit {result.returncode})"
        )

    # manim's images_dir is media/images/<filestem>/ — note: no quality
    # subdir, unlike videos_dir (see images_dir in manim's default.cfg).
    poster = MEDIA_DIR / "images" / scene.file.stem / "poster.png"
    if not poster.exists():
        raise FileNotFoundError(
            f"expected poster image not found: {poster}\n"
            "(check that MEDIA_DIR/images naming matches your manim config)"
        )
    return poster


# ---------------------------------------------------------------------------
# Copying + manifest generation
# ---------------------------------------------------------------------------

def copy_clips(scene: SceneRef, sections_dir: Path) -> list[str]:
    """Copies the rendered section clips + manifest json into
    slides/public/videos/<slug>/, returns ordered list of web-relative clip paths."""
    dest_dir = SLIDES_PUBLIC_VIDEOS / scene.slug
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True)

    manifest_path = sections_dir / f"{scene.class_name}.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"section manifest missing: {manifest_path}")

    manim_sections = json.loads(manifest_path.read_text())

    clip_names: list[str] = []
    for section in manim_sections:
        # manim's section json entries include a "video" filename field
        video_name = section.get("video")
        if not video_name:
            continue
        src = sections_dir / video_name
        if not src.exists():
            print(f"  ! warning: {src} listed in manifest but missing on disk", file=sys.stderr)
            continue
        shutil.copy2(src, dest_dir / video_name)
        clip_names.append(video_name)

    if not clip_names:
        # scene had no next_section() calls — manim still emits one full clip
        fallback = list(sections_dir.glob("*.mp4"))
        for f in fallback:
            shutil.copy2(f, dest_dir / f.name)
            clip_names.append(f.name)
        clip_names.sort()

    web_paths = [f"/videos/{scene.slug}/{name}" for name in clip_names]

    # drop a per-scene manifest too, handy for the Vue component to fetch directly
    (dest_dir / "clips.json").write_text(json.dumps(web_paths, indent=2), encoding="utf-8")

    return web_paths


def copy_poster(scene: SceneRef, poster_path: Path) -> Path:
    """Copies the rendered last-frame image into slides/public/videos/<slug>/,
    next to the clips. Returns the web-visible dest path."""
    dest = SLIDES_PUBLIC_VIDEOS / scene.slug / "poster.png"
    shutil.copy2(poster_path, dest)
    return dest


def write_global_manifest(manifest: dict[str, list[str]]) -> None:
    SLIDES_PUBLIC_VIDEOS.mkdir(parents=True, exist_ok=True)
    out = SLIDES_PUBLIC_VIDEOS / "manifest.json"
    out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nWrote global manifest: {out.relative_to(ROOT)}")


# ---------------------------------------------------------------------------
# Slidev markdown snippet generation + per-scene wrapper components
# ---------------------------------------------------------------------------

def _clips_literal(web_paths: list[str], indent: str = "  ") -> str:
    """Formats a clip list as a JS/TS array literal, one entry per line."""
    lines = ",\n".join(f"{indent}  '{p}'" for p in web_paths)
    return f"[\n{lines},\n{indent}]"


def _to_pascal_case(file_stem: str, class_name: str) -> str:
    """Builds a wrapper component name, avoiding redundant repetition when the
    filename and class name overlap (the common case, e.g. file
    'proof_walkthrough.py' + class 'ProofWalkthrough' -> just 'ProofWalkthrough',
    not 'ProofWalkthroughProofWalkthrough'). Only prefixes with the file name
    when the class name doesn't already cover it, which also keeps multiple
    files that happen to define same-named scenes disambiguated."""
    file_words = [w for w in file_stem.replace("-", "_").split("_") if w]
    joined_file = "".join(w.lower() for w in file_words)

    if joined_file == class_name.lower():
        return class_name

    prefix = "".join(w[:1].upper() + w[1:] for w in file_words)
    return f"{prefix}{class_name}"


def write_wrapper_component(slug: str, web_paths: list[str], component_name: str) -> None:
    """Writes slides/components/generated/<ComponentName>.vue — a thin wrapper
    around ManimClip with `clips` baked in, so slides.md only ever needs a
    one-line tag instead of repeating the clip array."""
    clips_arr = _clips_literal(web_paths, indent="")

    content = f"""<!-- AUTO-GENERATED by scripts/build_assets.py — do not hand-edit. -->
<!-- Source scene: {slug} -->
<script setup lang="ts">
import ManimClip from '../ManimClip.vue'

defineProps<{{ autoStart?: boolean }}>()

const clips = {clips_arr}
</script>

<template>
  <ManimClip :clips="clips" :auto-start="autoStart ?? false" />
</template>
"""
    SLIDES_COMPONENTS_GENERATED.mkdir(parents=True, exist_ok=True)
    (SLIDES_COMPONENTS_GENERATED / f"{component_name}.vue").write_text(content, encoding="utf-8")


def build_snippet(slug: str, web_paths: list[str], component_name: str) -> str:
    """Returns the minimal copy-paste block for one scene: the one-line
    component call for each mode, plus the `clicks:` value you still need to
    set by hand in your slide's frontmatter (Slidev has no partial-content
    include, so this part can't be auto-inserted)."""
    n = len(web_paths)
    auto_clicks = max(n - 1, 0)
    manual_clicks = n

    return f"""## {slug} → <{component_name} /> ({n} clip{"s" if n != 1 else ""})

Auto-start — set `clicks: {auto_clicks}` in this slide's frontmatter, then:
```md
<{component_name} auto-start />
```

Wait for a click — set `clicks: {manual_clicks}` in this slide's frontmatter, then:
```md
<{component_name} />
```
"""


def write_snippets(scene_results: list[tuple[SceneRef, list[str]]]) -> None:
    """Writes one generated wrapper component + a minimal reference snippet
    per scene. Components go in slides/components/generated/ (auto-imported
    by Slidev like any other component). Snippets go in slides/snippets/ —
    not served publicly, just a copy-paste reminder of the tag + clicks value."""
    if SLIDES_COMPONENTS_GENERATED.exists():
        shutil.rmtree(SLIDES_COMPONENTS_GENERATED)

    snippets_dir = ROOT / "slides" / "snippets"
    if snippets_dir.exists():
        shutil.rmtree(snippets_dir)
    snippets_dir.mkdir(parents=True)

    aggregate_parts = ["# Slidev snippets (auto-generated — do not hand-edit)\n"]

    for scene, web_paths in scene_results:
        component_name = _to_pascal_case(scene.file.stem, scene.class_name)
        write_wrapper_component(scene.slug, web_paths, component_name)

        snippet = build_snippet(scene.slug, web_paths, component_name)
        (snippets_dir / f"{scene.slug}.md").write_text(snippet, encoding="utf-8")
        aggregate_parts.append(snippet)

    (snippets_dir / "SNIPPETS.md").write_text("\n---\n".join(aggregate_parts), encoding="utf-8")
    print(f"Wrote wrapper components: {SLIDES_COMPONENTS_GENERATED.relative_to(ROOT)}/ "
          f"({len(scene_results)} component(s))")
    print(f"Wrote snippets: {snippets_dir.relative_to(ROOT)}/ "
          f"({len(scene_results)} scene file(s) + SNIPPETS.md)")



# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # Windows' default console codepage (e.g. cp1252) can't encode the
    # unicode characters used in this script's output (→, —, ✓). Force
    # UTF-8 for stdout/stderr so printing never raises UnicodeEncodeError.
    # (Python 3.7+; no-op if already UTF-8, e.g. on macOS/Linux.)
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # pyright: ignore[reportAttributeAccessIssue]
        except (AttributeError, ValueError):
            pass

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--quality", choices=QUALITY_MAP.keys(), default="l",
        help="manim render quality: l=480p15 (fast, default), m=720p30, h=1080p60, k=2160p60",
    )
    parser.add_argument(
        "--scene", default=None,
        help="only render one scene, e.g. 'ProofWalkthrough' or 'proof_walkthrough.ProofWalkthrough'",
    )
    parser.add_argument(
        "--clean", action="store_true",
        help="remove slides/public/videos/ before building",
    )
    parser.add_argument(
        "--no-poster", action="store_true",
        help="skip rendering each scene's last-frame image (default: on)",
    )
    parser.add_argument(
        "--theme", choices=["dark", "light"], default="dark",
        help="color theme for the deck: dark (default) or light — passed to manim as PPIDC_THEME",
    )
    args = parser.parse_args()

    if args.clean and SLIDES_PUBLIC_VIDEOS.exists():
        print(f"Removing {SLIDES_PUBLIC_VIDEOS.relative_to(ROOT)}")
        shutil.rmtree(SLIDES_PUBLIC_VIDEOS)

    if not MANIM_SRC.exists():
        sys.exit(f"manim source not found at {MANIM_SRC}")

    scenes = discover_scenes(MANIM_SRC)
    scenes = filter_scenes(scenes, args.scene)

    if not scenes:
        sys.exit("No scenes found to render.")

    print("Discovered scenes:")
    for s in scenes:
        print(f"  - {s.file.relative_to(ROOT)}::{s.class_name}")
    print()

    quality_flag = QUALITY_MAP[args.quality][0]
    global_manifest: dict[str, list[str]] = {}
    scene_results: list[tuple[SceneRef, list[str]]] = []

    for scene in scenes:
        sections_dir = render_scene(scene, quality_flag, args.theme)
        web_paths = copy_clips(scene, sections_dir)
        global_manifest[scene.slug] = web_paths
        scene_results.append((scene, web_paths))
        print(f"  ✓ {scene.slug}: {len(web_paths)} clip(s) -> "
              f"{(SLIDES_PUBLIC_VIDEOS / scene.slug).relative_to(ROOT)}")

        if not args.no_poster:
            poster = render_poster(scene, quality_flag, args.theme)
            copy_poster(scene, poster)
            print(f"  ✓ {scene.slug}: poster -> "
                  f"{(SLIDES_PUBLIC_VIDEOS / scene.slug / 'poster.png').relative_to(ROOT)}")

    write_global_manifest(global_manifest)
    write_snippets(scene_results)
    print("\nDone.")


if __name__ == "__main__":
    main()
