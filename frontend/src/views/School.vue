<template>
  <div>
    <PageHero
      title="软件赋能红色文化传承"
      subtitle="山东大学软件学院学生以软件工程、数据治理、地图导览和智能问答技术建设毛公山数字资源平台。"
      image="/assets/images/generated/youth-fieldwork-v2-wide.webp"
      mobile-image="/assets/images/generated/youth-fieldwork-v2-mobile.webp"
      eyebrow="山东大学软件学院专题"
    />
    <main class="page">
      <section class="school-hero panel reveal">
        <div>
          <p class="eyebrow">{{ data.unit || '山东大学软件学院' }}</p>
          <h1>{{ data.title || '山软青年数字实践' }}</h1>
          <p>用代码组织文化资源，用数据连接历史记忆，用交互设计提升红色文化传播体验。</p>
        </div>
        <div class="school-links">
          <RouterLink to="/school/topic/introduction">学院与项目</RouterLink>
          <RouterLink to="/school/topic/architecture">系统架构</RouterLink>
          <RouterLink to="/school/topic/development">开发过程</RouterLink>
          <RouterLink to="/school/topic/responsibility">青年责任</RouterLink>
          <RouterLink to="/team">成员分工</RouterLink>
          <RouterLink to="/achievements">数字化成果</RouterLink>
        </div>
      </section>

      <section class="school-photo panel reveal">
        <SafeImage :src="campusImage.path" :alt="campusImage.alt" kind="team" />
        <div>
          <span>校园实景 · 拓展配图</span>
          <h2>{{ campusImage.title }}</h2>
          <p>{{ campusImage.description }}</p>
          <small>作者：{{ campusImage.author }} · {{ campusImage.license }} · {{ campusImage.processing }}</small>
          <a :href="campusImage.sourceUrl" target="_blank" rel="noopener noreferrer">查看 Wikimedia Commons 原始文件页</a>
        </div>
      </section>

      <div class="school-grid">
        <article v-for="item in data.sections" :key="item.title" class="panel school-card reveal">
          <span>{{ item.category }}</span>
          <h2>{{ item.title }}</h2>
          <p>{{ item.content }}</p>
        </article>
      </div>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { http } from '../api/http'
import PageHero from '../components/PageHero.vue'
import SafeImage from '../components/SafeImage.vue'
import { offlineSchool } from '../data/offlineFallbacks'
import { supplementalImages } from '../data/supplementalImages'

const data = ref(offlineSchool)
const campusImage = supplementalImages.sduQingdaoCampus
onMounted(async () => {
  try {
    const payload = (await http.get('/api/school')).data
    if (payload && Array.isArray(payload.sections) && payload.sections.length) data.value = payload
  } catch {
    data.value = offlineSchool
  }
})
</script>

<style scoped>
.school-hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 24px;
  padding: 36px;
  color: #fff8e6;
  background:
    linear-gradient(120deg, rgba(84, 16, 21, .94), rgba(25, 65, 86, .82)),
    url('/assets/images/maogongshan/resource-021.jpg') center/cover;
}

.school-hero h1 {
  margin: 0;
  font-size: clamp(34px, 6vw, 70px);
}

.school-hero p {
  line-height: 1.85;
}

.school-links {
  display: grid;
  gap: 10px;
  align-content: center;
}

.school-links a {
  padding: 12px 14px;
  color: #fff8e6;
  background: rgba(255, 248, 229, .13);
  border: 1px solid rgba(255, 248, 229, .25);
  border-radius: 12px;
}

.school-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
  margin-top: 28px;
}

.school-photo {
  display: grid;
  grid-template-columns: minmax(280px, .9fr) minmax(0, 1.1fr);
  gap: 26px;
  padding: 20px;
  margin-top: 28px;
}
.school-photo :deep(.safe-image) { min-height: 320px; border-radius: 8px; }
.school-photo > div { display: grid; align-content: center; gap: 10px; }
.school-photo span { color: #24708a; font-weight: 800; }
.school-photo h2 { margin: 0; color: var(--red-dark); }
.school-photo p { color: var(--muted); line-height: 1.85; }
.school-photo small { color: #675c54; }
.school-photo a { color: var(--red); font-weight: 800; }

.school-card {
  padding: 24px;
}

.school-card span {
  color: var(--gold);
  font-weight: 700;
}

.school-card h2 {
  color: var(--red-dark);
}

.school-card p {
  color: var(--muted);
  line-height: 1.9;
}

@media (max-width: 900px) {
  .school-hero,
  .school-photo,
  .school-grid {
    grid-template-columns: 1fr;
  }
}
</style>
