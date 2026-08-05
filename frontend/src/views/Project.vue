<template>
  <div>
    <PageHero
      title="实践项目介绍"
      subtitle="山软寻脉·毛公山数字调研实践团公开信息与资源库建设思路展示。"
      image="/assets/images/commons/national-shandong-university-qingdao-jpg.jpg"
    />
    <main class="page">
      <SectionTitle title="项目基本信息" desc="围绕红色文化数字化保护、社会实践调研和青年传播能力建设整理。" />
      <div class="project-grid">
        <article v-for="item in information" :key="item.id" class="panel info-card reveal">
          <span>{{ item.category }}</span>
          <h3>{{ item.title }}</h3>
          <p>{{ item.value }}</p>
          <el-tag type="warning">{{ item.verification_status }}</el-tag>
        </article>
      </div>
      <SectionTitle title="实践计划概览" />
      <el-timeline>
        <el-timeline-item v-for="item in plans.slice(0, 6)" :key="item.id" :timestamp="`第 ${item.step_order} 阶段`" type="danger">
          <h3>{{ item.title }}</h3>
          <p class="subtle">{{ item.summary }}</p>
        </el-timeline-item>
      </el-timeline>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { http } from '../api/http'
import PageHero from '../components/PageHero.vue'
import SectionTitle from '../components/SectionTitle.vue'
import { offlineProject } from '../data/offlineFallbacks'

const information = ref(offlineProject.information)
const plans = ref(offlineProject.plans)

onMounted(async () => {
  try {
    const data = (await http.get('/api/project')).data || {}
    if (Array.isArray(data.information) && data.information.length) information.value = data.information
    if (Array.isArray(data.plans) && data.plans.length) plans.value = data.plans
  } catch {
    information.value = offlineProject.information
    plans.value = offlineProject.plans
  }
})
</script>

<style scoped>
.project-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
  margin-bottom: 40px;
}

.info-card {
  padding: 18px;
}

.info-card span {
  color: var(--gold);
  font-weight: 700;
}

.info-card h3 {
  color: var(--red-dark);
}

.info-card p {
  color: var(--muted);
  line-height: 1.8;
}

@media (max-width: 900px) {
  .project-grid {
    grid-template-columns: 1fr;
  }
}
</style>
