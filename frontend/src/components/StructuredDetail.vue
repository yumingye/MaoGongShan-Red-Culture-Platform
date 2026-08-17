<template>
  <div>
    <PageHero
      v-if="item"
      :title="item.title"
      :subtitle="item.summary"
      :image="assetUrl(item.image)"
      :eyebrow="itemType"
    />

    <main class="page" v-loading="loading">
      <el-alert v-if="error" :title="error" type="error" show-icon class="detail-error" />
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: listPath }">{{ listName }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ item?.title || itemType }}</el-breadcrumb-item>
      </el-breadcrumb>

      <el-empty v-if="!loading && !item" :description="`${itemType}不存在或加载失败`">
        <el-button type="primary" @click="$router.push(listPath)">返回列表</el-button>
      </el-empty>

      <article v-if="item" class="detail-layout">
        <section class="panel detail-main">
          <SafeImage :src="item.image" :alt="item.title" :kind="imageKind(item)" loading="eager" />
          <h1>{{ item.title }}</h1>
          <div class="meta-line">
            <el-tag v-if="item.category" type="danger">{{ item.category }}</el-tag>
            <el-tag v-if="item.date">{{ item.date }}</el-tag>
            <el-tag v-if="item.location" type="info">{{ item.location }}</el-tag>
          </div>
          <p class="lead">{{ item.summary }}</p>
          <div class="body">
            <p v-for="(paragraph,index) in contentParagraphs" :key="index">{{ paragraph }}</p>
          </div>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="资料来源">{{ item.source || '平台资料库' }}</el-descriptions-item>
            <el-descriptions-item label="标签">{{ formatTags(item.tags) }}</el-descriptions-item>
          </el-descriptions>
          <div class="actions">
            <el-button type="primary" @click="toggle">{{ favoriteLabel }}</el-button>
            <el-button plain @click="share">复制分享链接</el-button>
            <el-button plain @click="$router.push(listPath)">返回列表</el-button>
          </div>
          <nav class="prev-next" aria-label="上一篇和下一篇">
            <RouterLink v-if="previousItem" :to="`${detailPrefix}/${previousItem.id}`">
              <span>上一篇</span>
              <strong>{{ previousItem.title }}</strong>
            </RouterLink>
            <RouterLink v-if="nextItem" :to="`${detailPrefix}/${nextItem.id}`">
              <span>下一篇</span>
              <strong>{{ nextItem.title }}</strong>
            </RouterLink>
          </nav>
        </section>

        <aside class="panel side">
          <h3>相关推荐</h3>
          <RouterLink v-for="related in relatedItems" :key="related.id" :to="`${detailPrefix}/${related.id}`">
            <SafeImage :src="related.image" :alt="related.title" :kind="imageKind(related)" />
            <span><small>{{ related.date || related.location || related.category }}</small><strong>{{ related.title }}</strong></span>
          </RouterLink>
          <el-empty v-if="!relatedItems.length" description="可从列表继续浏览同类资料" />
        </aside>
      </article>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { http, assetUrl, inferImageKind } from '../api/http'
import PageHero from './PageHero.vue'
import SafeImage from './SafeImage.vue'
import { addRecentView, isFavorite, toggleFavorite } from '../utils/library'

const props = defineProps({
  api: String,
  detailPrefix: String,
  listPath: String,
  listName: String,
  itemType: String,
  favoriteType: String
})

const route = useRoute()
const item = ref(null)
const list = ref([])
const loading = ref(false)
const error = ref('')
const version = ref(0)

function imageKind(entry) {
  return inferImageKind(props.itemType, entry?.category, entry?.title, entry?.image)
}

const favoriteKey = computed(() => item.value ? `${props.favoriteType}:${item.value.id}` : '')
const favoriteLabel = computed(() => {
  version.value
  return favoriteKey.value && isFavorite(favoriteKey.value) ? '取消收藏' : `收藏${props.itemType}`
})

