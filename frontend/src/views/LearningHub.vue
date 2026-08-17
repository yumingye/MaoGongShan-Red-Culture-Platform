<template>
  <div class="learning-hub">
    <PageHero :title="pageTitle" :subtitle="pageSubtitle" :image="heroImage" mobile-image="/assets/images/generated/red-culture-gallery-v2-mobile.webp" eyebrow="红色文化数字学习馆" />

    <main class="page">
      <el-alert
        title="栏目边界说明"
        :description="scopeNote"
        type="warning"
        show-icon
        :closable="false"
        class="scope-note"
      />

      <section v-if="props.category === '党史学习'" class="stage-entry panel reveal">
        <div><span>九个阶段 · 可独立访问</span><h2>沿历史脉络进入专题</h2><p>从思想传播、建党初期到新时代，每个阶段都提供背景、节点、学习方法与权威来源入口。</p></div>
        <div class="stage-links"><RouterLink v-for="stage in historyStages" :key="stage.slug" :to="`/party-history/stage/${stage.slug}`"><small>{{ stage.period }}</small><strong>{{ stage.title }}</strong></RouterLink></div>
      </section>

      <section class="learning-toolbar panel">
        <el-input v-model="keyword" placeholder="检索标题、人物、地点、精神内涵" clearable @keyup.enter="load(1)">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="selectedCategory" placeholder="全部分类" clearable @change="load(1)">
          <el-option v-for="item in availableCategories" :key="item" :label="item" :value="item" />
        </el-select>
        <el-button type="primary" :loading="loading" @click="load(1)">开始检索</el-button>
      </section>

      <el-alert v-if="error" :title="error" type="error" show-icon class="scope-note" />

      <section v-if="featured" class="feature-story panel reveal">
        <SafeImage :src="featured.image" :alt="featured.title" loading="eager" />
        <div>
          <span class="scope-pill">{{ featured.scope }}</span>
          <p class="eyebrow">{{ featured.event_time }} · {{ featured.location }}</p>
          <h2>{{ featured.title }}</h2>
          <p>{{ featured.summary }}</p>
          <div class="tag-row">
            <span>{{ featured.category }}</span>
            <span>{{ featured.sub_category }}</span>
            <span>{{ featured.verification_status }}</span>
          </div>
          <el-button type="primary" @click="$router.push(`/learning/${featured.id}`)">进入专题</el-button>
        </div>
      </section>

      <SectionTitle :title="pageTitle" :desc="`已整理 ${total} 条可追溯专题资料，点击任一条目进入完整正文。`" />

      <div v-loading="loading" class="learning-grid">
        <RouterLink v-for="(item, index) in remainingItems" :key="item.id" :to="`/learning/${item.id}`" class="learning-card reveal">
          <div class="card-index">{{ String((page - 1) * pageSize + index + 2).padStart(2, '0') }}</div>
          <SafeImage :src="item.image" :alt="item.title" />
          <div class="card-copy">
            <span>{{ item.scope }}</span>
            <h3>{{ item.title }}</h3>
            <p>{{ item.summary }}</p>
            <div class="meta-line">
              <small>{{ item.event_time }}</small>
              <small>{{ item.location }}</small>
            </div>
          </div>
        </RouterLink>
      </div>

      <section v-if="!loading && !items.length" class="panel no-match">
        <h3>没有匹配到当前组合条件</h3>
        <p>可清除关键词或分类，继续浏览已经核验来源的专题资料。</p>
        <el-button type="primary" @click="reset">查看全部专题</el-button>
      </section>

      <el-pagination
        v-if="total > pageSize"
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next, total"
        background
        class="pagination"
        @current-change="load"
      />
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { http } from '../api/http'
import PageHero from '../components/PageHero.vue'
import SafeImage from '../components/SafeImage.vue'
import SectionTitle from '../components/SectionTitle.vue'
import { historyStages } from '../data/historyStages'

const props = defineProps({
  title: { type: String, default: '红色党史学习' },
  subtitle: { type: String, default: '沿着历史时期、重要事件与精神谱系，建立可追溯的数字学习路径。' },
  category: { type: String, default: '' },
  hero: { type: String, default: '/assets/images/commons/hero-hill-monument-jinan-2009-07-18-jpg.jpg' }
})

const items = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 12
const keyword = ref('')
const selectedCategory = ref(props.category)
const categories = ref([])
const loading = ref(false)
const error = ref('')

