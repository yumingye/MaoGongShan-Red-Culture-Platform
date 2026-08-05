<template>
  <div>
    <PageHero
      title="毛公山全景图库"
      subtitle="所有图片均从后端图片资源库读取；如原图异常，会自动显示本地真实风景备用图，避免空白、黑屏或破损图标。"
      image="/assets/images/scenery/maogongshan-sunset-rock.png"
      eyebrow="数字博物馆 · 影像典藏"
    />

    <main class="page">
      <section class="gallery-toolbar panel reveal">
        <div>
          <p class="eyebrow">Image Archive</p>
          <h2>真实影像瀑布流</h2>
          <p>图片资源保留来源、地点、时间与版权说明；页面不会出现空图，加载失败时统一切换到本地备用照片。</p>
        </div>
        <el-input v-model="keyword" clearable placeholder="搜索图片名称、地点、来源" @keyup.enter="load">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
      </section>

      <div class="category-rail">
        <button
          v-for="item in categories"
          :key="item"
          :class="{ active: category === item }"
          @click="selectCategory(item)"
        >
          {{ item }}
        </button>
      </div>

      <section class="gallery-topics reveal">
        <RouterLink to="/gallery/maogongshan">毛公山景色</RouterLink>
        <RouterLink to="/gallery/red-culture">红色文化影像</RouterLink>
        <RouterLink to="/gallery/research">调研实践影像</RouterLink>
        <RouterLink to="/gallery/school">山软青年图集</RouterLink>
      </section>

      <el-alert v-if="error" :title="error" type="error" show-icon class="error-alert" />

      <section v-loading="loading" class="museum-wall">
        <article
          v-for="(item, index) in safeList"
          :key="item.id"
          class="museum-photo reveal"
          tabindex="0"
          @click="openPreview(index)"
          @keyup.enter="openPreview(index)"
        >
          <SafeImage :src="item.safeUrl" :alt="item.title || '毛公山图库照片'" />
          <div class="photo-mask">
            <span>{{ item.category || '图片资料' }}</span>
            <h3>{{ item.title }}</h3>
            <p>{{ item.location || '青岛城阳及扩展参考区域' }}</p>
            <div class="photo-actions">
              <button type="button" @click.stop="openPreview(index)">放大预览</button>
              <button type="button" @click.stop="$router.push(photoDetailPath(item))">查看详情</button>
            </div>
          </div>
        </article>
      </section>

      <el-empty v-if="!loading && !safeList.length" description="当前条件未匹配图片，请调整分类或关键词。" />

      <SectionTitle title="相关景点推荐" desc="公开资料整理的毛公山景点、路线与周边文旅点位，可进入地点详情继续浏览。" />
      <div class="spot-showcase">
        <article v-for="spot in safeSpots" :key="spot.id" class="spot-card reveal" @click="$router.push(`/places/${spot.id}`)">
          <SafeImage :src="spot.safeUrl" :alt="spot.name || '景点照片'" />
          <div>
            <el-tag type="danger">{{ spot.type || '地点资源' }}</el-tag>
            <h3>{{ spot.name }}</h3>
            <p>{{ spot.description }}</p>
            <span>{{ spot.address }}</span>
          </div>
        </article>
      </div>
    </main>

    <Teleport to="body">
      <Transition name="lightbox">
        <div v-if="previewIndex >= 0" class="photo-lightbox" role="dialog" aria-modal="true" @click.self="closePreview">
          <button class="lightbox-close" type="button" aria-label="关闭图片预览" @click="closePreview">×</button>
          <button class="lightbox-nav previous" type="button" aria-label="上一张" @click="stepPreview(-1)">‹</button>
          <figure>
            <SafeImage
              :src="activePreview.detail_url || activePreview.image_url"
              :alt="activePreview.alt || activePreview.title"
              fit="contain"
              loading="eager"
            />
            <figcaption>
              <div>
                <span>{{ activePreview.category }}</span>
                <h2>{{ activePreview.title }}</h2>
                <p>{{ activePreview.description }}</p>
              </div>
              <el-button type="primary" @click="$router.push(photoDetailPath(activePreview))">查看图片档案</el-button>
            </figcaption>
          </figure>
          <button class="lightbox-nav next" type="button" aria-label="下一张" @click="stepPreview(1)">›</button>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { http, assetUrl, FALLBACK_IMAGE } from '../api/http'
import PageHero from '../components/PageHero.vue'
import SectionTitle from '../components/SectionTitle.vue'
import SafeImage from '../components/SafeImage.vue'
import photoLibrary from '../data/maogongshanPhotos.json'