const currentIndex = computed(() => list.value.findIndex((entry) => String(entry.id) === String(item.value?.id)))
const previousItem = computed(() => currentIndex.value > 0 ? list.value[currentIndex.value - 1] : null)
const nextItem = computed(() => currentIndex.value >= 0 && currentIndex.value < list.value.length - 1 ? list.value[currentIndex.value + 1] : null)
const relatedItems = computed(() => item.value?.related?.length ? item.value.related : list.value.filter((entry) => entry.id !== item.value?.id).slice(0, 5))
const contentParagraphs = computed(() => String(item.value?.content || item.value?.summary || '').split(/\n{2,}/).map((text) => text.trim()).filter(Boolean))

function formatTags(tags) {
  if (Array.isArray(tags)) return tags.join('、')
  return tags || '未设置标签'
}

function payload() {
  return {
    key: favoriteKey.value,
    type: props.itemType,
    title: item.value.title,
    summary: item.value.summary,
    url: `${props.detailPrefix}/${item.value.id}`
  }
}

function toggle() {
  const added = toggleFavorite(payload())
  version.value += 1
  ElMessage.success(added ? '已收藏' : '已取消收藏')
}

async function share() {
  try {
    await navigator.clipboard.writeText(window.location.href)
    ElMessage.success('分享链接已复制')
  } catch {
    ElMessage.warning('当前浏览器不支持自动复制，请手动复制地址栏链接')
  }
}

async function loadDetail() {
  loading.value = true
  error.value = ''
  try {
    const [detailRes, listRes] = await Promise.all([
      http.get(`${props.api}/${route.params.id}`),
      http.get(`${props.api}?page=1&page_size=200`)
    ])
    item.value = detailRes.data
    list.value = Array.isArray(listRes.data) ? listRes.data : listRes.data.items || []
    addRecentView(payload())
  } catch (requestError) {
    item.value = null
    list.value = []
    error.value = requestError?.response?.data?.detail || `${props.itemType}加载失败，可返回列表继续浏览。`
  } finally {
    loading.value = false
  }
}

watch(() => route.params.id, loadDetail)
onMounted(loadDetail)
</script>

<style scoped>
.detail-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 24px;
  margin-top: 24px;
}
.detail-error { margin: 18px 0; }

.detail-main {
  padding: 28px;
}

.detail-main :deep(.safe-image) {
  width: 100%;
  height: min(440px, 52vw);
  border-radius: 12px;
}

.detail-main h1 {
  color: var(--red-dark);
  font-size: clamp(30px, 5vw, 52px);
}

.meta-line {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.lead,
.body p {
  color: var(--muted);
  line-height: 2;
  white-space: pre-line;
}

.body p:first-child::first-letter { float:left;margin:8px 8px 0 0;color:var(--red);font:700 50px/38px Georgia,serif; }

.actions,
.prev-next {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 20px;
}

.prev-next a {
  flex: 1 1 240px;
  display: grid;
  gap: 6px;
  padding: 14px 16px;
  color: var(--red-dark);
  background: rgba(255, 250, 240, .8);
  border: 1px solid var(--line);
  border-radius: 10px;
}

.prev-next span,
.side span {
  color: var(--gold);
  font-size: 12px;
}

.side {
  padding: 20px;
}

.side h3 {
  color: var(--red-dark);
}

.side a {
  display: grid;
  grid-template-columns: 82px 1fr;
  gap: 12px;
  align-items: center;
  padding: 12px 0;
  text-decoration: none;
  border-bottom: 1px solid var(--line);
}

.side a :deep(.safe-image) {
  width: 82px;
  height: 64px;
  border-radius: 8px;
}

.side a > span {
  display: grid;
  gap: 5px;
}

.side a small {
  color: var(--gold);
}

.side strong,
.prev-next strong {
  color: var(--red-dark);
}

@media (max-width: 900px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }
}
</style>