const pageTitle = computed(() => props.title)
const pageSubtitle = computed(() => props.subtitle)
const heroImage = computed(() => props.hero)
const featured = computed(() => items.value[0] || null)
const remainingItems = computed(() => items.value.slice(1))
const availableCategories = computed(() => props.category ? [props.category] : categories.value)
const scopeNote = computed(() => props.category === '红色事件'
  ? '本栏目为全国党史重大事件学习资料，不作为毛公山地方历史叙述。'
  : props.category === '红色精神'
    ? '本栏目依据公开发布的中国共产党人精神谱系资料整理，并与毛公山核心资源分区呈现。'
    : '全国党史、山东与青岛红色文化拓展资料均明确标注范围；毛公山地方内容另设“毛公山核心资源”标签。')

async function load(nextPage = page.value) {
  page.value = nextPage
  loading.value = true
  error.value = ''
  try {
    const response = await http.get('/api/learning-articles', {
      params: { keyword: keyword.value.trim(), category: selectedCategory.value, page: page.value, page_size: pageSize }
    })
    items.value = response.data.items || []
    total.value = response.data.total || 0
    categories.value = response.data.categories || []
  } catch (requestError) {
    error.value = requestError?.response?.data?.detail || '专题资料加载失败，请确认后端服务正在运行。'
  } finally {
    loading.value = false
  }
}

function reset() {
  keyword.value = ''
  selectedCategory.value = props.category
  load(1)
}

watch(() => props.category, (value) => {
  selectedCategory.value = value
  load(1)
})

onMounted(() => load(1))
</script>

<style scoped>
.scope-note { margin-bottom: 22px; }
.stage-entry{display:grid;grid-template-columns:280px minmax(0,1fr);gap:28px;padding:26px;margin-bottom:28px}.stage-entry>div:first-child span{color:var(--gold);font-weight:800}.stage-entry h2{margin:8px 0;color:var(--red-dark)}.stage-entry p{color:var(--muted);line-height:1.8}.stage-links{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}.stage-links a{display:grid;gap:4px;padding:12px;background:#fffaf0;border:1px solid var(--line);border-radius:8px;transition:.2s}.stage-links a:hover{border-color:var(--gold);transform:translateY(-2px)}.stage-links small{color:var(--muted)}.stage-links strong{color:var(--red-dark)}
.learning-toolbar { display: grid; grid-template-columns: minmax(0, 1fr) 230px auto; gap: 12px; padding: 18px; margin-bottom: 28px; }
.feature-story { display: grid; grid-template-columns: minmax(0, 1.08fr) minmax(320px, .92fr); overflow: hidden; margin-bottom: 52px; }
.feature-story :deep(.safe-image) { min-height: 430px; border-radius: 0; }
.feature-story > div { display: flex; flex-direction: column; align-items: flex-start; justify-content: center; padding: clamp(26px, 5vw, 54px); }
.feature-story h2 { margin: 8px 0 16px; color: var(--red-dark); font-size: clamp(28px, 4vw, 46px); line-height: 1.2; }
.feature-story p { color: var(--muted); line-height: 1.9; }
.feature-story .el-button { margin-top: 20px; }
.scope-pill { padding: 6px 10px; color: #fff; background: var(--red); border-radius: 4px; font-size: 13px; }
.learning-grid { display: grid; gap: 18px; }
.learning-card { position: relative; display: grid; grid-template-columns: 180px minmax(0, 1fr); min-height: 180px; overflow: hidden; background: rgba(255,250,240,.94); border: 1px solid var(--line); border-radius: 10px; box-shadow: 0 12px 28px rgba(84,16,21,.08); transition: transform .2s ease, box-shadow .2s ease; }
.learning-card:hover { transform: translateY(-3px); box-shadow: 0 18px 38px rgba(84,16,21,.14); }
.learning-card :deep(.safe-image) { min-height: 180px; border-radius: 0; }
.card-copy { padding: 22px 26px; }
.card-copy > span { color: var(--gold); font-weight: 700; font-size: 13px; }
.card-copy h3 { margin: 7px 0 10px; color: var(--red-dark); font-size: 22px; }
.card-copy p { margin: 0; color: var(--muted); line-height: 1.8; }
.card-copy small { color: #87796a; }
.card-index { position: absolute; right: 18px; top: 10px; color: rgba(143,29,34,.08); font: 800 54px/1 Georgia, serif; z-index: 1; }
.pagination { justify-content: center; margin-top: 30px; }
.no-match { padding: 34px; text-align: center; }
@media (max-width: 760px) {
  .stage-entry,.stage-links { grid-template-columns: 1fr; }
  .learning-toolbar, .feature-story { grid-template-columns: 1fr; }
  .feature-story :deep(.safe-image) { min-height: 260px; }
  .learning-card { grid-template-columns: 112px minmax(0, 1fr); }
  .learning-card :deep(.safe-image) { min-height: 100%; }
  .card-copy { padding: 16px; }
  .card-copy h3 { font-size: 18px; }
  .card-copy p { display: -webkit-box; overflow: hidden; -webkit-line-clamp: 3; -webkit-box-orient: vertical; }
}
</style>
