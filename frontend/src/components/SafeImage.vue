<template>
  <figure
    class="safe-image"
    :class="[`kind-${kind}`, { loaded: loaded || failed, failed }]"
    :style="{ backgroundImage: `url(${resolvedFallback})` }"
  >
    <img
      v-if="!hideImage"
      :key="requestKey"
      :src="currentSrc"
      :alt="alt"
      :loading="loading"
      :style="{ objectFit: fit }"
      @load="handleLoad"
      @error="handleError"
    />
    <figcaption v-if="failed && showStatus" class="image-status" role="status">
      <span>原图未能加载，已显示本地备用图</span>
      <button type="button" @click.stop="retry">重试</button>
    </figcaption>
  </figure>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { FALLBACK_IMAGE, FALLBACK_IMAGES, assetUrl } from '../api/http'

const props = defineProps({
  src: { type: String, default: '' },
  alt: { type: String, default: '文化资源图片' },
  fit: { type: String, default: 'cover' },
  loading: { type: String, default: 'lazy' },
  fallback: { type: String, default: '' },
  kind: { type: String, default: 'default' },
  timeout: { type: Number, default: 12000 },
  showStatus: { type: Boolean, default: false }
})

const emit = defineEmits(['load', 'error'])
const currentSrc = ref('')
const loaded = ref(false)
const failed = ref(false)
const hideImage = ref(false)
const requestKey = ref(0)
const originalSrc = computed(() => assetUrl(props.src))
const resolvedFallback = computed(() => {
  const selected = props.fallback || FALLBACK_IMAGES[props.kind] || FALLBACK_IMAGE
  return assetUrl(selected) || FALLBACK_IMAGE
})
let timeoutId = 0

function clearLoadTimeout() {
  window.clearTimeout(timeoutId)
  timeoutId = 0
}

function armLoadTimeout() {
  clearLoadTimeout()
  if (!props.timeout || !currentSrc.value || currentSrc.value === resolvedFallback.value) return
  timeoutId = window.setTimeout(handleError, props.timeout)
}

function reset() {
  clearLoadTimeout()
  currentSrc.value = originalSrc.value || resolvedFallback.value
  loaded.value = false
  failed.value = !originalSrc.value
  hideImage.value = false
  requestKey.value += 1
  armLoadTimeout()
}

function handleLoad() {
  clearLoadTimeout()
  loaded.value = true
  emit('load', currentSrc.value)
}

function handleError() {
  clearLoadTimeout()
  if (currentSrc.value !== resolvedFallback.value) {
    currentSrc.value = resolvedFallback.value
    failed.value = true
    requestKey.value += 1
    emit('error', originalSrc.value)
    return
  }
  hideImage.value = true
  failed.value = true
  emit('error', originalSrc.value)
}

function retry() {
  reset()
}

watch(() => [props.src, props.fallback, props.kind], reset, { immediate: true })
onBeforeUnmount(clearLoadTimeout)
</script>

<style scoped>
.safe-image { position:relative;width:100%;height:100%;min-height:inherit;margin:0;overflow:hidden;background-color:#eee4d6;background-position:center;background-size:cover; }
.safe-image.kind-culture,.safe-image.kind-people{background-color:#5b171b}.safe-image.kind-team,.safe-image.kind-research,.safe-image.kind-news{background-color:#dce9ed}.safe-image.kind-scenery{background-color:#dce7dc}
.safe-image::after { position:absolute;inset:0;background:linear-gradient(105deg,transparent 25%,rgba(255,255,255,.38) 45%,transparent 65%);background-size:220% 100%;animation:image-loading 1.25s ease-in-out infinite;pointer-events:none;content:""; }
.safe-image.loaded::after { display:none; }
.safe-image img { position:absolute;inset:0;display:block;width:100%;height:100%;min-height:inherit; }
.image-status { position:absolute;z-index:2;right:10px;bottom:10px;display:flex;align-items:center;gap:8px;max-width:calc(100% - 20px);padding:7px 9px;color:#fff;background:rgba(49,8,11,.82);border-radius:7px;font-size:12px; }
.image-status button { flex:none;padding:3px 7px;color:#fff8e6;background:transparent;border:1px solid rgba(255,255,255,.55);border-radius:5px;cursor:pointer; }
@keyframes image-loading { from{background-position:180% 0}to{background-position:-80% 0} }
@media(prefers-reduced-motion:reduce){.safe-image::after{animation:none}}
</style>
