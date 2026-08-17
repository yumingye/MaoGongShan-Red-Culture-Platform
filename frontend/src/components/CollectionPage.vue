<template>
  <div>
    <PageHero :title="title" :subtitle="subtitle" :image="hero" />
    <main class="page">
      <section class="panel collection-tools">
        <el-input v-model="keyword" placeholder="输入关键词检索标题、正文、地点或标签" clearable @keyup.enter="load(1)" />
        <el-button type="primary" :loading="loading" @click="load(1)">查询</el-button>
        <el-button @click="reset">重置</el-button>
      </section>
      <SectionTitle :title="`${title}列表`" :desc="`共 ${total} 条${itemType}，每条均可进入详情页查看来源和相关推荐。`" />
      <el-alert v-if="error" :title="error" type="error" show-icon class="error-alert" />
      <div v-loading="loading" class="grid grid-3">
        <article v-for="item in list" :key="item.id" class="collection-card reveal" @click="$router.push(`${detailPrefix}/${item.id}`)">
          <SafeImage :src="item.image" :alt="item.title" :kind="imageKind(item)" />
          <div>
            <span>{{ item.date || item.location || item.category }}</span>
            <h3>{{ item.title }}</h3>
            <p>{{ item.summary }}</p>
          </div>
        </article>
      </div>
      <el-empty v-if="!loading && !list.length" description="没有找到匹配内容" />
      <div class="pager">
        <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total" layout="prev, pager, next, total" background @current-change="load" />
      </div>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { http, inferImageKind } from '../api/http'
import PageHero from './PageHero.vue'
import SafeImage from './SafeImage.vue'
import SectionTitle from './SectionTitle.vue'

const props = defineProps({
  title: String,
  subtitle: String,
  hero: String,
  api: String,
  detailPrefix: String,
  itemType: String
})

const keyword = ref('')
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 12
const loading = ref(false)
const error = ref('')

function imageKind(item) {
  return inferImageKind(props.itemType, props.title, item?.category, item?.title, item?.image)
}

async function load(nextPage = page.value) {
  page.value = nextPage
  loading.value = true
  error.value = ''
  try {
    const res = await http.get(props.api, { params: { keyword: keyword.value, page: page.value, page_size: pageSize } })
    list.value = res.data.items || res.data
    total.value = res.data.total ?? list.value.length
  } catch (err) {
    error.value = err?.response?.data?.detail || '内容加载失败，请确认后端服务已启动。'
  } finally {
    loading.value = false
  }
}

function reset() {
  keyword.value = ''
  load(1)
}

onMounted(() => load(1))
</script>

<style scoped>
.collection-tools {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  gap: 12px;
  padding: 18px;
  margin-bottom: 20px;
}

.collection-card {
  overflow: hidden;
  cursor: pointer;
  background: #fffaf0;
  border: 1px solid var(--line);
  border-radius: 14px;
  box-shadow: 0 14px 34px rgba(84, 16, 21, .1);
  transition: transform .2s ease, box-shadow .2s ease;
}

.collection-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 42px rgba(84, 16, 21, .16);
}

.collection-card :deep(.safe-image) {
  width: 100%;
  height: 210px;
}

.collection-card div {
  padding: 16px;
}

.collection-card span {
  color: var(--gold);
  font-size: 13px;
}

.collection-card h3 {
  color: var(--red-dark);
}

.collection-card p {
  color: var(--muted);
  line-height: 1.75;
}

@media (min-width: 1000px) {
  .collection-card:first-child {
    grid-column: span 2;
    display: grid;
    grid-template-columns: minmax(0, 1.25fr) minmax(280px, .75fr);
    min-height: 330px;
  }

  .collection-card:first-child :deep(.safe-image) {
    height: 100%;
    min-height: 330px;
  }

  .collection-card:first-child > div {
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: clamp(24px, 4vw, 42px);
  }

  .collection-card:first-child h3 {
    font-size: clamp(24px, 3vw, 34px);
  }
}

.pager {
  display: flex;
  justify-content: center;
  margin-top: 26px;
}

.error-alert {
  margin-bottom: 18px;
}

@media (max-width: 720px) {
  .collection-tools {
    grid-template-columns: 1fr;
  }
}
</style>
