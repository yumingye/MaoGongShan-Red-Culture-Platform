<template>
  <div>
    <PageHero
      v-if="image"
      :title="image.title"
      :subtitle="image.description"
      :image="assetUrl(image.image_url)"
      eyebrow="数字影像典藏"
    />
    <main class="page" v-loading="loading">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: '/scenery' }">全景图库</el-breadcrumb-item>
        <el-breadcrumb-item>{{ image?.title || '图片详情' }}</el-breadcrumb-item>
      </el-breadcrumb>

      <el-empty v-if="!loading && !image" description="图片不存在或加载失败">
        <el-button type="primary" @click="$router.push('/scenery')">返回全景图库</el-button>
      </el-empty>

      <article v-if="image" class="image-detail">
        <section class="image-stage panel reveal">
          <SafeImage :src="image.image_url" :alt="image.title || '毛公山图库大图'" fit="contain" loading="eager" />
        </section>

        <aside class="image-info panel reveal">
          <p class="eyebrow">{{ image.category || '图片资料' }}</p>
          <h1>{{ image.title }}</h1>
          <p class="lead">{{ image.description }}</p>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="拍摄/发布时间">{{ image.captured_at || '见来源页面' }}</el-descriptions-item>
            <el-descriptions-item label="地点">{{ image.location || '青岛城阳及扩展参考区域' }}</el-descriptions-item>
            <el-descriptions-item label="来源">{{ image.source_name || '来源已记录' }}</el-descriptions-item>
            <el-descriptions-item label="版权说明">{{ image.copyright_note || '仅用于课程展示和社会实践演示，商业传播前请确认授权。' }}</el-descriptions-item>
          </el-descriptions>
          <div class="detail-actions">
            <el-button type="primary" @click="toggle">{{ favoriteLabel }}</el-button>
            <el-button plain @click="copyShare">复制分享链接</el-button>
            <el-button v-if="image.source_url" plain tag="a" :href="image.source_url" target="_blank">查看来源</el-button>
            <el-button plain @click="$router.push('/favorites')">查看收藏</el-button>
          </div>
        </aside>
      </article>

      <SectionTitle v-if="relatedImages.length" title="相关图片" desc="继续浏览毛公山、城阳和实践主题影像资料。" />
      <div v-if="relatedImages.length" class="masonry small">
        <article v-for="item in relatedImages" :key="item.id" class="museum-card reveal" @click="$router.push(detailPath(item))">
          <SafeImage :src="item.image_url" :alt="item.title || '相关图片'" />
          <div>
            <span>{{ item.category || '图片资料' }}</span>
            <h3>{{ item.title }}</h3>
          </div>
        </article>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { http, assetUrl } from '../api/http'
import PageHero from '../components/PageHero.vue'
import SectionTitle from '../components/SectionTitle.vue'
import SafeImage from '../components/SafeImage.vue'
import { addRecentView, isFavorite, toggleFavorite } from '../utils/library'
import { copyText } from '../utils/clipboard'

const route = useRoute()
const image = ref(null)
const loading = ref(false)
const favoriteVersion = ref(0)
const favoriteKey = computed(() => image.value ? `image:${image.value.id}` : '')
const favoriteLabel = computed(() => {
  favoriteVersion.value
  return favoriteKey.value && isFavorite(favoriteKey.value) ? '取消收藏' : '收藏图片'
})
const relatedImages = computed(() => image.value?.related?.filter((item) => item?.image_url) || [])

function payload() {
  return {
    key: favoriteKey.value,
    type: '图片资料',
    title: image.value.title,
    summary: image.value.description,
    url: detailPath(image.value)
  }
}

function detailPath(item) {
  return item?.slug ? `/photos/${item.slug}` : `/images/${item?.id}`
}

async function load() {
  loading.value = true
  try {
    const endpoint = route.params.slug
      ? `/api/images/slug/${encodeURIComponent(route.params.slug)}`
      : `/api/images/${route.params.id}`
    image.value = (await http.get(endpoint)).data
    addRecentView(payload())
  } catch {
    image.value = null
  } finally {
    loading.value = false
  }
}

function toggle() {
  const added = toggleFavorite(payload())
  favoriteVersion.value += 1
  ElMessage.success(added ? '已收藏图片' : '已取消收藏')
}

async function copyShare() {
  const copied = await copyText(window.location.href)
  copied ? ElMessage.success('分享链接已复制') : ElMessage.warning('复制失败，请手动复制地址栏链接')
}

watch(() => [route.params.id, route.params.slug], load)
onMounted(load)
</script>

<style scoped>
.image-detail {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(340px, .75fr);
  gap: 24px;
  margin-top: 22px;
}

.image-stage {
  padding: 14px;
  background: #171311;
}

.image-stage :deep(.safe-image),
.image-stage :deep(img) {
  width: 100%;
  height: min(72vh, 680px);
  object-fit: contain;
}

.image-info {
  padding: 24px;
}

.image-info h1 {
  margin-top: 0;
  color: var(--red-dark);
  font-size: clamp(28px, 4vw, 44px);
}

.lead {
  color: var(--muted);
  line-height: 1.9;
}

.detail-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 18px;
}

.masonry.small {
  columns: 3 260px;
  column-gap: 18px;
}

.museum-card {
  break-inside: avoid;
  margin-bottom: 18px;
  overflow: hidden;
  cursor: pointer;
  background: #fffaf0;
  border: 1px solid var(--line);
  border-radius: 14px;
  box-shadow: 0 14px 34px rgba(84, 16, 21, .1);
}

.museum-card :deep(.safe-image),
.museum-card :deep(img) {
  width: 100%;
  min-height: 210px;
  display: block;
  object-fit: cover;
}

.museum-card div {
  padding: 14px;
}

.museum-card span {
  color: var(--gold);
  font-size: 13px;
}

.museum-card h3 {
  margin: 6px 0 0;
  color: var(--red-dark);
}

@media (max-width: 900px) {
  .image-detail {
    grid-template-columns: 1fr;
  }
}
</style>