const categories = ['全部', '自然风光', '毛公山全景', '登山道路', '景区建筑', '红色文化', '历史资料', '人物故事', '实践记录', '团队风采']
const category = ref('全部')
const keyword = ref('')
const list = ref([])
const spots = ref([])
const loading = ref(false)
const error = ref('')
const previewIndex = ref(-1)

const safeList = computed(() => list.value.map((item) => ({
  ...item,
  safeUrl: assetUrl(item.thumbnail_url || item.image_url) || FALLBACK_IMAGE
})))
const activePreview = computed(() => safeList.value[previewIndex.value] || {})

const safeSpots = computed(() => spots.value.map((item) => ({
  ...item,
  safeUrl: assetUrl(item.image_url) || FALLBACK_IMAGE
})))

async function load() {
  loading.value = true
  error.value = ''
  try {
    const params = { keyword: keyword.value }
    if (category.value !== '全部') params.category = category.value
    const rows = (await http.get('/api/images', { params })).data
    list.value = rows.filter((item) => item?.image_url)
  } catch (err) {
    error.value = '后端暂时不可用，当前显示随项目打包的本地照片资源。'
    const localRows = photoLibrary.images
    list.value = localRows.filter((item) => {
      const matchCategory = category.value === '全部' || item.category === category.value
      const text = `${item.title}${item.description}${item.location}${item.group}`
      return matchCategory && (!keyword.value || text.includes(keyword.value))
    })
  } finally {
    loading.value = false
  }
}

function selectCategory(value) {
  category.value = value
  load()
}

function openPreview(index) {
  previewIndex.value = index
  document.body.style.overflow = 'hidden'
}

function closePreview() {
  previewIndex.value = -1
  document.body.style.overflow = ''
}

function stepPreview(offset) {
  if (!safeList.value.length) return
  previewIndex.value = (previewIndex.value + offset + safeList.value.length) % safeList.value.length
}

function photoDetailPath(item) {
  return item?.slug ? `/photos/${item.slug}` : `/images/${item?.id}`
}

function handleKeydown(event) {
  if (previewIndex.value < 0) return
  if (event.key === 'Escape') closePreview()
  if (event.key === 'ArrowLeft') stepPreview(-1)
  if (event.key === 'ArrowRight') stepPreview(1)
}

