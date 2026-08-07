<script setup lang="ts">
import { ref, watch } from 'vue'
import { useNav, onSlideEnter, onSlideLeave } from '@slidev/client'

/**
 * Plays a sequence of Manim section clips, synced to Slidev's click state.
 *
 * Modes:
 *  - auto-start: clip 0 plays the moment the slide is entered.
 *                clicks: in frontmatter = clips.length - 1
 *  - manual (default): nothing plays until the first click.
 *                clicks: in frontmatter = clips.length
 *
 * Usage (typically via a generated wrapper component that bakes in `clips`):
 *   <ManimClip :clips="[...]" auto-start />
 *   <ManimClip :clips="[...]" />
 */

const props = withDefaults(
  defineProps<{
    clips: string[]
    autoStart?: boolean
  }>(),
  { autoStart: false }
)

// current slide's click count, as a reactive ComputedRef<number>
const { clicks } = useNav()

// Two <video> elements, double-buffered: the next clip is preloaded into
// the inactive one and only swapped in once it has a real decoded frame,
// so the visible element is never touched mid-display. This is what
// eliminates the blank-frame flicker on clip transitions.
const videoA = ref<HTMLVideoElement>()
const videoB = ref<HTMLVideoElement>()
const activeIsA = ref(true)
let currentIndex = -1

function activeEl() {
  return activeIsA.value ? videoA.value : videoB.value
}
function inactiveEl() {
  return activeIsA.value ? videoB.value : videoA.value
}

function clipIndexForClick(n: number): number {
  const raw = props.autoStart ? n : n - 1
  return Math.max(0, Math.min(raw, props.clips.length - 1))
}

async function showClip(index: number) {
  if (index === currentIndex) return
  currentIndex = index

  const clip = props.clips[index]
  const nextEl = inactiveEl()
  const curEl = activeEl()
  if (!nextEl || !curEl || !clip) return

  nextEl.src = clip

  // Wait for a real decoded frame before revealing it — the actual fix for
  // the flicker, not just having two elements.
  await new Promise<void>((resolve) => {
    const onReady = () => {
      nextEl.removeEventListener('loadeddata', onReady)
      resolve()
    }
    nextEl.addEventListener('loadeddata', onReady)
    nextEl.load()
  })

  await nextEl.play().catch(() => {
    // autoplay can still be blocked in some contexts even when muted;
    // fail silently rather than throwing during slide navigation
  })

  activeIsA.value = !activeIsA.value
  curEl.pause()
}

function playForClick(n: number) {
  if (!props.autoStart && n <= 0) {
    // manual mode, no click yet: nothing should be playing
    currentIndex = -1
    return
  }
  showClip(clipIndexForClick(n))
}

// Slidev keeps every slide's component instance mounted for the whole deck
// (for fast prev/next navigation), so `autoplay` fires at mount time, not
// at slide-entry time — using it here would mean the clip already finished
// playing offscreen before you ever navigate to the slide. Driving playback
// from onSlideEnter/onSlideLeave instead fixes that, and also handles
// re-entering the slide from a later one (clicks may already be > 0).
onSlideEnter(() => playForClick(clicks.value))
onSlideLeave(() => {
  videoA.value?.pause()
  videoB.value?.pause()
})

watch(clicks, (n) => playForClick(n))
</script>

<template>
  <div class="manim-clip-wrapper">
    <video ref="videoA" muted playsinline preload="auto" :class="{ back: !activeIsA }" />
    <video ref="videoB" muted playsinline preload="auto" :class="{ back: activeIsA }" />
  </div>
</template>

<style scoped>
.manim-clip-wrapper {
  position: relative;
  width: 100%;
  /* Both videos are position: absolute below, which removes them from
     normal document flow and contributes zero height to this wrapper.
     Without an explicit aspect-ratio the wrapper collapses to 0px and
     the slide renders blank. Match this to how the scene was rendered
     (Manim's default is 16/9) — override per-instance with a style prop
     if a scene uses a different resolution. */
  aspect-ratio: 16 / 9;
}

.manim-clip-wrapper video {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}

/* opacity, not display:none — some browsers (Safari especially)
   deprioritize decoding for display:none elements as if backgrounded,
   which stalls the preload of the inactive video. */
.manim-clip-wrapper video.back {
  opacity: 0;
  z-index: 0;
}

.manim-clip-wrapper video:not(.back) {
  opacity: 1;
  z-index: 1;
}
</style>
