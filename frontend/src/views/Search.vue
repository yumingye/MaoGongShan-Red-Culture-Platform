<template>
  <main class="page search-page">
    <PageHero
      title="统一智能搜索"
      subtitle="同时检索历史事件、人物档案、数字资源、图片资料、景点点位、实践调研和山软青年专题内容。"
      image="/assets/images/scenery/maogongshan-mountain.jpg"
    />

    <section class="search-panel panel">
      <el-input
        v-model="q"
        size="large"
        placeholder="搜索毛公山、红色文化、山软青年、实践日志、地图点位等内容"
        clearable
        @keyup.enter="load"
        @input="loadSuggestions"
      >
        <template #append>
          <el-button type="primary" :loading="loading" @click="load">搜索</el-button>
        </template>
      </el-input>

      <div class="search-tools">
        <span>热门：</span>
        <el-tag v-for="word in hotWords" :key="word" effect="plain" @click="quickSearch(word)">{{ word }}</el-tag>
      </div>

      <div v-if="suggestions.length" class="search-tools">
        <span>建议：</span>
        <el-tag v-for="word in suggestions" :key="word" type="warning" effect="plain" @click="quickSearch(word)">
          {{ word }}
        </el-tag>
      </div>

      <div v-if="historyWords.length" class="search-tools">
        <span>历史：</span>
        <el-tag v-for="word in historyWords" :key="word" type="info" effect="plain" @click="quickSearch(word)">
          {{ word }}
        </el-tag>
        <el-button text type="danger" @click="clearHistory">清空历史</el-button>
      </div>
    </section>

    <el-alert v-if="error" :title="error" type="error" show-icon class="error-alert" />

    <section class="panel result-summary">
      <strong>共找到 {{ total }} 条相关结果</strong>
      <span v-if="q">关键词：{{ q }}</span>
      <span v-else>输入关键词可进一步缩小范围</span>
    </section>

    <el-empty v-if="!loading && q && total === 0" description="未找到匹配结果">
      <el-button type="primary" @click="quickSearch('毛公山')">查看毛公山相关资料</el-button>
      <el-button plain @click="quickSearch('山东大学软件学院')">查看山软青年专题</el-button>
    </el-empty>

    <el-tabs v-else v-model="activeType" class="result-tabs">
      <el-tab-pane v-for="group in groups" :key="group.key" :label="`${group.label} ${group.items.length}`" :name="group.key">
        <TransitionGroup name="fade-list" tag="div" class="result-list">
          <RouterLink
            v-for="item in group.items"
            :key="`${group.key}-${item.id}`"
            class="search-card"
            :to="resolveLink(group.key, item)"
          >
            <SafeImage v-if="item.image" :src="item.image" :alt="item.title" />
            <div>
              <div class="meta-line">
                <span class="type-pill">{{ group.label }}</span>
                <span>{{ item.meta }}</span>
              </div>
              <h3 v-html="highlight(item.title)"></h3>
              <p v-html="highlight(item.summary)"></p>
            </div>
          </RouterLink>
        </TransitionGroup>
        <el-empty v-if="!loading && !group.items.length" description="当前分类没有匹配结果" />
      </el-tab-pane>
    </el-tabs>
  </main>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { http } from '../api/http'
import PageHero from '../components/PageHero.vue'
import SafeImage from '../components/SafeImage.vue'
import { exhibitions, videoLessons } from '../data/experienceContent'
import { readStorage, removeStorage, writeStorage } from '../utils/storage'

const HISTORY_KEY = 'mg_search_history'

const route = useRoute()
const router = useRouter()
const q = ref(route.query.q || '')
const activeType = ref('events')
const loading = ref(false)
const error = ref('')
const suggestions = ref([])
const historyWords = ref([])
const data = reactive({ events: [], figures: [], resources: [], images: [], spots: [], learning: [] })
const hotWords = ['毛公山在哪里', '红色故事', '山东大学软件学院', '实践调研', '登山路线', '图片来源']

const groups = computed(() => [
  { key: 'events', label: '历史事件', items: data.events.map((item) => normalize(item, 'title', 'summary', 'event_time', item.image_url)) },
  { key: 'figures', label: '人物档案', items: data.figures.map((item) => normalize(item, 'name', 'biography', 'active_period', item.photo_url)) },
  { key: 'resources', label: '数字资源', items: data.resources.map((item) => normalize(item, 'name', 'summary', 'type', item.file_url)) },
  { key: 'images', label: '图片资料', items: data.images.map((item) => normalize(item, 'name', 'description', 'category', item.image_url || item.local_path)) },
  { key: 'spots', label: '景点点位', items: data.spots.map((item) => normalize(item, 'name', 'description', 'type', item.image_url)) },
  { key: 'learning', label: '党史学习', items: data.learning.map((item) => normalize(item, 'title', 'summary', 'event_time', item.image)) },
  { key: 'exhibitions', label: '数字展览', items: filterLocal(exhibitions).map((item) => normalize(item, 'title', 'summary', 'category', item.image)) },
  { key: 'videos', label: '图文微课', items: filterLocal(videoLessons).map((item) => normalize(item, 'title', 'summary', 'category', item.cover)) }
])

