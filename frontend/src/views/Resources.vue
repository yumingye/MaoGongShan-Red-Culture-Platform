<template>
  <div>
    <PageHero
      title="数字资源库"
      subtitle="统一管理文献、图片、音频、调研记录、实践成果、地点、人物和红色故事等结构化资料。"
      image="/assets/images/culture/qingfeng-community.jpg"
      eyebrow="Digital Resource Library"
    />
    <main class="page">
      <section class="resource-dashboard">
        <div class="panel query-panel">
          <el-form class="toolbar" inline>
            <el-form-item label="关键词">
              <el-input v-model="keyword" placeholder="资源名称、简介、标签" clearable @keyup.enter="load(1)" />
            </el-form-item>
            <el-form-item label="资源类型">
              <el-select v-model="type" placeholder="全部类型" clearable style="width: 190px">
                <el-option v-for="item in categories" :key="item.name" :label="item.name" :value="item.name" />
              </el-select>
            </el-form-item>
            <el-button type="primary" :loading="loading" @click="load(1)">查询</el-button>
            <el-button @click="reset">重置</el-button>
          </el-form>
          <div class="type-cloud">
            <button
              v-for="item in categories.slice(0, 12)"
              :key="item.name"
              :class="{ active: type === item.name }"
              @click="type = item.name; load(1)"
            >
              {{ item.name }}
            </button>
          </div>
        </div>
        <aside class="panel resource-note">
          <strong>资源说明</strong>
          <p>每条资源保留来源、标签、浏览量和详情入口。历史事实、实践材料、技术说明和扩展参考资源按类型区分展示。</p>
          <RouterLink to="/sources">查看资料来源与考证说明</RouterLink>
        </aside>
      </section>

      <section class="category-entry reveal">
        <RouterLink to="/resources/category/documents">文献资料库</RouterLink>
        <RouterLink to="/resources/category/images">图片资源库</RouterLink>
        <RouterLink to="/resources/category/audio">音频讲解资源</RouterLink>
        <RouterLink to="/resources/category/achievements">实践成果资源</RouterLink>
        <RouterLink to="/search?q=毛公山">全局搜索</RouterLink>
        <RouterLink to="/favorites">收藏中心</RouterLink>
      </section>

      <SectionTitle title="资源列表" :desc="`共 ${total} 条资源，当前第 ${page} 页。`" />
      <el-alert v-if="error" :title="error" type="error" show-icon class="error-alert" />
      <div v-loading="loading" class="grid grid-3">
        <ResourceCard v-for="item in list" :key="item.id" :item="item" />
      </div>
      <el-empty v-if="!loading && !list.length" description="没有匹配资源，请尝试更换关键词或分类。" />
      <div class="pager">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next, total"
          background
          @current-change="load"
        />
      </div>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { http, normalizeListResponse } from '../api/http'
import PageHero from '../components/PageHero.vue'
import SectionTitle from '../components/SectionTitle.vue'
import ResourceCard from '../components/ResourceCard.vue'

const route = useRoute()
const keyword = ref('')
const type = ref(route.query.type || '')
const list = ref([])
const categories = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 9
const loading = ref(false)
const error = ref('')

async function load(nextPage = page.value) {
  page.value = nextPage
  loading.value = true
  error.value = ''
  try {
    const res = await http.get('/api/resources', { params: { keyword: keyword.value, type: type.value, page: page.value, page_size: pageSize } })
    const data = normalizeListResponse(res.data)
    list.value = data.items
    total.value = data.total
  } catch (err) {
    error.value = err?.response?.data?.detail || '资源加载失败，请确认后端服务已启动。'
  } finally {
    loading.value = false
  }
}

function reset() {
  keyword.value = ''
  type.value = ''
  load(1)
}

watch(() => route.query.type, (value) => {
  type.value = value || ''
  load(1)
})

onMounted(async () => {
  const categoryRes = await http.get('/api/categories')
  categories.value = categoryRes.data
  await load(1)
})
</script>

<style scoped>
.resource-dashboard {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 18px;
  margin-bottom: 24px;
}

.query-panel,
.resource-note {
  padding: 18px;
}

.resource-note {
  color: var(--muted);
  line-height: 1.8;
  background:
    linear-gradient(135deg, rgba(127, 29, 29, .08), rgba(20, 83, 45, .08)),
    #fff;
}

.resource-note strong,
.resource-note a {
  color: var(--red-dark);
  font-weight: 700;
}

.type-cloud,
.category-entry {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.type-cloud {
  margin-top: 12px;
}

.type-cloud button,
.category-entry a {
  padding: 8px 12px;
  color: var(--muted);
  cursor: pointer;
  background: #fff7ed;
  border: 1px solid rgba(180, 83, 9, .18);
  border-radius: 999px;
}

.category-entry {
  margin-bottom: 28px;
}

.category-entry a {
  color: var(--red-dark);
  background: #fffaf0;
  border-color: var(--line);
}

.type-cloud button.active,
.type-cloud button:hover,
.category-entry a:hover {
  color: #fff;
  background: var(--red);
}

.pager {
  display: flex;
  justify-content: center;
  margin-top: 28px;
}

.error-alert {
  margin-bottom: 18px;
}

@media (max-width: 900px) {
  .resource-dashboard {
    grid-template-columns: 1fr;
  }
}
</style>
