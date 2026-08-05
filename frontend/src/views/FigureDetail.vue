<template>
  <div>
    <PageHero v-if="figure" :title="figure.name" :subtitle="figure.biography" :image="assetUrl(figure.photo_url)" />
    <main class="page" v-loading="loading">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: '/figures' }">历史人物</el-breadcrumb-item>
        <el-breadcrumb-item>{{ figure?.name || '人物详情' }}</el-breadcrumb-item>
      </el-breadcrumb>

      <el-empty v-if="!loading && !figure" description="人物资料不存在或加载失败" />
      <article v-if="figure" class="figure-detail panel reveal">
        <figure class="portrait">
          <SafeImage :src="figure.photo_url" :alt="`${figure.name}人物照片：${figure.photo_note}`" show-status />
          <figcaption><el-tag effect="dark">{{ figure.photo_type || '人物照片' }}</el-tag><p>{{ figure.photo_note }}</p></figcaption>
        </figure>
        <section>
          <h1>{{ figure.name }}</h1>
          <div class="meta-line">
            <el-tag>{{ figure.active_period || '公开资料所示时期' }}</el-tag>
            <el-tag :type="figure.verified ? 'success' : 'warning'">{{ figure.verification_status || '公开资料' }}</el-tag>
          </div>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="人物简介">{{ figure.biography }}</el-descriptions-item>
            <el-descriptions-item label="主要事迹">{{ figure.deeds }}</el-descriptions-item>
            <el-descriptions-item label="与毛公山或城阳区关系">{{ figure.relation_to_maogongshan }}</el-descriptions-item>
            <el-descriptions-item label="相关事件">{{ figure.related_events }}</el-descriptions-item>
            <el-descriptions-item label="资料来源">{{ figure.source }}</el-descriptions-item>
            <el-descriptions-item label="照片来源"><a v-if="figure.source_url" :href="figure.source_url" target="_blank" rel="noopener noreferrer">打开原始文件页</a><span v-else>见资料来源</span></el-descriptions-item>
            <el-descriptions-item label="版权说明">{{ figure.copyright_note }}</el-descriptions-item>
          </el-descriptions>
          <el-button type="primary" plain class="back-btn" @click="$router.push('/figures')">返回人物列表</el-button>
        </section>
      </article>

      <SectionTitle v-if="figure?.related?.length" title="相关历史资料" desc="人物资料可与历史事件、口述历史和研究文章进一步关联。" />
      <div v-if="figure?.related?.length" class="grid grid-2">
        <router-link v-for="item in figure.related" :key="item.id" class="related-card reveal" :to="`/events/${item.id}`">
          <strong>{{ item.title }}</strong>
          <span>{{ item.event_time }}</span>
          <p>{{ item.summary }}</p>
        </router-link>
      </div>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { http, assetUrl } from '../api/http'
import PageHero from '../components/PageHero.vue'
import SectionTitle from '../components/SectionTitle.vue'
import SafeImage from '../components/SafeImage.vue'

const route = useRoute()
const figure = ref(null)
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    figure.value = (await http.get(`/api/figures/${route.params.id}`)).data
  } catch {
    figure.value = null
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.figure-detail {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 26px;
  padding: 24px;
  margin-top: 22px;
}

.portrait { margin: 0; }
.portrait :deep(.safe-image) {
  width: 100%;
  aspect-ratio: 4 / 5;
  object-fit: cover;
  border-radius: 12px;
}
.portrait figcaption { padding: 12px; background: #fff6df; border: 1px solid var(--line); border-top: 0; }
.portrait figcaption p { margin: 8px 0 0; color: var(--muted); line-height: 1.65; font-size: 13px; }
.figure-detail a { color: var(--red); font-weight: 700; }

.figure-detail h1 {
  margin-top: 0;
  color: var(--red-dark);
  font-size: 38px;
}

.back-btn {
  margin-top: 18px;
}

.related-card {
  padding: 18px;
  background: #fffaf0;
  border: 1px solid var(--line);
  border-radius: 12px;
  box-shadow: 0 12px 28px rgba(84, 16, 21, .08);
}

.related-card strong {
  color: var(--red-dark);
}

.related-card span {
  display: block;
  margin-top: 6px;
  color: var(--gold);
}

.related-card p {
  color: var(--muted);
  line-height: 1.7;
}

@media (max-width: 760px) {
  .figure-detail {
    grid-template-columns: 1fr;
  }
}
</style>
