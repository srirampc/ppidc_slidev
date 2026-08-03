<!-- components/ManimClip.vue -->
<script setup lang="ts">
import { ref, watch } from 'vue'
import { useNav, onSlideEnter, onSlideLeave } from '@slidev/client'

const props = withDefaults(
  defineProps<{ clips: string[]; autoStart?: boolean }>(),
  { autoStart: false }
)

const { clicks } = useNav()

const videoA = ref<HTMLVideoElement>()
const videoB = ref<HTMLVideoElement>()
const activeIsA = ref(true)
let currentIndex = -1

function activeEl() { return activeIsA.value ? videoA.value : videoB.value }
function inactiveEl() { return activeIsA.value ? videoB.value : videoA.value }

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
  if (!nextEl || !curEl) return

  nextEl.src = clip

  // Wait for a real decoded frame before revealing it — this is the part
  // that actually kills the flicker, not just having two elements.
  await new Promise<void>((resolve) => {
    const onReady = () => {
      nextEl.removeEventListener('loaded_data', onReady)
      resolve()
    }
    nextEl.addEventListener('loaded_data', onReady)
    nextEl.load()
  })

  await nextEl.play().catch(() => {})
  activeIsA.value = !activeIsA.value
  curEl.pause()
}

function playForClick(n: number) {
  if (!props.autoStart && n <= 0) {
    currentIndex = -1
    return
  }
  showClip(clipIndexForClick(n))
}

onSlideEnter(() => playForClick(clicks.value))
onSlideLeave(() => { videoA.value?.pause(); videoB.value?.pause() })

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
}
.manim-clip-wrapper video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  display: block;
}
.manim-clip-wrapper video.back {
  opacity: 0;
  z-index: 0;
}
.manim-clip-wrapper video:not(.back) {
  opacity: 1;
  z-index: 1;
}
</style>
