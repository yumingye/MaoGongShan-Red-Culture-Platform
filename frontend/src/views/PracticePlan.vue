<template>
  <div>
    <PageHero
      title="实践计划"
      subtitle="以时间轴呈现资料查阅、实地调研、数字采集、资源整理、平台建设和成果传播。"
      image="/assets/images/activity/maogongshan-3a-plaque.jpg"
    />
    <main class="page">
      <p class="data-note">
        本页内容来自社会实践申报材料和平台整理资料，属于项目计划与实施流程展示，不作为毛公山历史事实记载。
      </p>
      <el-timeline>
        <el-timeline-item
          v-for="item in plans"
          :key="item.id"
          :timestamp="`第 ${item.step_order} 阶段 | ${item.status}`"
          type="danger"
          placement="top"
        >
          <article class="panel plan-card reveal">
            <h3>{{ item.title }}</h3>
            <p>{{ item.summary }}</p>
            <el-tag type="warning">{{ item.verification_status }}</el-tag>
          </article>
        </el-timeline-item>
      </el-timeline>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { http } from '../api/http'
import PageHero from '../components/PageHero.vue'
import { offlineProject } from '../data/offlineFallbacks'

const plans = ref(offlineProject.plans)

onMounted(async () => {
  try {
    const rows = (await http.get('/api/project')).data?.plans
    if (Array.isArray(rows) && rows.length) plans.value = rows
  } catch {
    plans.value = offlineProject.plans
  }
})
</script>

<style scoped>
.plan-card {
  padding: 18px;
}

.plan-card h3 {
  color: var(--red-dark);
}

.plan-card p {
  color: var(--muted);
  line-height: 1.8;
}
</style>
