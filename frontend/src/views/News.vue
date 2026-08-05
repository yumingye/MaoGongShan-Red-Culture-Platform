<template>
  <div>
    <PageHero
      title="新闻与活动"
      subtitle="汇集毛公山现场调研、文化展陈参观和团队实践图像；未附可靠日期的素材不虚构新闻时间。"
      :image="items[0]?.detail_url"
      eyebrow="Activity Archive"
    />
    <main class="page">
      <p class="data-note">
        本页为项目活动影像纪实，不将未标注日期的现场照片包装成新闻报道。图片标题、说明和人物标注均以可确认信息为限。
      </p>
      <div class="news-filters">
        <button
          v-for="value in filters"
          :key="value"
          :class="{ active: selected === value }"
          type="button"
          @click="selected = value"
        >
          {{ value }}
        </button>
      </div>
      <section class="news-layout">
        <RouterLink
          v-for="(item, index) in filteredItems"
          :key="item.slug"
          :to="item.detail_link"
          class="news-story reveal"
          :class="{ featured: index === 0 }"
        >
          <SafeImage :src="item.thumbnail_url" :alt="item.alt" />
          <div>
            <span>{{ item.group }} · 日期未标注</span>
            <h2>{{ item.title }}</h2>
            <p>{{ item.description }}</p>
            <strong>查看图片档案与来源说明</strong>
          </div>
        </RouterLink>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import PageHero from '../components/PageHero.vue'
import SafeImage from '../components/SafeImage.vue'
import photoLibrary from '../data/maogongshanPhotos.json'

const filters = ['全部', '调研活动', '团队实践', '文化参观']
const selected = ref('全部')
const items = photoLibrary.images.filter((item) => [
  '社会实践与调研活动',
  '山东大学软件学院团队',
  '红色文化与党史'
].includes(item.group))

const filteredItems = computed(() => {
  if (selected.value === '全部') return items
  const groupMap = {
    调研活动: '社会实践与调研活动',
    团队实践: '山东大学软件学院团队',
    文化参观: '红色文化与党史'
  }
  return items.filter((item) => item.group === groupMap[selected.value])
})
</script>

<style scoped>
.news-filters {
  display: flex;
  gap: 10px;
  margin: 24px 0;
  overflow-x: auto;
}

.news-filters button {
  flex: none;
  padding: 10px 16px;
  color: #245f76;
  cursor: pointer;
  background: #eef7f9;
  border: 1px solid #bcd3da;
  border-radius: 999px;
}

.news-filters button.active {
  color: #fff;
  background: var(--red);
  border-color: var(--red);
}

.news-layout {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
}

.news-story {
  display: grid;
  overflow: hidden;
  background: #fffaf0;
  border: 1px solid var(--line);
  border-radius: 12px;
  box-shadow: 0 14px 34px rgba(84, 16, 21, .1);
  transition: transform .25s ease, box-shadow .25s ease;
}

.news-story:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow);
}

.news-story :deep(.safe-image) {
  min-height: 230px;
}

.news-story > div {
  padding: 18px;
}

.news-story span {
  color: #24708a;
  font-size: 12px;
}

.news-story h2 {
  margin: 8px 0;
  color: var(--red-dark);
  font-size: 22px;
}

.news-story p {
  color: var(--muted);
  line-height: 1.75;
}

.news-story strong {
  color: var(--red);
  font-size: 13px;
}

.news-story.featured {
  grid-column: span 2;
  grid-template-columns: 1.2fr .8fr;
}

.news-story.featured :deep(.safe-image) {
  min-height: 390px;
}

.news-story.featured > div {
  display: grid;
  align-content: center;
  padding: 30px;
}

@media (max-width: 900px) {
  .news-layout {
    grid-template-columns: 1fr 1fr;
  }

  .news-story.featured {
    grid-column: 1 / -1;
  }
}

@media (max-width: 620px) {
  .news-layout,
  .news-story.featured {
    grid-template-columns: 1fr;
  }

  .news-story.featured {
    grid-column: auto;
  }

  .news-story.featured :deep(.safe-image) {
    min-height: 260px;
  }
}
</style>
