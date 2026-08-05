<template>
  <section class="safe-video" :class="{ failed, loaded }" :aria-label="`${title}媒体播放器`">
    <video
      v-if="src && !failed"
      ref="video"
      :key="requestKey"
      :src="assetUrl(src)"
      :poster="assetUrl(poster)"
      controls
      preload="metadata"
      playsinline
      @loadeddata="handleLoaded"
      @error="handleError"
    >
      您的浏览器不支持 HTML5 视频播放。
    </video>
    <div v-else class="video-fallback">
      <SafeImage :src="poster" :alt="`${title}封面`" kind="culture" loading="eager" />
      <div>
        <el-icon><VideoCamera /></el-icon>
        <strong>{{ title }}</strong>
        <p>{{ message }}</p>
        <small>当前页面仍可继续阅读完整图文讲解。</small>
      </div>
    </div>
    <div v-if="src && !loaded && !failed" class="video-loading" role="status">正在准备媒体内容…</div>
    <el-button v-if="failed && src" type="primary" plain @click="retry">重新加载</el-button>
  </section>
</template>

<script setup>
import { onBeforeUnmount, ref, watch } from 'vue'
import { VideoCamera } from '@element-plus/icons-vue'
import { assetUrl } from '../api/http'
import SafeImage from './SafeImage.vue'

const props = defineProps({
  src: { type: String, default: '' },
  poster: { type: String, default: '' },
  title: { type: String, default: '影像资料' },
  message: { type: String, default: '当前条目使用本地图文动态微课；播放器不可用时仍可阅读完整内容。' },
  timeout: { type: Number, default: 15000 }
})
const emit = defineEmits(['load', 'error'])
const failed = ref(false)
const loaded = ref(false)
const video = ref(null)
const requestKey = ref(0)
let timeoutId = 0

function clearLoadTimeout() { window.clearTimeout(timeoutId) }
function armLoadTimeout() {
  clearLoadTimeout()
  if (props.src && props.timeout) timeoutId = window.setTimeout(handleError, props.timeout)
}
function handleLoaded() { clearLoadTimeout(); loaded.value = true; emit('load') }
function handleError() { clearLoadTimeout(); failed.value = true; loaded.value = false; emit('error') }
function retry() { failed.value = false; loaded.value = false; requestKey.value += 1; armLoadTimeout() }

watch(() => props.src, () => { failed.value = false; loaded.value = false; requestKey.value += 1; armLoadTimeout() }, { immediate: true })
onBeforeUnmount(clearLoadTimeout)
</script>

<style scoped>
.safe-video{position:relative;min-height:320px;overflow:hidden;background:#261014;border-radius:12px}.safe-video video{display:block;width:100%;aspect-ratio:16/9;background:#261014}.video-fallback{position:relative;min-height:320px}.video-fallback :deep(.safe-image){position:absolute;inset:0;width:100%;height:100%}.video-fallback>div{position:absolute;inset:0;display:grid;place-content:center;justify-items:center;padding:28px;text-align:center;color:#fff8e6;background:rgba(49,8,11,.68)}.video-fallback .el-icon{font-size:52px}.video-fallback strong{font-size:24px}.video-fallback p{max-width:580px;margin-bottom:8px;line-height:1.8}.video-fallback small{color:#f3d891}.video-loading{position:absolute;inset:0;display:grid;place-items:center;color:#fff8e6;background:linear-gradient(110deg,#31080b,#68141a,#31080b);background-size:200% 100%;animation:media-loading 1.4s infinite}.safe-video>.el-button{position:absolute;z-index:3;right:16px;bottom:16px}@keyframes media-loading{to{background-position:-200% 0}}@media(prefers-reduced-motion:reduce){.video-loading{animation:none}}
</style>
