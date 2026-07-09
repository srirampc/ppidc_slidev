<!-- components/ManimClip.vue -->
<script setup lang="ts">
import { ref, watch } from 'vue'
import { onSlideEnter, onSlideLeave } from '@slidev/client'

const props = withDefaults(
  defineProps<{
    clips: string[]
    autoStart?: boolean   // true: plays immediately on slide enter
                           // false (default): first click starts playback
  }>(),
  { autoStart: false }
)

const videoEl = ref<HTMLVideoElement>()
const started = ref(false)

// In autoStart mode, click n -> clip n (clip 0 plays as soon as the slide is entered).
// In manual mode, click 0 = nothing yet, click 1 -> clip 0, click 2 -> clip 1, etc.
// (i.e. manual mode "spends" one click just starting the sequence.)
function clipIndexForClick(n: number): number {
  const raw = props.autoStart ? n : n - 1
  return Math.max(0, Math.min(raw, props.clips.length - 1))
}

function playClip(n: number) {
  if (!props.autoStart && n <= 0) {
    started.value = false
    return
  }
  started.value = true
  const clip = props.clips[clipIndexForClick(n)]
  if (!videoEl.value) return
  if (!videoEl.value.currentSrc.endsWith(clip)) {
    videoEl.value.src = clip
  }
  videoEl.value.currentTime = 0
  videoEl.value.play()
}

onSlideEnter(() => {
  playClip($clicksContext.current)
})

onSlideLeave(() => {
  videoEl.value?.pause()
})

watch(() => $clicksContext.current, (n) => playClip(n))
</script>

<template>
  <video ref="videoEl" v-show="started" muted playsinline />
</template>
<!--
<script setup lang="ts">
import { ref, watch } from 'vue'
import { useNav } from '@slidev/client'

const props = defineProps<{ clips: string[] }>()
const videoEl = ref<HTMLVideoElement>()

watch(
  () => $clicksContext.current,
  (n) => {
    const clip = props.clips[Math.min(n, props.clips.length - 1)]
    if (!videoEl.value) return
    if (videoEl.value.currentSrc.endsWith(clip)) return
    videoEl.value.src = clip
    videoEl.value.play()
  }
)
</script>

<template>
  <video ref="videoEl" :src="clips[0]" autoplay />
</template>
-->
