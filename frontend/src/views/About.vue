<template>
  <div>
    <PageHero
      title="关于毛公山"
      subtitle="这里用于集中说明毛公山位置、自然风景、红色文化价值、资源库建设意义和数据考证要求。"
      image="/assets/images/scenery/maogongshan-mountain.jpg"
    />
    <main class="page">
      <section class="about-grid">
        <article class="panel about-card reveal">
          <SectionTitle eyebrow="项目定位" title="课程展示与社会实践数字平台" />
          <p>本项目以“青岛市城阳区毛公山红色文化数字资源库”为主题，面向课程答辩、社会实践成果展示和后续资料管理。系统采用前后端分离与 SQLite 数据库，便于本地运行和扩展维护。</p>
          <p>平台优先收录来源清晰的公开资料和已登记版权说明的图片，涉及历史事实的内容在详情页保留来源链接，便于后续继续核验和补充。</p>
        </article>
        <article class="panel about-card reveal">
          <SectionTitle eyebrow="建设意义" title="让资料可展示、可查询、可管理" />
          <p>资源库将历史事件、人物故事、风景图片、景点导览、新闻报道、研究文章和口述历史统一纳入数据库，支持关键词检索、分类筛选、详情阅读和后台维护。</p>
          <p>后续可逐步接入地方志、档案馆、景区管理部门、公开报道和实地调研授权材料，形成更可靠的数字化展示平台。</p>
        </article>
      </section>

      <SectionTitle title="景点与资源点" desc="以下点位依据公开资料整理，具体坐标和路线以高德地图实时导航及现场标识为准。" />
      <div class="grid grid-4">
        <article v-for="spot in spots" :key="spot.id" class="spot-card reveal">
          <SafeImage :src="spot.image_url" :alt="spot.name" />
          <div>
            <el-tag type="danger">{{ spot.type }}</el-tag>
            <h3>{{ spot.name }}</h3>
            <p>{{ spot.description }}</p>
            <span>{{ spot.route_hint }}</span>
          </div>
        </article>
      </div>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { http } from '../api/http'
import PageHero from '../components/PageHero.vue'
import SectionTitle from '../components/SectionTitle.vue'
import SafeImage from '../components/SafeImage.vue'

const spots = ref([])

onMounted(async () => {
  try { spots.value = (await http.get('/api/scenic-spots')).data } catch { spots.value = [] }
})
</script>

<style scoped>
.about-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 46px;
}

.about-card {
  padding: 24px;
}

.about-card p {
  color: var(--muted);
  line-height: 1.9;
}

.spot-card {
  overflow: hidden;
  background: #fffaf0;
  border: 1px solid var(--line);
  border-radius: 12px;
  box-shadow: 0 14px 30px rgba(84, 16, 21, .08);
}

.spot-card :deep(.safe-image) {
  width: 100%;
  height: 150px;
  object-fit: cover;
}

.spot-card div {
  padding: 14px;
}

.spot-card h3 {
  color: var(--red-dark);
}

.spot-card p,
.spot-card span {
  color: var(--muted);
  line-height: 1.7;
}

@media (max-width: 820px) {
  .about-grid {
    grid-template-columns: 1fr;
  }
}
</style>
