<template>
  <section ref="story" class="motion-story" :class="{ paused: !playing }" aria-label="动态图文微课" @keydown="handleKeydown">
    <SafeImage
      v-for="(frame, index) in frames"
      :key="frame"
      :src="frame"
      :alt="`${title}画面${index + 1}`"
      class="motion-frame"
      :style="frameStyle(index)"
    />
    <div class="motion-shade"></div>
    <div class="motion-copy" aria-live="polite">
      <span>本地图文动态微课 · {{ frameTypes[activeFrame] || '媒体资料' }}</span>
      <h2>{{ title }}</h2>
      <p>{{ captions[activeCaption] || '通过来源清晰的本地图片与字幕组织学习内容。' }}</p>
    </div>
    <div class="motion-toolbar">
      <button type="button" :aria-label="playing ? '暂停动态演示' : '继续动态演示'" @click="toggle">
        <el-icon><VideoPause v-if="playing" /><VideoPlay v-else /></el-icon>
        {{ playing ? '暂停' : '播放' }}
      </button>
      <button type="button" aria-label="切换播放速度" @click="cycleSpeed">{{ speed }}×</button>
      <button type="button" aria-label="全屏查看" @click="toggleFullscreen">
        <el-icon><FullScreen /></el-icon>
        全屏
      </button>
    </div>
    <div class="motion-dots" aria-label="切换画面">
      <button v-for="(_, index) in frames" :key="index" type="button" :class="{ active: activeFrame === index }" :aria-label="`查看第${index + 1}幅画面`" @click="goTo(index)"></button>
    </div>
    <div class="motion-progress" aria-hidden="true"><i :style="{ transform: `scaleX(${progress})` }"></i></div>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { FullScreen, VideoPause, VideoPlay } from '@element-plus/icons-vue'
import SafeImage from './SafeImage.vue'

const props = defineProps({ title: String, frames: { type: Array, default: () => [] }, captions: { type: Array, default: () => [] }, frameTypes: { type: Array, default: () => [] } })
const story = ref(null)
const playing = ref(true)
const cursor = ref(0)
const elapsed = ref(0)
const speed = ref(1)
const progress = computed(() => Math.min(1, elapsed.value / frameDuration.value))
const frameDuration = computed(() => 4200 / speed.value)
const activeFrame = computed(() => props.frames.length ? cursor.value % props.frames.length : 0)
const activeCaption = computed(() => props.captions.length ? cursor.value % props.captions.length : 0)
let animationFrame = 0
let previousTime = 0

function tick(time) {
  if (!previousTime) previousTime = time
  if (playing.value) {
    elapsed.value += time - previousTime
    if (elapsed.value >= frameDuration.value) {
      elapsed.value = 0
      cursor.value += 1
    }
  }
  previousTime = time
  animationFrame = window.requestAnimationFrame(tick)
}
function frameStyle(index) { return { opacity: activeFrame.value === index ? 1 : 0, transform: activeFrame.value === index ? 'scale(1.08)' : 'scale(1)' } }
function toggle() { playing.value = !playing.value }
function goTo(index) { cursor.value = index; elapsed.value = 0 }
function cycleSpeed() { speed.value = speed.value === 1 ? 1.25 : speed.value === 1.25 ? .75 : 1; elapsed.value = 0 }
async function toggleFullscreen() {
  if (!document.fullscreenElement) await story.value?.requestFullscreen?.()
  else await document.exitFullscreen?.()
}
function handleKeydown(event) {
  if (event.code === 'Space') { event.preventDefault(); toggle() }
  if (event.key === 'ArrowRight') goTo((activeFrame.value + 1) % Math.max(props.frames.length, 1))
  if (event.key === 'ArrowLeft') goTo((activeFrame.value - 1 + Math.max(props.frames.length, 1)) % Math.max(props.frames.length, 1))
}

onMounted(() => { story.value?.setAttribute('tabindex', '0'); animationFrame = window.requestAnimationFrame(tick) })
onBeforeUnmount(() => window.cancelAnimationFrame(animationFrame))
</script>

<style scoped>
.motion-story{position:relative;min-height:clamp(360px,56vw,620px);overflow:hidden;color:#fff8e6;background:#31080b;border-radius:14px;isolation:isolate}.motion-story:focus-visible{outline:3px solid var(--gold-soft);outline-offset:3px}.motion-frame{position:absolute;inset:-4%;width:108%;height:108%;transition:opacity .85s ease,transform 5s linear}.motion-shade{position:absolute;inset:0;z-index:2;background:linear-gradient(90deg,rgba(25,5,7,.92),rgba(49,8,11,.36) 65%,rgba(0,0,0,.08))}.motion-copy{position:absolute;z-index:3;left:clamp(22px,6vw,72px);bottom:clamp(78px,12vw,126px);max-width:680px}.motion-copy span{color:var(--gold-soft);font-weight:800}.motion-copy h2{margin:8px 0;font-size:clamp(30px,5vw,60px)}.motion-copy p{line-height:1.9;font-size:clamp(15px,2vw,19px)}.motion-toolbar{position:absolute;z-index:4;right:20px;bottom:20px;display:flex;gap:8px}.motion-toolbar button{display:flex;align-items:center;gap:6px;padding:9px 12px;color:#fff;background:rgba(49,8,11,.76);border:1px solid rgba(255,255,255,.45);border-radius:999px;cursor:pointer}.motion-dots{position:absolute;z-index:4;left:clamp(22px,6vw,72px);bottom:26px;display:flex;gap:8px}.motion-dots button{width:10px;height:10px;padding:0;background:rgba(255,255,255,.48);border:0;border-radius:50%;cursor:pointer;transition:width .2s}.motion-dots button.active{width:30px;background:var(--gold-soft);border-radius:999px}.motion-progress{position:absolute;z-index:4;left:0;right:0;bottom:0;height:4px;background:rgba(255,255,255,.2)}.motion-progress i{display:block;width:100%;height:100%;background:var(--gold-soft);transform-origin:left;transition:transform .08s linear}@media(max-width:640px){.motion-toolbar{left:18px;right:auto}.motion-toolbar button:last-child{display:none}.motion-dots{left:auto;right:18px}}@media(prefers-reduced-motion:reduce){.motion-frame{transition:opacity .1s}.motion-progress{display:none}}
</style>
