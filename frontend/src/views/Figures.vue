<template>
  <div>
    <PageHero
      title="历史人物资料"
      subtitle="汇集30位革命先辈、英雄模范、科学家和新时代榜样的真人照片与人物档案。"
      image="/assets/images/party-history/info-party-founding.jpg"
    />
    <main class="page">
      <div class="toolbar">
        <el-input v-model="keyword" placeholder="按人物姓名、活动时期、事迹或关系搜索" clearable @keyup.enter="load(1)">
          <template #prefix><el-icon><Search /></el-icon></template>
          <template #append><el-button :loading="loading" @click="load(1)">搜索</el-button></template>
        </el-input>
      </div>

      <SectionTitle title="人物列表" :desc="`共 ${total} 条人物资料`" />
      <el-alert v-if="error" :title="error" type="error" show-icon class="error-alert" />
      <div v-loading="loading" class="grid grid-2">
        <FigureCard v-for="item in list" :key="item.id" :item="item" />
      </div>
      <el-empty v-if="!loading && !list.length" description="当前条件未匹配人物，可清除关键词查看全部档案" />
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
import { onMounted, ref } from 'vue'
import { http, normalizeListResponse } from '../api/http'
import PageHero from '../components/PageHero.vue'
import SectionTitle from '../components/SectionTitle.vue'
import FigureCard from '../components/FigureCard.vue'

const keyword = ref('')
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 8
const loading = ref(false)
const error = ref('')

async function load(nextPage = page.value) {
  page.value = nextPage
  loading.value = true
  error.value = ''
  try {
    const res = await http.get('/api/figures', { params: { keyword: keyword.value, page: page.value, page_size: pageSize } })
    const data = normalizeListResponse(res.data)
    list.value = data.items
    total.value = data.total
  } catch (err) {
    error.value = err?.response?.data?.detail || '人物资料加载失败，请确认后端服务已启动。'
  } finally {
    loading.value = false
  }
}

onMounted(() => load(1))
</script>

<style scoped>
.pager {
  display: flex;
  justify-content: center;
  margin-top: 28px;
}

.error-alert {
  margin-bottom: 18px;
}
</style>
