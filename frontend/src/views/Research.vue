<template>
  <div>
    <PageHero
      title="实践调研"
      subtitle="展示山软寻脉·毛公山数字调研实践团的路线、方法、日志、成果与青年感悟。"
      :image="researchPhotos[0]?.detail_url"
      eyebrow="Field Research"
    />
    <main class="page">
      <section class="research-intro panel reveal">
        <div>
          <p class="eyebrow">从实地走访到数字建库</p>
          <h1>让社会实践材料真正进入可检索、可讲解、可复用的平台</h1>
          <p>
            实践调研围绕资料查阅、路线梳理、图像采集、访谈记录、数据整理、平台开发和成果展示展开。
            重点不是“拍几张照片”，而是用软件工程方法把文化资源整理成结构化数据。
          </p>
        </div>
        <div class="quick-links">
          <RouterLink to="/research/topic/route">调研路线</RouterLink>
          <RouterLink to="/research/topic/interviews">访谈记录</RouterLink>
          <RouterLink to="/research/topic/methods">调研方法</RouterLink>
          <RouterLink to="/research/topic/reflections">青年感悟</RouterLink>
          <RouterLink to="/achievements">实践成果</RouterLink>
          <RouterLink to="/team">团队成员</RouterLink>
        </div>
      </section>

      <SectionTitle
        title="现场调研图像时间线"
        desc="原始照片未附带可靠拍摄日期，因此不编造具体日期；时间线按资料采集流程组织，并明确标注时间信息状态。"
      />
      <section class="field-timeline">
        <article v-for="(photo, index) in researchPhotos" :key="photo.slug" class="field-node reveal">
          <div class="field-index">{{ String(index + 1).padStart(2, '0') }}</div>
          <RouterLink :to="photo.detail_link" class="field-photo">
            <SafeImage :src="photo.thumbnail_url" :alt="photo.alt" />
          </RouterLink>
          <div class="field-copy">
            <span>拍摄日期未标注 · 毛公山红色文化展陈空间</span>
            <h3>{{ photo.title }}</h3>
            <p>{{ photo.description }}</p>
            <RouterLink :to="photo.detail_link">查看照片档案</RouterLink>
          </div>
        </article>
      </section>

      <SectionTitle title="实践日志" desc="每篇日志可进入独立详情页，查看地点、分类、正文、来源和相关推荐。" />
      <div class="grid grid-3">
        <article v-for="item in list" :key="item.id" class="log-card reveal" @click="$router.push(`/research/${item.id}`)">
          <SafeImage :src="item.image" :alt="item.title" />
          <div>
            <span>{{ item.date }} · {{ item.category }}</span>
            <h3>{{ item.title }}</h3>
            <p>{{ item.summary }}</p>
          </div>
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
import photoLibrary from '../data/maogongshanPhotos.json'
import researchLogs from '../data/research_logs.json'

const list = ref(researchLogs)
const researchPhotos = photoLibrary.images
  .filter((item) => item.group === '社会实践与调研活动')

onMounted(async () => {
  try {
    const rows = (await http.get('/api/research-logs')).data
    if (Array.isArray(rows) && rows.length) list.value = rows
  } catch {
    list.value = researchLogs
  }
})
</script>

<style scoped>
.research-intro {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 24px;
  padding: 34px;
  color: #fff8e6;
  background:
    linear-gradient(120deg, rgba(84, 16, 21, .92), rgba(25, 65, 86, .78)),
    url('/assets/images/culture/xifu-cultural-tourism.jpg') center/cover;
}

.research-intro h1 {
  margin: 0;
  font-size: clamp(30px, 5vw, 58px);
}

.research-intro p {
  max-width: 850px;
  line-height: 1.9;
}

.quick-links {
  display: grid;
  gap: 10px;
  align-content: center;
}

.quick-links a {
  padding: 12px 14px;
  color: #fff;
  text-decoration: none;
  background: rgba(255, 255, 255, .14);
  border: 1px solid rgba(255, 255, 255, .24);
  border-radius: 12px;
}

.field-timeline {
  position: relative;
  display: grid;
  gap: 18px;
  margin-bottom: 54px;
}

.field-timeline::before {
  position: absolute;
  top: 20px;
  bottom: 20px;
  left: 29px;
  width: 2px;
  background: linear-gradient(var(--red), #245f76);
  content: '';
}

.field-node {
  position: relative;
  display: grid;
  grid-template-columns: 60px 240px minmax(0, 1fr);
  gap: 20px;
  align-items: center;
  min-height: 170px;
  padding: 14px 20px 14px 0;
  background: linear-gradient(100deg, rgba(255, 250, 240, .95), rgba(237, 247, 249, .94));
  border: 1px solid var(--line);
  border-radius: 14px;
  box-shadow: 0 12px 30px rgba(36, 76, 90, .08);
}

.field-index {
  z-index: 1;
  display: grid;
  place-items: center;
  width: 46px;
  height: 46px;
  margin-left: 7px;
  color: #fff;
  font-weight: 900;
  background: var(--red);
  border: 5px solid #fffaf0;
  border-radius: 50%;
}

.field-photo :deep(.safe-image) {
  height: 150px;
  min-height: 150px;
  border-radius: 9px;
}

.field-copy span {
  color: #24708a;
  font-size: 12px;
}

.field-copy h3 {
  margin: 7px 0;
  color: var(--red-dark);
}

.field-copy p {
  margin: 0 0 8px;
  color: var(--muted);
  line-height: 1.75;
}

.field-copy a {
  color: var(--red);
  font-weight: 800;
}

.log-card {
  overflow: hidden;
  cursor: pointer;
  background: #fffaf0;
  border: 1px solid var(--line);
  border-radius: 14px;
  box-shadow: 0 14px 34px rgba(84, 16, 21, .1);
  transition: transform .2s ease, box-shadow .2s ease;
}

.log-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow);
}

.log-card img {
  width: 100%;
  height: 210px;
  object-fit: cover;
}

.log-card div {
  padding: 16px;
}

.log-card span {
  color: var(--gold);
  font-size: 13px;
}

.log-card h3 {
  color: var(--red-dark);
}

.log-card p {
  color: var(--muted);
  line-height: 1.75;
}

@media (max-width: 900px) {
  .research-intro {
    grid-template-columns: 1fr;
  }

  .field-node {
    grid-template-columns: 60px minmax(0, 1fr);
  }

  .field-photo {
    grid-column: 2;
  }

  .field-copy {
    grid-column: 2;
  }
}

@media (max-width: 560px) {
  .field-node {
    grid-template-columns: 48px minmax(0, 1fr);
    gap: 12px;
    padding-right: 12px;
  }

  .field-timeline::before {
    left: 23px;
  }

  .field-index {
    width: 38px;
    height: 38px;
    margin-left: 4px;
    font-size: 12px;
  }
}
</style>