const total = computed(() => groups.value.reduce((sum, group) => sum + group.items.length, 0))

function normalize(item, titleKey, summaryKey, metaKey, image) {
  return {
    ...item,
    title: item[titleKey] || '未命名资料',
    summary: item[summaryKey] || '该资料已收录，详情页包含来源、标签和相关说明。',
    meta: item[metaKey] || '来源已标注',
    image
  }
}

function filterLocal(items) {
  const term = q.value.trim().toLowerCase()
  if (!term) return items
  return items.filter((item) => `${item.title} ${item.summary} ${item.category} ${(item.keywords || []).join(' ')}`.toLowerCase().includes(term))
}

function highlight(text = '') {
  const value = String(text)
  if (!q.value) return value
  const keyword = q.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return value.replace(new RegExp(keyword, 'gi'), (match) => `<span class="highlight">${match}</span>`)
}

function resolveLink(type, item) {
  if (type === 'events') return `/events/${item.id}`
  if (type === 'figures') return `/figures/${item.id}`
  if (type === 'resources') return `/resources/${item.id}`
  if (type === 'images') return `/images/${item.id}`
  if (type === 'learning') return `/learning/${item.id}`
  if (type === 'exhibitions') return `/exhibitions/${item.slug}`
  if (type === 'videos') return `/videos/${item.slug}`
  return '/map'
}

function readHistory() {
  const value = readStorage(HISTORY_KEY, [])
  historyWords.value = Array.isArray(value) ? value : []
}

function saveHistory(word) {
  const value = word.trim()
  if (!value) return
  const next = [value, ...historyWords.value.filter((item) => item !== value)].slice(0, 8)
  writeStorage(HISTORY_KEY, next)
  historyWords.value = next
}

function clearHistory() {
  removeStorage(HISTORY_KEY)
  historyWords.value = []
}

function quickSearch(word) {
  q.value = word
  load()
}

async function loadSuggestions() {
  if (!q.value.trim()) {
    suggestions.value = []
    return
  }
  try {
    const res = await http.get('/api/search/suggestions', { params: { q: q.value } })
    suggestions.value = (res.data.items || res.data || []).slice(0, 8)
  } catch {
    suggestions.value = []
  }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const keyword = q.value.trim()
    const res = await http.get('/api/search', { params: { q: keyword } })
    Object.assign(data, res.data)
    if (keyword) saveHistory(keyword)
    router.replace({ path: '/search', query: keyword ? { q: keyword } : {} })
    await loadSuggestions()
    const firstAvailable = groups.value.find((group) => group.items.length)
    if (firstAvailable && !groups.value.find((group) => group.key === activeType.value)?.items.length) activeType.value = firstAvailable.key
  } catch (err) {
    error.value = err?.response?.data?.detail || '搜索失败，请确认后端服务已启动。'
  } finally {
    loading.value = false
  }
}

watch(() => route.query.q, (value) => {
  if ((value || '') !== q.value) {
    q.value = value || ''
    load()
  }
})

onMounted(() => {
  readHistory()
  load()
})
</script>

<style scoped>
.search-page {
  padding-top: 0;
}

.search-panel {
  padding: 20px;
  margin-bottom: 18px;
}

.search-tools {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  margin-top: 14px;
}

.search-tools span {
  color: var(--muted);
}

.search-tools .el-tag {
  cursor: pointer;
}

.result-summary {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 18px;
  margin-bottom: 18px;
  color: var(--muted);
}

.result-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.search-card {
  display: grid;
  grid-template-columns: 140px minmax(0, 1fr);
  gap: 16px;
  padding: 14px;
  color: inherit;
  text-decoration: none;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 10px;
  transition: transform .2s ease, box-shadow .2s ease;
}

.search-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 16px 34px rgba(95, 12, 21, .12);
}

.search-card img {
  width: 100%;
  height: 110px;
  object-fit: cover;
  border-radius: 8px;
}

.search-card h3 {
  margin: 8px 0;
  color: var(--red-dark);
}

.search-card p {
  margin: 0;
  color: var(--muted);
  line-height: 1.8;
}

.type-pill {
  padding: 4px 8px;
  color: #fff;
  background: var(--red);
  border-radius: 999px;
  font-size: 12px;
}

.error-alert {
  margin-bottom: 18px;
}

:deep(.highlight) {
  padding: 0 2px;
  color: var(--red);
  background: rgba(199, 45, 45, .12);
  border-radius: 3px;
}

@media (max-width: 820px) {
  .result-summary,
  .search-card {
    grid-template-columns: 1fr;
  }

  .result-list {
    grid-template-columns: 1fr;
  }
}
</style>
