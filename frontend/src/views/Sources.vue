<template>
  <div>
    <PageHero title="资料来源与考证说明" subtitle="记录公开资料来源、检索日期、版权状态和考证状态。" image="/assets/images/culture/maogongshan-red-park-2022.jpg" />
    <main class="page">
      <el-table :data="sources" class="panel" stripe>
        <el-table-column prop="title" label="资料标题" min-width="180" />
        <el-table-column prop="source_name" label="来源名称" min-width="160" />
        <el-table-column prop="source_type" label="类型" width="130" />
        <el-table-column prop="retrieved_at" label="检索日期" width="120" />
        <el-table-column prop="verification_status" label="状态" width="120" />
        <el-table-column label="链接" width="110">
          <template #default="{ row }">
            <el-link v-if="row.source_url" :href="row.source_url" target="_blank" type="primary">打开</el-link>
            <span v-else>本地项目资料</span>
          </template>
        </el-table-column>
      </el-table>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { http } from '../api/http'
import PageHero from '../components/PageHero.vue'
import { offlineSources } from '../data/offlineFallbacks'
const sources = ref(offlineSources)
onMounted(async () => {
  try {
    const rows = (await http.get('/api/sources')).data
    if (Array.isArray(rows) && rows.length) sources.value = rows
  } catch {
    sources.value = offlineSources
  }
})
</script>
