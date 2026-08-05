<template>
  <section v-if="errorMessage" class="page-error" role="alert">
    <div class="page-error-mark" aria-hidden="true">!</div>
    <p class="eyebrow">页面局部异常</p>
    <h1>这一页暂时没有完成渲染</h1>
    <p>{{ errorMessage }}</p>
    <div class="page-error-actions">
      <el-button type="primary" @click="retry">重新加载本页</el-button>
      <el-button plain @click="router.push('/')">返回首页</el-button>
    </div>
  </section>
  <div v-else :key="renderKey">
    <slot />
  </div>
</template>

<script setup>
import { onErrorCaptured, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const errorMessage = ref('')
const renderKey = ref(0)

onErrorCaptured((error) => {
  errorMessage.value = error?.message || '页面中的一个模块发生异常，导航和其他栏目仍可继续使用。'
  return false
})

watch(() => route.fullPath, () => {
  errorMessage.value = ''
  renderKey.value += 1
})

function retry() {
  errorMessage.value = ''
  renderKey.value += 1
}
</script>

<style scoped>
.page-error {
  width: min(880px, calc(100% - 32px));
  min-height: 420px;
  display: grid;
  align-content: center;
  justify-items: start;
  gap: 12px;
  margin: 40px auto;
  padding: clamp(28px, 6vw, 64px);
  color: #3c3030;
  background: #fffaf0;
  border: 1px solid #e2d0b5;
  border-left: 6px solid var(--red);
  box-shadow: var(--shadow);
}
.page-error-mark {
  width: 54px;
  height: 54px;
  display: grid;
  place-items: center;
  color: #fff8e6;
  background: var(--red);
  border-radius: 50%;
  font-size: 30px;
  font-weight: 900;
}
.page-error h1 { margin: 0; color: var(--red-dark); font-size: clamp(28px, 5vw, 44px); }
.page-error p { max-width: 680px; margin: 0; line-height: 1.8; }
.page-error-actions { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 12px; }
</style>
