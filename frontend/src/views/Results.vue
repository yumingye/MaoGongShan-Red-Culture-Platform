<template>
  <div>
    <PageHero
      title="项目成果展示"
      subtitle="集中展示资源库、调研报告、宣传内容、技术方案和社会实践总结等成果。"
      image="/assets/images/activity/xifu-grape-harvest.jpg"
    />
    <main class="page">
      <div class="grid grid-3">
        <article v-for="item in results" :key="item.id" class="resource-card reveal">
          <div class="resource-icon">
            <el-icon><Document /></el-icon>
          </div>
          <div>
            <el-tag type="warning">{{ item.status }}</el-tag>
            <h3>{{ item.title }}</h3>
            <p class="subtle">{{ item.summary }}</p>
            <p class="mini-meta">来源：{{ item.source_title }} | {{ item.verification_status }}</p>
          </div>
        </article>
      </div>
    </main>
  </div>
</template>

<script setup>
import { Document } from '@element-plus/icons-vue'
import { onMounted, ref } from 'vue'
import { http } from '../api/http'
import PageHero from '../components/PageHero.vue'
import { offlineProject } from '../data/offlineFallbacks'

const results = ref(offlineProject.results)

onMounted(async () => {
  try {
    const rows = (await http.get('/api/project')).data?.results
    if (Array.isArray(rows) && rows.length) results.value = rows
  } catch {
    results.value = offlineProject.results
  }
})
</script>
