<template>
  <div>
    <PageHero v-if="item" :title="item.title" :subtitle="item.summary" :image="assetUrl(item.image)" eyebrow="实践日志详情" />
    <main class="page" v-loading="loading">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: '/research' }">实践调研</el-breadcrumb-item>
        <el-breadcrumb-item>{{ item?.title || '日志详情' }}</el-breadcrumb-item>
      </el-breadcrumb>
      <el-empty v-if="!loading && !item" description="日志不存在或加载失败" />
      <article v-if="item" class="detail-layout">
        <section class="panel detail">
          <SafeImage :src="item.image" :alt="item.title" />
          <h1>{{ item.title }}</h1>
          <p class="meta">{{ item.date }} | {{ item.location }} | {{ item.category }}</p>
          <el-alert
            v-if="item.category === '访谈整理稿'"
            class="record-notice"
            title="情景化整理稿"
            description="本文依据项目调研目标编写，用于展示访谈提纲和记录结构，不代表真实受访者原话。转为正式访谈记录前，必须依据授权录音、现场笔记和受访者确认逐条核对。"
            type="warning"
            :closable="false"
            show-icon
          />
          <p class="body">{{ item.content }}</p>
          <section class="source-box">
            <strong>资料性质与来源</strong>
            <p>{{ item.source || '山软寻脉·毛公山数字调研实践团公开整理文稿' }}</p>
          </section>
          <div class="actions">
            <el-button type="primary" @click="toggle">{{ favoriteLabel }}</el-button>
            <el-button plain @click="share">复制分享链接</el-button>
            <el-button plain @click="$router.push('/research')">返回实践调研</el-button>
          </div>
        </section>
        <aside class="panel side">
          <h3>相关日志</h3>
          <router-link v-for="related in item.related" :key="related.id" :to="`/research/${related.id}`">
            <span>{{ related.date }}</span>
            <strong>{{ related.title }}</strong>
          </router-link>
        </aside>
      </article>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { http, assetUrl } from '../api/http'
import PageHero from '../components/PageHero.vue'
import SafeImage from '../components/SafeImage.vue'
import { addRecentView, isFavorite, toggleFavorite } from '../utils/library'
import { copyText } from '../utils/clipboard'

const route = useRoute()
const item = ref(null)
const loading = ref(false)
const version = ref(0)
const key = computed(() => item.value ? `research:${item.value.id}` : '')
const favoriteLabel = computed(() => {
  version.value
  return key.value && isFavorite(key.value) ? '取消收藏' : '收藏日志'
})

function payload() {
  return { key: key.value, type: '实践日志', title: item.value.title, summary: item.value.summary, url: `/research/${item.value.id}` }
}

async function share() {
  const copied = await copyText(window.location.href)
  copied ? ElMessage.success('分享链接已复制') : ElMessage.warning('复制失败，请手动复制地址栏链接')
}

function toggle() {
  const added = toggleFavorite(payload())
  version.value += 1
  ElMessage.success(added ? '已收藏日志' : '已取消收藏')
}

onMounted(async () => {
  loading.value = true
  try {
    item.value = (await http.get(`/api/research-logs/${route.params.id}`)).data
    addRecentView(payload())
  } catch {
    item.value = null
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.detail-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 24px;
  margin-top: 24px;
}

.detail {
  padding: 30px;
}

.detail img {
  width: 100%;
  max-height: 420px;
  object-fit: cover;
  border-radius: 12px;
}

.detail h1 {
  color: var(--red-dark);
  font-size: clamp(30px, 5vw, 52px);
}

.detail p {
  color: var(--muted);
  line-height: 2;
}

.meta {
  color: var(--gold) !important;
}

.body {
  white-space: pre-line;
}

.record-notice {
  margin: 18px 0 24px;
}

.record-notice :deep(.el-alert__description) {
  line-height: 1.8;
}

.source-box {
  margin-top: 28px;
  padding: 18px 20px;
  border-left: 4px solid var(--gold);
  background: #fbf7ef;
}

.source-box strong {
  color: var(--red-dark);
}

.source-box p {
  margin: 8px 0 0;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 20px;
}

.side {
  padding: 20px;
}

.side h3 {
  color: var(--red-dark);
}

.side a {
  display: grid;
  gap: 4px;
  padding: 12px 0;
  text-decoration: none;
  border-bottom: 1px solid var(--line);
}

.side span {
  color: var(--gold);
  font-size: 12px;
}

.side strong {
  color: var(--red-dark);
}

@media (max-width: 900px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }
}
</style>
