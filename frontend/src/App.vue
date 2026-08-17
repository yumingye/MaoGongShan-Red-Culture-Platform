<template>
  <div class="app-layout">
    <a class="skip-link" href="#main-content">跳至主要内容</a>
    <div class="scroll-progress" :style="{ transform: `scaleX(${scrollProgress})` }" aria-hidden="true"></div>
    <SiteHeader />
    <div id="main-content" class="app-main" tabindex="-1">
      <el-alert
        v-if="runtimeError"
        class="runtime-alert"
        title="页面局部内容发生异常"
        :description="runtimeError"
        type="error"
        show-icon
        :closable="false"
        @close="runtimeError = ''"
      >
        <template #default>
          <div class="runtime-actions">
            <span>{{ runtimeError }}</span>
            <el-button size="small" @click="reloadPage">重新加载</el-button>
            <el-button size="small" plain @click="goHome">返回首页</el-button>
            <el-button size="small" text @click="runtimeError = ''">关闭提示</el-button>
          </div>
        </template>
      </el-alert>
      <RouterView v-slot="{ Component, route }">
        <PageErrorBoundary v-if="Component" :key="route.fullPath">
          <component :is="Component" :key="route.fullPath" />
        </PageErrorBoundary>
        <section v-else class="route-loading-state" role="status" aria-live="polite">
          <span class="route-loading-state__mark" aria-hidden="true"></span>
          <div>
            <strong>正在载入数字文化内容</strong>
            <p>页面资源正在安全加载，导航与页脚仍可正常使用，请稍候。</p>
          </div>
        </section>
      </RouterView>
    </div>
    <SiteFooter />
    <el-backtop :right="24" :bottom="24" />
  </div>
</template>

<script setup>
import { onBeforeUnmount, onErrorCaptured, onMounted, ref } from 'vue'
import SiteHeader from './components/SiteHeader.vue'
import SiteFooter from './components/SiteFooter.vue'
import PageErrorBoundary from './components/PageErrorBoundary.vue'
import { setupRevealObserver } from './utils/reveal'

const runtimeError = ref('')
const scrollProgress = ref(0)
let stopReveal = () => {}

function describeError(error) {
  return error?.message || '该模块未能正常渲染，其他页面仍可继续访问。'
}

function handleWindowError(event) {
  runtimeError.value = describeError(event.error)
}

function handlePromiseError(event) {
  runtimeError.value = describeError(event.reason)
}

function updateScrollProgress() {
  const total = document.documentElement.scrollHeight - window.innerHeight
  scrollProgress.value = total > 0 ? Math.min(1, window.scrollY / total) : 0
}

function reloadPage() { window.location.reload() }
function goHome() { window.location.assign('/') }

onErrorCaptured((error) => {
  runtimeError.value = describeError(error)
  return false
})

onMounted(() => {
  window.addEventListener('error', handleWindowError)
  window.addEventListener('unhandledrejection', handlePromiseError)
  window.addEventListener('scroll', updateScrollProgress, { passive: true })
  stopReveal = setupRevealObserver()
})

onBeforeUnmount(() => {
  window.removeEventListener('error', handleWindowError)
  window.removeEventListener('unhandledrejection', handlePromiseError)
  window.removeEventListener('scroll', updateScrollProgress)
  stopReveal()
})
</script>

<style>
.skip-link {
  position: fixed;
  z-index: 120;
  top: 8px;
  left: 12px;
  padding: 10px 14px;
  color: #fff;
  background: #7f1d1d;
  border-radius: 6px;
  transform: translateY(-160%);
  transition: transform .16s ease;
}
.skip-link:focus { transform: translateY(0); }
.scroll-progress {
  position: fixed;
  z-index: 100;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, var(--gold), #d92832, var(--gold-soft));
  transform-origin: left;
  transition: transform .08s linear;
}
.runtime-alert {
  position: relative;
  z-index: 40;
  width: min(1180px, calc(100% - 32px));
  margin: 16px auto 0;
}
.runtime-actions { display:flex;flex-wrap:wrap;align-items:center;gap:8px; }
.runtime-actions span { flex:1;min-width:220px; }
.route-loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  width: min(1180px, calc(100% - 32px));
  min-height: 360px;
  margin: 24px auto;
  color: #4f2726;
  background: #fffaf0;
  border: 1px solid rgba(139, 30, 36, .16);
  border-radius: 8px;
}
.route-loading-state__mark {
  width: 36px;
  height: 36px;
  border: 3px solid rgba(139, 30, 36, .18);
  border-top-color: #8b1e24;
  border-radius: 50%;
  animation: route-loading-spin .8s linear infinite;
}
.route-loading-state strong { display: block; margin-bottom: 6px; }
.route-loading-state p { margin: 0; color: #735f5b; }
@keyframes route-loading-spin { to { transform: rotate(360deg); } }
@media (prefers-reduced-motion: reduce) {
  .route-loading-state__mark { animation: none; }
}

</style>
