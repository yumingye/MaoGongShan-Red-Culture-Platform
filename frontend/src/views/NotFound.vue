<template>
  <main class="page not-found">
    <div class="panel">
      <span class="error-code" aria-hidden="true">404</span>
      <h1>页面未找到</h1>
      <p>资源库没有这个地址。你可以返回首页，或使用顶部搜索查找历史、图片、路线和数字资源。</p>
      <div class="actions">
        <el-button type="primary" @click="router.push('/')">返回首页</el-button>
        <el-button plain @click="goBack">返回上一页</el-button>
        <el-button plain @click="router.push('/search')">进入搜索</el-button>
      </div>
    </div>
  </main>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
function goBack() {
  if (window.history.length > 1) router.back()
  else router.push('/')
}
</script>

<style scoped>
.not-found {
  display: grid;
  place-items: center;
  min-height: 70vh;
}

.panel {
  position: relative;
  overflow: hidden;
  max-width: 680px;
  padding: 36px;
  text-align: center;
}

.error-code {
  display: block;
  color: rgba(143, 29, 34, .09);
  font-family: Georgia, 'Times New Roman', serif;
  font-size: clamp(96px, 18vw, 180px);
  font-weight: 900;
  line-height: .82;
}
h1 {
  margin-top: -18px;
  color: var(--red-dark);
  font-size: clamp(34px, 7vw, 52px);
}

p {
  color: var(--muted);
  line-height: 1.9;
}
.actions { display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; margin-top: 24px; }
@media (max-width: 520px) {
  .panel { padding: 28px 18px; }
  .actions { display: grid; }
  .actions :deep(.el-button) { width: 100%; margin-left: 0; }
}
</style>
