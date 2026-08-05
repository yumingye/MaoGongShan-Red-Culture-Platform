<template>
  <main class="page not-found">
    <div class="panel">
      <h1>页面未找到</h1>
      <p>资源库没有这个地址。你可以返回首页，或使用顶部搜索查找历史、图片、路线和数字资源。</p>
      <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
      <el-button plain @click="$router.push('/search')">进入搜索</el-button>
    </div>
  </main>
</template>

<style scoped>
.not-found {
  display: grid;
  place-items: center;
  min-height: 70vh;
}

.panel {
  max-width: 680px;
  padding: 36px;
  text-align: center;
}

h1 {
  color: var(--red-dark);
  font-size: 48px;
}

p {
  color: var(--muted);
  line-height: 1.9;
}
</style>
