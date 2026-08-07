# Presentation with [Slidev](https://github.com/slidevjs/slidev)!

This is a standalone [Slidev](https://sli.dev) project (its own Node/pnpm
toolchain, independent of the root `uv`-managed Python project). It authors
and presents the deck; it does not render any animations itself — those come
from `../ppidc/` via `../scripts/build_assets.py`.

See the root [`README.md`](../README.md) for the full build workflow and
[`../docs/COMPONENTS.md`](../docs/COMPONENTS.md) for how the Manim video
integration works.

## Install

```bash
pnpm install
```

## Commands

| Command        | What it does                                                              |
| -------------- | ------------------------------------------------------------------------- |
| `pnpm dev`     | Dev server with hot reload at `http://localhost:3030`                     |
| `pnpm build`   | Static build to `dist/` (any static HTTP server can host it)              |
| `pnpm preview` | Serves the `dist/` build locally, to sanity-check before deploying        |
| `pnpm export`  | Exports to PDF/PNG/PPTX (requires `playwright-chromium`, see Slidev docs) |

## Directory notes

- **`slides.md`** — the deck itself. Component tags for animated slides come
  from `slides/snippets/SNIPPETS.md` (generated — check there for the exact
  tag + required `clicks:` value per scene before pasting into a slide).
- **`components/generated/`** — one wrapper component per Manim scene,
  fully regenerated on every `build_assets.py` run. Don't hand-edit these;
  edit the source scene in `../ppidc/` instead and rebuild.
- **`components/ManimClip.vue`** — the actual video player all generated
  wrapper components delegate to (double-buffered, click-synced). This one
  _is_ hand-maintained — see `../docs/COMPONENTS.md` for its design.
- **`public/videos/`** — rendered clips + `manifest.json`. Generated;
  gitignore-friendly if you'd rather rebuild than commit binary video
  assets.
- **`ext/`** — the deck's theme.
- **`pages/`** — supplementary slide content pulled in via Slidev's
  multi-file `src:` imports, if the deck is split across files.

## Fast iteration with watchers

When iterating on Manim animations, you don't have to run `build_assets.py` manually after every edit.

- **Animation-only:** from the project root,
  run `uv run --group dev python scripts/watch_scene.py <SceneName>`.
  It re-renders that scene on every save and prints the output path.
- **Full deck:** run `uv run --group dev python scripts/watch_assets.py`
  in one terminal, and `cd slides && pnpm dev` in another. The deck
  hot-reloads after each asset rebuild.


## Hosting the built deck

`pnpm build` produces a static SPA. Any static file server works, with two
requirements:

- **SPA fallback routing** — unknown paths must serve `index.html` (e.g.
  nginx's `try_files $uri $uri/ /index.html;`), since slide navigation is
  client-side routed.
- **`--base`** — if hosted under a subpath rather than the domain root, build
  with `pnpm build --base /your-subpath/` so asset URLs resolve correctly.

`netlify.toml` / `vercel.json` in this directory already configure this for
those two platforms.
