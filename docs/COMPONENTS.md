# Manim ↔ Slidev video integration

How rendered Manim clips get from `ppidc/` into a click-synced, flicker-free
video inside a Slidev deck, and every issue we hit getting there.

## Why not manim-slides' reveal.js export

`manim-slides convert --to html` bundles its own reveal.js player — its own
click/pause logic, its own styling — with no supported path into Slidev's
markdown format. Instead we render **plain Manim scenes** to video and let
Slidev own all slide authoring and pacing.

## Why not one video per scene

`manim-slides`' `next_slide()`-style pausing is built on a native Manim
feature: **sections**. Calling `self.next_section("label")` inside a
`construct()` checkpoints the render — one continuous scene becomes several
video files, each picking up visually exactly where the previous one ended.
`scripts/build_assets.py` renders every scene with `--save_sections` and
reads Manim's own `<SceneName>.json` manifest to get the ordered clip list,
rather than assuming filenames.

## The build pipeline (`scripts/build_assets.py`)

1. **Discovers** `Scene` subclasses under `ppidc/` via `ast` parsing (no
   import needed just to enumerate scenes).
2. **Renders** each with `uv run manim render --save_sections`.
3. **Copies** the resulting clips into `slides/public/videos/<slug>/`,
   alongside a per-scene `clips.json` and a global `manifest.json`.
4. **Generates a wrapper component** per scene in
   `slides/components/generated/<ComponentName>.vue` — a thin shim around
   `ManimClip.vue` with that scene's `clips` array baked in, so `slides.md`
   only ever needs a one-line tag:
    ```md
    <ProofWalkthrough auto-start />
    ```
    instead of repeating the clip array inline. Component names dedupe the
    common file/class overlap (`proof_walkthrough.py` + `ProofWalkthrough` →
    just `ProofWalkthrough`), and disambiguate when they genuinely differ
    (`diagram.py` + `ForceDiagram` → `DiagramForceDiagram`).
5. **Writes reference snippets** to `slides/snippets/` — the one thing that
   _can't_ be auto-inserted into `slides.md` is the `clicks:` frontmatter
   value, since Slidev has no partial-content include mechanism (`src:`
   frontmatter imports a whole slide, not a fragment spliced into one you're
   already writing). The snippet spells out the exact number for both usage
   modes so it can't drift out of sync with the clip count.

## `ManimClip.vue` — two playback modes

A slide with an animation sometimes needs a beat of prose before the
animation starts, and sometimes should just start immediately. `autoStart`
picks between them:

- **`auto-start`** — clip 0 plays the moment the slide is entered.
  `clicks:` in frontmatter = `clips.length - 1`.
- **default (manual)** — nothing plays until the first click.
  `clicks:` in frontmatter = `clips.length` (the first click "spends" a
  click just starting the sequence).

## `ManimClip.vue` — double-buffered playback (no flicker)

Setting `videoEl.src` on a single `<video>` element blanks the frame while
the browser fetches/decodes the new source — a visible flash on every clip
transition. The fix is to keep **two** `<video>` elements, preload the next
clip into the _inactive_ one, wait for a real decoded frame
(`loadeddata` event — not just calling `.load()`), then swap visibility and
pause the old element. The now-visible element is never touched while it's
on screen, so there's nothing to blank.

Layout requirements this depends on:

- both `<video>`s are `position: absolute` inside a `position: relative`
  wrapper, stacked via `opacity`/`z-index` — **not** `display: none` for the
  inactive one, since some browsers (Safari especially) deprioritize
  decoding for display-none elements as if backgrounded, stalling the
  preload.