onMounted(async () => {
  window.addEventListener('keydown', handleKeydown)
  await load()
  try {
    spots.value = (await http.get('/api/scenic-spots')).data.filter((item) => item?.image_url)
  } catch {
    spots.value = []
  }
})
onBeforeUnmount(() => {
  document.body.style.overflow = ''
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.gallery-toolbar {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 24px;
  align-items: end;
  padding: 24px;
  margin-bottom: 22px;
  background:
    linear-gradient(135deg, rgba(255, 250, 240, .96), rgba(239, 247, 244, .92)),
    url('/assets/images/culture/maogongshan-red-park-2022.jpg') center/cover;
}

.gallery-toolbar h2 {
  margin: 0;
  color: var(--red-dark);
  font-size: clamp(26px, 4vw, 42px);
}

.gallery-toolbar p:last-child {
  color: var(--muted);
}

.category-rail,
.gallery-topics {
  display: flex;
  gap: 10px;
  padding: 8px 0 18px;
  overflow-x: auto;
}

.category-rail button,
.gallery-topics a {
  flex: 0 0 auto;
  padding: 10px 16px;
  color: var(--red-dark);
  cursor: pointer;
  background: #fffaf0;
  border: 1px solid var(--line);
  border-radius: 999px;
  transition: all .2s ease;
}

.category-rail button.active,
.category-rail button:hover,
.gallery-topics a:hover {
  color: #fff8e6;
  background: var(--red);
  border-color: var(--red);
  box-shadow: 0 10px 22px rgba(143, 29, 34, .18);
}

.museum-wall {
  columns: 4 250px;
  column-gap: 18px;
  min-height: 360px;
}

.museum-photo {
  position: relative;
  break-inside: avoid;
  margin-bottom: 18px;
  overflow: hidden;
  cursor: pointer;
  background: #171311;
  border-radius: 16px;
  box-shadow: 0 18px 45px rgba(50, 18, 18, .16);
}

.museum-photo :deep(img),
.museum-photo :deep(.safe-image) {
  width: 100%;
  display: block;
  min-height: 240px;
  object-fit: cover;
  transition: transform .45s ease, filter .45s ease;
}

.museum-photo:nth-child(3n + 1) :deep(img),
.museum-photo:nth-child(3n + 1) :deep(.safe-image) {
  min-height: 330px;
}

.museum-photo:hover :deep(img) {
  transform: scale(1.055);
  filter: saturate(1.08) contrast(1.05);
}

.photo-mask {
  position: absolute;
  inset: auto 0 0;
  padding: 40px 16px 16px;
  color: #fff8e6;
  background: linear-gradient(0deg, rgba(18, 13, 12, .88), rgba(18, 13, 12, 0));
}

.photo-mask span {
  color: var(--gold-soft);
  font-size: 13px;
}

.photo-mask h3 {
  margin: 6px 0;
  font-size: 20px;
}

.photo-mask p {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
}

.photo-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  opacity: 0;
  transform: translateY(8px);
  transition: opacity .2s ease, transform .2s ease;
}

.museum-photo:hover .photo-actions,
.museum-photo:focus-within .photo-actions {
  opacity: 1;
  transform: translateY(0);
}

.photo-actions button {
  padding: 7px 10px;
  color: #fff8e6;
  cursor: pointer;
  background: rgba(255, 255, 255, .13);
  border: 1px solid rgba(255, 255, 255, .4);
  border-radius: 7px;
}

.photo-actions button:last-child {
  color: #3a130d;
  background: var(--gold-soft);
  border-color: var(--gold-soft);
}

.photo-lightbox {
  position: fixed;
  z-index: 3000;
  inset: 0;
  display: grid;
  place-items: center;
  padding: 34px 80px;
  background: rgba(16, 12, 11, .94);
  backdrop-filter: blur(12px);
}

.photo-lightbox figure {
  width: min(1180px, 100%);
  max-height: calc(100vh - 58px);
  margin: 0;
  overflow: hidden;
  background: #211b18;
  border: 1px solid rgba(255, 248, 230, .22);
  border-radius: 12px;
  box-shadow: 0 28px 80px rgba(0, 0, 0, .5);
}

.photo-lightbox figure :deep(.safe-image) {
  height: min(72vh, 760px);
  min-height: 360px;
  background-color: #211b18;
}

.photo-lightbox figcaption {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: center;
  padding: 18px 22px;
  color: #fff8e6;
}

.photo-lightbox figcaption span {
  color: var(--gold-soft);
  font-size: 12px;
}

.photo-lightbox figcaption h2 {
  margin: 4px 0;
}

.photo-lightbox figcaption p {
  margin: 0;
  color: rgba(255, 248, 230, .72);
}

.lightbox-close,
.lightbox-nav {
  position: absolute;
  z-index: 1;
  display: grid;
  place-items: center;
  color: #fff8e6;
  cursor: pointer;
  background: rgba(255, 255, 255, .1);
  border: 1px solid rgba(255, 255, 255, .28);
  border-radius: 50%;
}

.lightbox-close {
  top: 18px;
  right: 22px;
  width: 44px;
  height: 44px;
  font-size: 28px;
}

.lightbox-nav {
  top: 50%;
  width: 50px;
  height: 50px;
  font-size: 40px;
  transform: translateY(-50%);
}

.lightbox-nav.previous { left: 18px; }
.lightbox-nav.next { right: 18px; }
.lightbox-enter-active,
.lightbox-leave-active { transition: opacity .22s ease; }
.lightbox-enter-from,
.lightbox-leave-to { opacity: 0; }

.spot-showcase {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.spot-card {
  overflow: hidden;
  cursor: pointer;
  background: #fffaf0;
  border: 1px solid var(--line);
  border-radius: 14px;
  box-shadow: 0 14px 34px rgba(84, 16, 21, .1);
}

.spot-card :deep(img),
.spot-card :deep(.safe-image) {
  width: 100%;
  height: 190px;
  object-fit: cover;
}

.spot-card div {
  padding: 16px;
}

.spot-card h3 {
  color: var(--red-dark);
}

.spot-card p,
.spot-card span {
  color: var(--muted);
  line-height: 1.75;
}

.error-alert {
  margin-bottom: 18px;
}

@media (max-width: 900px) {
  .gallery-toolbar,
  .spot-showcase {
    grid-template-columns: 1fr;
  }

  .museum-wall {
    columns: 2 180px;
  }
}

@media (max-width: 560px) {
  .museum-wall {
    columns: 1;
  }

  .photo-actions {
    opacity: 1;
    transform: none;
  }

  .photo-lightbox {
    padding: 70px 12px 20px;
  }

  .photo-lightbox figure :deep(.safe-image) {
    height: 58vh;
    min-height: 260px;
  }

  .photo-lightbox figcaption {
    display: grid;
  }

  .lightbox-nav {
    top: 43%;
    width: 42px;
    height: 42px;
  }

  .lightbox-nav.previous { left: 8px; }
  .lightbox-nav.next { right: 8px; }
}
</style>
