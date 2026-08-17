<template>
  <div>
    <PageHero
      title="毛公山概览"
      subtitle="从位置、山体、风景、路线、文化价值和教育价值认识毛公山，并进入多个二级专题继续阅读。"
      image="/assets/images/generated/overview-forest-v2-wide.webp"
      mobile-image="/assets/images/generated/overview-forest-v2-mobile.webp"
      eyebrow="Maogongshan Overview"
    />
    <main class="page">
      <section class="overview-lead panel reveal">
        <SafeImage src="/assets/images/scenery/xifu-autumn.jpg" alt="惜福镇周边自然风光" />
        <div>
          <p class="eyebrow">核心概览</p>
          <h1>把自然景观、地方文化和数字导览放在同一个入口</h1>
          <p>
            毛公山概览页用于建立用户的第一层认知：它在哪里、可以看什么、如何游览、资料从哪里来，以及为什么适合建设红色文化数字资源库。
            页面内容均由后端数据库和结构化专题数据支撑，避免只停留在静态介绍。
          </p>
          <div class="quick-topic-row">
            <RouterLink v-for="item in topics" :key="item.to" :to="item.to">{{ item.title }}</RouterLink>
          </div>
        </div>
      </section>

      <section class="overview-grid">
        <article v-for="item in data.sections" :key="item.title" class="panel overview-card reveal">
          <h2>{{ item.title }}</h2>
          <p>{{ item.content }}</p>
        </article>
      </section>

      <SectionTitle title="概览图集" desc="从真实图片资源库中选取毛公山、惜福镇及周边自然文化影像，点击可进入图片详情。" />
      <div class="overview-gallery">
        <RouterLink v-for="img in data.images" :key="img.id" :to="`/images/${img.id}`">
          <SafeImage :src="img.image_url" :alt="img.title || img.name" />
          <span>{{ img.title || img.name }}</span>
        </RouterLink>
      </div>

      <SectionTitle title="路线与点位" desc="继续进入地图导览或三维沙盘，查看景点、路线、红色资源点和服务设施。" />
      <div class="grid grid-3">
        <article v-for="route in data.routes" :key="route.id" class="panel route-card reveal">
          <h3>{{ route.name }}</h3>
          <p>{{ route.summary }}</p>
          <span>{{ route.start_point }} → {{ route.end_point }}</span>
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
import SectionTitle from '../components/SectionTitle.vue'
import SafeImage from '../components/SafeImage.vue'
import { offlineOverview } from '../data/offlineFallbacks'

const data = ref(offlineOverview)
const topics = [
  { title: '地理环境', to: '/overview/geography' },
  { title: '名称由来', to: '/overview/name-origin' },
  { title: '自然景观', to: '/overview/nature' },
  { title: '文化价值', to: '/overview/culture' },
  { title: '游览路线', to: '/overview/routes' }
]

onMounted(async () => {
  try {
    const payload = (await http.get('/api/platform-overview')).data
    data.value = {
      sections: payload?.sections?.length ? payload.sections : offlineOverview.sections,
      images: payload?.images || [],
      routes: payload?.routes || [],
      spots: payload?.spots || []
    }
  } catch {
    data.value = offlineOverview
  }
})
</script>

<style scoped>
.overview-lead {
  display: grid;
  grid-template-columns: .95fr 1.05fr;
  gap: 24px;
  overflow: hidden;
  margin-bottom: 28px;
}

.overview-lead :deep(.safe-image) {
  width: 100%;
  height: 100%;
  min-height: 320px;
  object-fit: cover;
}

.overview-lead div {
  padding: 30px;
}

.overview-lead h1 {
  margin: 0;
  color: var(--red-dark);
  font-size: clamp(28px, 4vw, 46px);
}

.overview-lead p {
  color: var(--muted);
  line-height: 1.9;
}

.quick-topic-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.quick-topic-row a {
  padding: 10px 14px;
  color: var(--red-dark);
  background: #fff4d7;
  border: 1px solid #ead18d;
  border-radius: 999px;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
  margin-bottom: 44px;
}

.overview-card,
.route-card {
  padding: 22px;
  background: linear-gradient(135deg, #fffaf0, #eef7f4);
}

.overview-card h2,
.route-card h3 {
  color: var(--red-dark);
}

.overview-card p,
.route-card p,
.route-card span {
  color: var(--muted);
  line-height: 1.85;
}

.overview-gallery {
  columns: 4 220px;
  column-gap: 16px;
  margin-bottom: 40px;
}

.overview-gallery a {
  display: block;
  break-inside: avoid;
  margin-bottom: 16px;
  overflow: hidden;
  color: #fff8e6;
  background: #171311;
  border-radius: 14px;
}

.overview-gallery img {
  width: 100%;
  display: block;
  min-height: 180px;
  object-fit: cover;
}

.overview-gallery span {
  display: block;
  padding: 12px;
}

@media (max-width: 900px) {
  .overview-lead,
  .overview-grid {
    grid-template-columns: 1fr;
  }
}
</style>