- the wrapper needs an explicit `aspect-ratio` (matching however the scene
  was rendered — Manim's default is `16 / 9`). Both videos being
  `position: absolute` removes them from normal flow, so without an
  explicit ratio the wrapper collapses to zero height — this reads as a
  **blank slide**, not a flicker, and was exactly the failure mode when the
  aspect-ratio was missing.

## Driving playback from Slidev's click state

**Don't rely on the `autoplay` attribute.** Slidev keeps every slide's
component instance mounted for the whole deck (for fast prev/next
navigation) rather than mounting on entry — so `autoplay` fires the moment
the component mounts, which can be long before the slide is actually on
screen. By the time you navigate to it, the clip already played through in
the background and is sitting on its last frame, which looks identical to
"never played."

Correct approach: use Slidev's slide-lifecycle hooks instead of `autoplay`
or `onMounted`/`onUnmounted` (the docs explicitly warn against the latter
for this exact reason — the instance persists across the whole deck):

```ts
import { onSlideEnter, onSlideLeave, useNav } from "@slidev/client";

const { clicks } = useNav(); // ComputedRef<number>, current slide's click count

onSlideEnter(() => playForClick(clicks.value)); // covers both forward AND backward navigation
onSlideLeave(() => {
    /* pause */
});

watch(clicks, (n) => playForClick(n));
```

### A dead end worth documenting: `$clicksContext`

An earlier draft tried `const { $clicksContext } = useNav()`. Two failures,
in order:

1. **`Identifier '$clicksContext' has already been declared'`** — Slidev's
   Vite transform auto-injects certain `$`-prefixed globals (`$slidev`,
   `$page`, `$clicksContext` in older drafts, etc.) directly into every
   `<script setup>`. Destructuring another binding of the same name is a
   duplicate `const`.
2. **After removing the destructure and using the injected global directly,
   editors (Zed, in our case) still flagged `Property '$clicksContext' does
not exist on type 'SlidevContextNavFull'`** — correctly, because it
   doesn't. Checking Slidev's actual source
   (`packages/client/composables/useNav.ts`), `useNav()`'s real return type
   exposes `clicksContext` (a `ComputedRef<ClicksContext>`, with `.current`)
   and, more simply, **`clicks`** — an already-unwrapped
   `ComputedRef<number>` that's exactly what playback logic needs. The
   `$`-prefixed globals (`$nav`, `$clicks`, `$page`, `$slidev`) are a
   _separate_, template/markdown-only injection mechanism — not the same
   namespace as what `useNav()` returns. Mixing the two conventions is what
   caused both errors.

**Fix:** use `const { clicks } = useNav()` and pass `clicks.value` /
`clicks` (as a ref) directly — no `$`, no `.current`, no destructuring
collision, and it type-checks cleanly in any editor.

## Windows: `UnicodeEncodeError` in `build_assets.py`

`Path.write_text()` without an explicit encoding uses the OS's default
locale encoding — `cp1252` on most Windows setups, not UTF-8. The script's
generated output uses `→`, `—`, `✓` in snippet/manifest content and console
messages, none of which exist in `cp1252`, so writes (and `print()` calls)
raised `UnicodeEncodeError`. Never surfaced on macOS/Linux because their
default locale encoding is already UTF-8.

Fixed by:

- passing `encoding="utf-8"` explicitly on every `Path.write_text()` call
- reconfiguring `sys.stdout`/`sys.stderr` to UTF-8 at the top of `main()`
  (`stream.reconfigure(encoding="utf-8", errors="replace")`, Python 3.7+)

**Going forward:** any new file-writing code added to this project should
pass `encoding="utf-8"` explicitly rather than leaving it implicit — it
works silently on Mac/Linux dev machines and only breaks on Windows, making
it an easy regression to miss without testing there directly.

## Troubleshooting

| Symptom                                                                     | Cause                                                                                    | Fix                                                                             |
| --------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `[vue/compiler-sfc] Unexpected token`                                       | `<script setup>` uses TS generics (`defineProps<...>()`) without `lang="ts"`             | add `lang="ts"` to the script tag                                               |
| `Identifier '$clicksContext' has already been declared`                     | destructuring a name Slidev already auto-injects                                         | don't destructure it — or alias it, or (better) use `useNav().clicks` instead   |
| Video doesn't autoplay until the first click                                | Slidev keeps components mounted deck-wide; `autoplay` fires at mount, not at slide-entry | drive playback from `onSlideEnter`/`onSlideLeave`, not the `autoplay` attribute |
| Flicker when switching clips                                                | single `<video>` blanks its frame when `.src` changes                                    | double-buffer with two `<video>` elements, swap on `loadeddata`                 |
| Slide goes blank after adding double-buffering                              | both `<video>`s are `position: absolute`, contribute no height to the wrapper            | give the wrapper an explicit `aspect-ratio`                                     |
| `Property '$clicksContext' does not exist on type 'SlidevContextNavFull'`   | that property genuinely isn't on the real return type                                    | use `const { clicks } = useNav()`                                               |
| `UnicodeEncodeError: 'charmap' codec can't encode character` (Windows only) | `write_text()`/`print()` defaulting to `cp1252`                                          | pass `encoding="utf-8"` explicitly everywhere; reconfigure stdout to UTF-8      |
