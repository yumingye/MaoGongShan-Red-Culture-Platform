<template>
  <div>
    <PageHero
      title="红色历史资料查询"
      subtitle="支持关键词、分类、时间、地点和考证状态筛选，资料详情页保留来源、参考资料和相关推荐。"
      image="/assets/images/generated/history-archive-v2-wide.webp"
      mobile-image="/assets/images/generated/history-archive-v2-mobile.webp"
      eyebrow="Red History Archive"
    />
    <main class="page">
      <p class="data-note">查询结果优先展示公开资料和来源已记录内容；无法确认的历史信息不会被写成确定事实。</p>

      <section class="history-topics panel reveal">
        <div>
          <p class="eyebrow">历史专题入口</p>
          <h2>按时间、人物、故事和精神主题进入红色文化资料</h2>
        </div>
        <div class="topic-buttons">
          <RouterLink to="/timeline">历史时间轴</RouterLink>
          <RouterLink to="/figures">红色人物</RouterLink>
          <RouterLink to="/stories">红色故事</RouterLink>
          <RouterLink to="/history/topic/spirit">红色精神专题</RouterLink>
          <RouterLink to="/history/topic/qingdao-memory">青岛与城阳红色记忆</RouterLink>
        </div>
      </section>

      <el-form class="toolbar" :model="filters" label-position="top">
        <el-row :gutter="14">
          <el-col :xs="24" :md="8">
            <el-form-item label="关键词">
              <el-input v-model="filters.keyword" placeholder="标题、正文、人物、地点" clearable @keyup.enter="load(1)" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="4">
            <el-form-item label="资料分类">
              <el-select v-model="filters.category" placeholder="全部" clearable>
                <el-option v-for="item in categories" :key="item" :label="item" :value="item" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="4">
            <el-form-item label="时间">
              <el-input v-model="filters.event_time" placeholder="如 2024" clearable />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="4">
            <el-form-item label="地点">
              <el-input v-model="filters.location" placeholder="城阳区" clearable />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="4">
            <el-form-item label="考证状态">
              <el-select v-model="filters.verification_status" placeholder="全部" clearable>
                <el-option label="公开报道" value="公开报道" />
                <el-option label="公开转载资料" value="公开转载资料" />
                <el-option label="公开百科资料" value="公开百科资料" />
                <el-option label="实践团队整理" value="实践团队整理" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <div class="meta-line">
          <el-button type="primary" :loading="loading" @click="load(1)">查询资料</el-button>
          <el-button @click="reset">重置条件</el-button>
        </div>
      </el-form>

      <SectionTitle title="查询结果" :desc="`共找到 ${total} 条资料，当前第 ${page} 页。`" />
      <el-alert v-if="error" :title="error" type="error" show-icon class="error-alert" />
      <div v-loading="loading" class="grid grid-3 result-grid">
        <HistoryCard v-for="item in list" :key="item.id" :item="item" />
      </div>
      <el-empty v-if="!loading && !list.length" description="当前条件未匹配资料，请调整关键词或筛选条件。" />
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
import { onMounted, reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { http, normalizeListResponse } from '../api/http'
import PageHero from '../components/PageHero.vue'
import SectionTitle from '../components/SectionTitle.vue'
import HistoryCard from '../components/HistoryCard.vue'

const filters = reactive({ keyword: '', category: '', event_time: '', location: '', verification_status: '' })
const categories = ['历史事件', '历史文献', '新闻报道', '研究文章', '口述历史', '景区资料', '图片资料', '视频资料']
const list = ref([])
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
    const res = await http.get('/api/events', { params: { ...filters, page: page.value, page_size: pageSize } })
    const data = normalizeListResponse(res.data)
    list.value = data.items
    total.value = data.total
  } catch (err) {
    error.value = err?.response?.data?.detail || '资料加载失败，请确认后端服务已启动。'
  } finally {
    loading.value = false
  }
}

function reset() {
  Object.keys(filters).forEach((key) => (filters[key] = ''))
  load(1)
}

onMounted(() => load(1))
</script>

<style scoped>
.history-topics {
  display: grid;
  grid-template-columns: minmax(0, .9fr) minmax(0, 1.1fr);
  gap: 18px;
  align-items: center;
  padding: 24px;
  margin-bottom: 24px;
  background:
    linear-gradient(120deg, rgba(84, 16, 21, .92), rgba(25, 65, 86, .82)),
    url('/assets/images/commons/liberation-pavillion-jinan-2008-11-jpg.jpg') center/cover;
  color: #fff8e6;
}

.history-topics h2 {
  margin: 0;
  font-size: clamp(24px, 4vw, 40px);
}

.topic-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.topic-buttons a {
  padding: 10px 14px;
  background: rgba(255, 248, 229, .13);
  border: 1px solid rgba(255, 248, 229, .24);
  border-radius: 999px;
}

.result-grid {
  min-height: 240px;
}

.error-alert {
  margin-bottom: 18px;
}

.pager {
  display: flex;
  justify-content: center;
  margin-top: 28px;
}

@media (max-width: 900px) {
  .history-topics {
    grid-template-columns: 1fr;
  }
}
</style>
