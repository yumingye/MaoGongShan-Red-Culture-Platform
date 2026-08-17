<template>
  <div>
    <PageHero
      title="团队介绍"
      subtitle="山软寻脉·毛公山数字调研实践团成员、职责与实践现场。"
      image="/assets/images/generated/youth-fieldwork-v2-wide.webp"
      mobile-image="/assets/images/generated/youth-fieldwork-v2-mobile.webp"
      eyebrow="山东大学软件学院 · 青年实践"
    />
    <main class="page">
      <section class="team-overview panel reveal">
        <SafeImage :src="teamPhoto.detail_url" :alt="teamPhoto.alt" />
        <div>
          <p class="eyebrow">山软寻脉 · 毛公山数字调研实践团</p>
          <h1>用软件工程方法记录现场、整理资料、连接公众</h1>
          <p>{{ teamPhoto.description }}</p>
          <p>团队以资料整理、实地调研、影像记录和平台开发协同推进项目建设。</p>
          <el-button type="primary" @click="$router.push('/research')">查看实践调研</el-button>
        </div>
      </section>

      <h2 class="section-heading">团队成员与分工</h2>
      <div class="grid grid-3">
        <article v-for="item in team" :key="item.id" class="panel member-card reveal">
          <div class="member-initial" aria-hidden="true">{{ item.name?.slice(0, 1) || '团' }}</div>
          <h3>{{ item.name }}</h3>
          <p>{{ item.college }}</p>
          <el-tag type="danger">{{ item.role }}</el-tag>
          <p class="subtle">{{ item.responsibility }}</p>
          <p class="mini-meta">{{ item.public_bio }}</p>
        </article>
      </div>

      <h2 class="section-heading">团队现场工作记录</h2>
      <div class="team-activity-grid">
        <RouterLink v-for="photo in activityPhotos" :key="photo.slug" :to="photo.detail_link" class="activity-photo reveal">
          <SafeImage :src="photo.thumbnail_url" :alt="photo.alt" />
          <div>
            <strong>{{ photo.title }}</strong>
            <span>{{ photo.description }}</span>
          </div>
        </RouterLink>
      </div>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { http } from '../api/http'
import PageHero from '../components/PageHero.vue'
import SafeImage from '../components/SafeImage.vue'
import photoLibrary from '../data/maogongshanPhotos.json'
import { offlineTeamMembers } from '../data/offlineFallbacks'

const team = ref(offlineTeamMembers.map((item) => ({ ...item })))
const teamPhoto = photoLibrary.images.find((item) => item.group === '山东大学软件学院团队')
const activityPhotos = photoLibrary.images
  .filter((item) => item.group === '社会实践与调研活动')
  .slice(0, 6)
onMounted(async () => {
  try {
    const payload = (await http.get('/api/project')).data.team
    if (Array.isArray(payload) && payload.length) team.value = payload
  } catch {
    team.value = offlineTeamMembers.map((item) => ({ ...item }))
  }
})
</script>

<style scoped>
.team-overview {
  display: grid;
  grid-template-columns: minmax(0, 1.12fr) minmax(320px, .88fr);
  gap: 30px;
  align-items: center;
  padding: 18px;
  background: linear-gradient(135deg, #eef7f9, #fffaf0);
}
.team-overview :deep(.safe-image) { min-height: 390px; border-radius: 12px; }
.team-overview > div { padding: 24px; }
.team-overview h1 { margin: 0; color: #164b62; font-size: clamp(28px, 4vw, 48px); }
.team-overview p { color: var(--muted); line-height: 1.9; }
.section-heading { margin: 52px 0 20px; color: var(--red-dark); font-size: clamp(26px, 3vw, 38px); }
.member-card { padding: 24px; text-align: center; }
.member-initial {
  display: grid;
  place-items: center;
  width: 82px;
  height: 82px;
  margin: 0 auto;
  color: #fff8e6;
  font-size: 30px;
  font-weight: 900;
  background: linear-gradient(145deg, var(--red), #245f76);
  border: 5px solid #fff;
  border-radius: 50%;
  box-shadow: 0 10px 24px rgba(84, 16, 21, .18);
}
.member-card h3 { color: var(--red-dark); }
.team-activity-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}
.activity-photo {
  position: relative;
  min-height: 300px;
  overflow: hidden;
  color: #fff8e6;
  border-radius: 12px;
  box-shadow: var(--shadow);
}
.activity-photo :deep(.safe-image) { position: absolute; inset: 0; }
.activity-photo :deep(img) { transition: transform .35s ease; }
.activity-photo:hover :deep(img) { transform: scale(1.05); }
.activity-photo > div {
  position: absolute;
  z-index: 1;
  inset: auto 0 0;
  display: grid;
  gap: 6px;
  padding: 48px 16px 16px;
  background: linear-gradient(0deg, rgba(22, 25, 27, .92), transparent);
}
.activity-photo span { color: rgba(255, 248, 230, .76); font-size: 13px; line-height: 1.6; }
@media (max-width: 900px) {
  .team-overview,
  .team-activity-grid { grid-template-columns: 1fr; }
  .team-overview :deep(.safe-image) { min-height: 280px; }
}
</style>
