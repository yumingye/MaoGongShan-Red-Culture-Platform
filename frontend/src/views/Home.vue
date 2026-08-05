<template>
  <div>
    <section class="home-hero">
      <el-carousel
        class="hero-carousel"
        height="calc(100vh - 74px)"
        :interval="6200"
        arrow="always"
        indicator-position="none"
        @change="currentHero = $event"
      >
        <el-carousel-item v-for="(slide, index) in heroSlides" :key="slide.slug">
          <SafeImage
            :src="slide.hero_url"
            :alt="slide.alt"
            :loading="index === 0 ? 'eager' : 'lazy'"
            :timeout="15000"
          />
          <div class="hero-slide-shade"></div>
        </el-carousel-item>
      </el-carousel>
      <div class="hero-particles" aria-hidden="true"></div>
      <div class="home-hero-inner">
        <p class="eyebrow">青岛城阳 · 毛公山数字文化平台</p>
        <h1>山河铭记 · 红色传承</h1>
        <p class="hero-photo-title">{{ activeHero.title }}</p>
        <p>{{ activeHero.description }}</p>
        <div class="hero-actions">
          <el-button type="primary" size="large" @click="$router.push('/history')">探索红色历史</el-button>
          <el-button size="large" plain @click="$router.push('/scenery')">浏览全景图库</el-button>
          <el-button size="large" plain @click="$router.push('/guide')">进入数字讲解</el-button>
        </div>
      </div>
    </section>

    <main class="page">
      <p class="data-note reveal">
        数据说明：平台区分“毛公山核心资源”和“扩展参考资源”。历史事实以公开来源和考证状态为准，实践计划、文化解读和技术说明不混写为历史事实。
      </p>
      <el-alert
        v-if="displayNotice"
        class="home-api-notice"
        :title="displayNotice"
        type="warning"
        show-icon
        :closable="false"
      />

      <section class="intro-grid">
        <div class="intro-image reveal">
          <SafeImage src="/assets/images/scenery/maogongshan-mountain.jpg" alt="毛公山山体实景" />
        </div>
        <div class="intro-text reveal">
          <SectionTitle eyebrow="关于毛公山" title="山水风景与红色文化资源的数字化汇聚" />
          <ul>
            <li><strong>地理位置：</strong>公开资料显示，毛公山位于青岛市城阳区惜福镇街道青峰社区一带。</li>
            <li><strong>自然风光：</strong>山体轮廓、登山步道、观景视野和周边乡村环境适合研学展示。</li>
            <li><strong>文化价值：</strong>平台以红色文化传播、地方记忆整理和青年实践为主线组织内容。</li>
            <li><strong>技术路径：</strong>用数据库、地图、检索、问答、音频讲解和三维沙盘提升资料可达性。</li>
          </ul>
          <div class="hero-actions">
            <el-button type="primary" @click="$router.push('/overview')">查看概览</el-button>
            <el-button plain @click="$router.push('/overview/geography')">地理环境专题</el-button>
          </div>
        </div>
      </section>

      <section class="split-head">
        <SectionTitle
          eyebrow="项目实拍"
          title="从山林步道到红色展陈"
          desc="本组照片来自项目提供的毛公山本地素材，统一完成方向校正、压缩和多尺寸处理；点击即可查看大图、说明与来源。"
        />
        <el-button type="primary" plain @click="$router.push('/scenery')">浏览完整图库</el-button>
      </section>
      <div class="home-photo-grid">
        <RouterLink
          v-for="photo in sceneryPhotos"
          :key="photo.slug"
          :to="photo.detail_link"
          class="home-photo-card reveal"
        >
          <SafeImage :src="photo.thumbnail_url" :alt="photo.alt" />
          <div>
            <span>{{ photo.category }}</span>
            <h3>{{ photo.title }}</h3>
            <p>{{ photo.description }}</p>
          </div>
        </RouterLink>
      </div>

      <section class="documentary-grid">
        <div class="documentary-column reveal">
          <div class="documentary-heading">
            <p class="eyebrow">红色文化推荐</p>
            <h2>看见现场展陈中的历史资料</h2>
            <p>展板、资料柜和主题艺术展陈均按画面实际内容命名，不将其误标为历史现场照片。</p>
          </div>
          <RouterLink v-for="photo in culturePhotos" :key="photo.slug" :to="photo.detail_link" class="documentary-row">
            <SafeImage :src="photo.thumbnail_url" :alt="photo.alt" />
            <span><strong>{{ photo.title }}</strong><small>{{ photo.description }}</small></span>
          </RouterLink>
        </div>
        <div class="documentary-column research-column reveal">
          <div class="documentary-heading">
            <p class="eyebrow">调研活动</p>
            <h2>把现场观察转化为数字资源</h2>
            <p>照片记录资料阅读、现场观察、图像采集与团队协作过程。</p>
          </div>
          <RouterLink v-for="photo in researchPhotos" :key="photo.slug" :to="photo.detail_link" class="documentary-row">
            <SafeImage :src="photo.thumbnail_url" :alt="photo.alt" />
            <span><strong>{{ photo.title }}</strong><small>{{ photo.description }}</small></span>
          </RouterLink>
        </div>
      </section>

      <section v-if="teamPhoto" class="team-photo-band reveal">
        <SafeImage :src="teamPhoto.detail_url" :alt="teamPhoto.alt" />
        <div>
          <p class="eyebrow">山东大学软件学院实践团队</p>
          <h2>青年走进现场，软件连接文化资源</h2>
          <p>{{ teamPhoto.description }} 平台不根据照片猜测个人姓名，只在团队页面展示已确认且适合公开的信息。</p>
          <div class="hero-actions">
            <el-button type="primary" @click="$router.push('/team')">查看团队介绍</el-button>
            <el-button plain @click="$router.push('/research')">浏览调研纪实</el-button>
          </div>
        </div>
      </section>

      <section class="home-motion reveal">
        <MotionStory title="红色文化数字专区" :frames="motionFrames" :captions="motionCaptions" />
        <div class="motion-menu">
          <p class="eyebrow">互动展馆</p>
          <h2>看得见的历史脉络，参与式的学习过程</h2>
          <p>专题展馆、动态图文微课、知识闯关和时间长卷均可独立访问，在手机端自动降低动画强度。</p>
          <RouterLink to="/exhibitions">进入红色数字专区</RouterLink>
          <RouterLink to="/videos">观看红色动态微课</RouterLink>
          <RouterLink to="/learning-challenge">开始红色知识闯关</RouterLink>
        </div>
      </section>

      <SectionTitle eyebrow="资源概览" title="数字资源统计" desc="统计数据来自后端 SQLite 数据库，随资源录入自动更新。" />
      <div class="grid grid-6 stats-grid">
        <StatCard label="历史事件" :value="stats.events || 0" icon="Calendar" />
        <StatCard label="红色人物" :value="stats.figures || 0" icon="UserFilled" />
        <StatCard label="图库影像" :value="stats.images || 0" icon="Picture" />
        <StatCard label="数字文献" :value="stats.documents || 0" icon="Document" />
        <StatCard label="地图点位" :value="stats.spots || 0" icon="Location" />
        <StatCard label="资源总量" :value="stats.resources || 0" icon="Collection" />
      </div>

      <section class="topic-showcase reveal">
        <div>
          <p class="eyebrow">多级专题</p>
          <h2>从一座山，进入一座数字文化展馆</h2>
          <p>平台已建立概览、历史、资源、实践、山软青年、地图、图库和音频等多级页面，所有入口都能进入独立专题或详情页。</p>
        </div>
        <div class="topic-links">
          <RouterLink v-for="item in topicLinks" :key="item.to" :to="item.to">
            <strong>{{ item.title }}</strong>
            <span>{{ item.desc }}</span>
          </RouterLink>
        </div>
      </section>

      <section class="split-head">
        <SectionTitle eyebrow="党史学习" title="沿历史坐标理解红色精神" desc="全国党史学习资料与毛公山地方内容分区管理，每条专题保留权威来源和资料边界。" />
        <el-button type="primary" plain @click="$router.push('/party-history')">进入党史学习馆</el-button>
      </section>
      <div class="learning-picks">
        <RouterLink v-for="item in home.learning" :key="item.id" :to="`/learning/${item.id}`" class="learning-pick reveal">
          <SafeImage :src="item.image" :alt="item.title" />
          <div>
            <span>{{ item.scope }}</span>
            <strong>{{ item.event_time }}</strong>
            <h3>{{ item.title }}</h3>
            <p>{{ item.summary }}</p>
          </div>
        </RouterLink>
      </div>

      <section class="split-head">
        <SectionTitle eyebrow="红色历史" title="精选历史资料" desc="进入详情页可查看正文、来源、参考资料、考证状态和相关推荐。" />
        <el-button type="primary" plain @click="$router.push('/history')">查看更多历史资料</el-button>
      </section>
      <div v-loading="loading" class="grid grid-3">
        <HistoryCard v-for="event in home.events" :key="event.id" :item="event" />
      </div>

      <SectionTitle eyebrow="时间脉络" title="历史时间轴入口" desc="用时间线方式浏览公开资料和项目整理形成的文化脉络。" />
      <div class="timeline-strip">
        <article v-for="node in home.timeline" :key="node.id" class="timeline-node reveal" @click="$router.push(`/events/${node.id}`)">
          <strong>{{ node.event_time }}</strong>
          <h3>{{ node.title }}</h3>
          <p>{{ node.summary }}</p>
        </article>
      </div>

      <section class="split-head">
        <SectionTitle eyebrow="真实影像" title="毛公山与扩展资源图库" desc="图库记录标题、地点、来源和版权说明，图片加载失败时自动使用本地备用照片。" />
        <el-button type="primary" plain @click="$router.push('/scenery')">进入全景图库</el-button>
      </section>
      <div class="scenery-mosaic">
        <article
          v-for="image in home.images"
          :key="image.id"
          class="image-card reveal"
          @click="$router.push(image.detail_link || `/images/${image.id}`)"
        >
          <SafeImage
            :src="image.image_url"
            :alt="image.name || image.title || '毛公山与红色文化影像'"
            kind="scenery"
          />
          <div class="image-card-caption">
            <h3>{{ image.name || image.title }}</h3>
            <p>{{ image.category }} · {{ image.location }}</p>
          </div>
        </article>
      </div>

      <SectionTitle eyebrow="数字资源" title="资源分类入口" desc="支持文献、图片、音频、视频、实践成果、红色故事和地点资源分类检索。" />
      <div class="grid grid-6 category-grid">
        <RouterLink v-for="item in resourceTypes" :key="item.name" class="category-card reveal" :to="item.to">
          <el-icon><component :is="item.icon" /></el-icon>
          <strong>{{ item.name }}</strong>
          <span>{{ item.desc }}</span>
        </RouterLink>
      </div>

      <section class="project-band reveal">
        <div>
          <p class="eyebrow">社会实践项目</p>
          <h2>山软寻脉 · 毛公山数字调研实践团</h2>
          <p>山东大学软件学院学生围绕毛公山红色文化数字化保护、青年赓续实践和数字资源库建设开展资料整理、实地调研、平台开发与成果传播。</p>
          <div class="hero-actions">
            <el-button type="primary" @click="$router.push('/project')">项目介绍</el-button>
            <el-button plain @click="$router.push('/research')">实践调研</el-button>
            <el-button plain @click="$router.push('/school')">山软青年专题</el-button>
            <el-button plain @click="$router.push('/chat')">智能问答</el-button>
          </div>
        </div>
      </section>

      <SectionTitle eyebrow="导览与讲解" title="地图、问答、音频与三维沙盘" desc="即使未配置第三方 Key，地图和问答也会使用本地降级方案，保证展示不中断。" />
      <div class="grid grid-3">
        <RouterLink class="feature-entry reveal" to="/map">
          <el-icon><Location /></el-icon>
          <h3>数字地图</h3>
          <p>查看毛公山位置、景点、红色资源点、调研路线和服务设施。</p>
        </RouterLink>
        <RouterLink class="feature-entry reveal" to="/guide">
          <el-icon><ChatDotRound /></el-icon>
          <h3>AI 数字讲解</h3>
          <p>结合本地知识库、语音讲解稿和推荐问题，形成可演示的讲解入口。</p>
        </RouterLink>
        <RouterLink class="feature-entry reveal" to="/sandtable">
          <el-icon><Location /></el-icon>
          <h3>三维数字沙盘</h3>
          <p>用地形、路线光带和点位标记呈现毛公山导览结构。</p>
        </RouterLink>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { Location, ChatDotRound } from '@element-plus/icons-vue'
import { http, normalizeListResponse } from '../api/http'
import SectionTitle from '../components/SectionTitle.vue'
import StatCard from '../components/StatCard.vue'
import HistoryCard from '../components/HistoryCard.vue'
import SafeImage from '../components/SafeImage.vue'
import MotionStory from '../components/MotionStory.vue'
import { videoLessons } from '../data/experienceContent'
import photoLibrary from '../data/maogongshanPhotos.json'

const loading = ref(true)
const apiNotice = ref('')
const route = useRoute()
const displayNotice = computed(() => route.query.loadError === 'chunk'
  ? '页面资源更新后浏览器缓存未能同步，已安全返回首页。请重新进入刚才的栏目。'
  : apiNotice.value)
const currentHero = ref(0)
const localImages = photoLibrary.images.slice(0, 6).map((item, index) => ({
  id: `local-${index}`,
  name: item.title,
  title: item.title,
  category: item.category,
  location: item.location,
  image_url: item.thumbnail_url,
  detail_link: item.detail_link
}))
const home = ref({ events: [], figures: [], images: localImages, timeline: [], learning: [] })
const stats = ref({ images: photoLibrary.images.length, resources: photoLibrary.images.length })
const motionFrames = videoLessons[0].frames
const motionCaptions = ['让历史节点沿时间线逐步点亮。', '用本地影像和清晰字幕组织微课内容。', '通过问答、收藏和闯关形成个人学习路径。']

const heroSlides = computed(() => photoLibrary.hero_slugs
  .map((slug) => photoLibrary.images.find((item) => item.slug === slug))
  .filter(Boolean))
const activeHero = computed(() => heroSlides.value[currentHero.value] || {
  title: '毛公山实景',
  description: '青岛市城阳区毛公山红色文化数字资源平台'
})
const sceneryPhotos = photoLibrary.images
  .filter((item) => item.group === '毛公山自然风景')
  .slice(0, 6)
const culturePhotos = photoLibrary.images
  .filter((item) => item.group === '红色文化与党史')
  .slice(0, 4)
const researchPhotos = photoLibrary.images
  .filter((item) => item.group === '社会实践与调研活动')
  .slice(0, 4)
const teamPhoto = photoLibrary.images.find((item) => item.group === '山东大学软件学院团队')
const topicLinks = [
  { title: '地理环境', desc: '位置、交通和周边格局', to: '/overview/geography' },
  { title: '党史学习', desc: '历史时期与重要事件', to: '/party-history' },
  { title: '红色精神', desc: '精神谱系与青年启示', to: '/spirits' },
  { title: '调研路线', desc: '从现场到数据入库', to: '/research/topic/route' },
  { title: '系统架构', desc: '软件工程技术路线', to: '/school/topic/architecture' },
  { title: '红色点位', desc: '地图与点位联动', to: '/map/topic/red-points' },
  { title: '图片资源', desc: '来源与版权管理', to: '/resources/category/images' }
]
const resourceTypes = [
  { name: '历史文献', icon: 'Document', desc: '档案、报道、报告', to: '/resources/category/documents' },
  { name: '图片资源', icon: 'Picture', desc: '风景与活动图片', to: '/resources/category/images' },
  { name: '音频讲解', icon: 'Microphone', desc: '讲解稿与播报', to: '/resources/category/audio' },
  { name: '实践成果', icon: 'Collection', desc: '调研与系统成果', to: '/resources/category/achievements' },
  { name: '红色故事', icon: 'Reading', desc: '故事和文化解读', to: '/stories' },
  { name: '地点资源', icon: 'Location', desc: '景点和路线点位', to: '/places' }
]

onMounted(async () => {
  try {
    const [homeRes, statsRes] = await Promise.all([http.get('/api/home'), http.get('/api/stats')])
    const payload = homeRes.data && typeof homeRes.data === 'object' ? homeRes.data : {}
    home.value = {
      events: normalizeListResponse(payload.events).items,
      figures: normalizeListResponse(payload.figures).items,
      images: normalizeListResponse(payload.images).items.length ? payload.images : localImages,
      timeline: normalizeListResponse(payload.timeline).items,
      learning: normalizeListResponse(payload.learning).items
    }
    stats.value = statsRes.data && typeof statsRes.data === 'object' ? statsRes.data : stats.value
  } catch {
    apiNotice.value = '后端暂时不可连接，当前展示本地毛公山照片与平台固定专题；服务恢复后数据统计会自动更新。'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.home-hero {
  position: relative;
  overflow: hidden;
  min-height: calc(100vh - 74px);
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  align-items: center;
  color: #fff8e6;
  background: #241411;
}

.home-hero::after {
  content: '';
  position: absolute;
  inset: auto 0 0;
  height: 34%;
  pointer-events: none;
  background: linear-gradient(0deg, rgba(248, 244, 232, 1), rgba(248, 244, 232, 0));
}

.hero-carousel {
  position: absolute;
  inset: 0;
}

.hero-carousel :deep(.el-carousel__container),
.hero-carousel :deep(.el-carousel__item),
.hero-carousel :deep(.safe-image) {
  height: 100%;
}

.hero-carousel :deep(img) {
  transform: scale(1.03);
  animation: heroImageDrift 11s ease-in-out infinite alternate;
}

.hero-carousel :deep(.el-carousel__arrow) {
  z-index: 4;
  width: 46px;
  height: 46px;
  background: rgba(49, 8, 11, .64);
  border: 1px solid rgba(255, 248, 230, .42);
}

.hero-slide-shade {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(105deg, rgba(49, 8, 11, .92), rgba(84, 16, 21, .58) 52%, rgba(18, 40, 38, .24)),
    linear-gradient(0deg, rgba(23, 15, 12, .42), transparent 55%);
}

.hero-particles {
  position: absolute;
  z-index: 0;
  inset: 0;
  pointer-events: none;
  opacity: .4;
  background-image:
    radial-gradient(circle, rgba(255, 221, 143, .9) 0 2px, transparent 2.6px),
    radial-gradient(circle, rgba(255, 255, 255, .72) 0 1px, transparent 1.8px);
  background-size: 140px 140px, 220px 220px;
  animation: particleFloat 18s linear infinite;
}

.home-hero-inner {
  position: relative;
  z-index: 1;
  width: min(1180px, calc(100% - 32px));
  margin: 0 auto;
  padding-bottom: 6vh;
  min-width: 0;
}

.home-hero h1 {
  max-width: 980px;
  margin: 0;
  font-size: clamp(48px, 8vw, 104px);
  line-height: 1.12;
  letter-spacing: 0;
  text-shadow: 0 16px 38px rgba(0, 0, 0, .32);
  overflow-wrap: anywhere;
}

.home-hero p {
  max-width: 760px;
  font-size: 20px;
  line-height: 1.9;
}

.home-hero .hero-photo-title {
  margin-bottom: -12px;
  color: var(--gold-soft);
  font-weight: 800;
}

@keyframes heroImageDrift {
  from { transform: scale(1.03) translate3d(0, 0, 0); }
  to { transform: scale(1.09) translate3d(-1.2%, -.8%, 0); }
}

@keyframes particleFloat {
  from { background-position: 0 0, 0 0; }
  to { background-position: 140px -140px, -220px 220px; }
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
}

.intro-grid {
  display: grid;
  grid-template-columns: 1.05fr .95fr;
  gap: 28px;
  align-items: center;
  margin: 34px 0 52px;
}

.intro-image img {
  width: 100%;
  display: block;
  border-radius: 16px;
  box-shadow: var(--shadow);
}

.intro-text {
  padding: 28px;
  background: rgba(255, 250, 240, .9);
  border: 1px solid var(--line);
  border-radius: 16px;
  box-shadow: var(--shadow);
}

.intro-text ul {
  padding-left: 20px;
  color: var(--muted);
  line-height: 1.9;
}

.home-photo-grid {
  display: grid;
  grid-template-columns: 1.25fr 1fr 1fr;
  gap: 18px;
  margin-bottom: 58px;
}

.home-photo-card {
  position: relative;
  min-height: 260px;
  overflow: hidden;
  color: #fff8e6;
  border-radius: 14px;
  box-shadow: var(--shadow);
}

.home-photo-card:first-child {
  grid-row: span 2;
  min-height: 538px;
}

.home-photo-card :deep(.safe-image) {
  position: absolute;
  inset: 0;
}

.home-photo-card :deep(img) {
  transition: transform .45s ease, filter .45s ease;
}

.home-photo-card:hover :deep(img) {
  transform: scale(1.055);
  filter: saturate(1.08);
}

.home-photo-card > div {
  position: absolute;
  z-index: 1;
  inset: auto 0 0;
  padding: 54px 18px 18px;
  background: linear-gradient(0deg, rgba(24, 15, 12, .94), transparent);
}

.home-photo-card span {
  color: var(--gold-soft);
  font-size: 12px;
}

.home-photo-card h3 {
  margin: 5px 0;
  font-size: 21px;
}

.home-photo-card p {
  margin: 0;
  color: rgba(255, 248, 230, .78);
  font-size: 13px;
  line-height: 1.65;
}

.documentary-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 22px;
  margin-bottom: 58px;
}

.documentary-column {
  padding: 26px;
  background: #fffaf0;
  border: 1px solid var(--line);
  border-radius: 16px;
  box-shadow: 0 16px 38px rgba(84, 16, 21, .1);
}

.research-column {
  background: linear-gradient(145deg, #f4f9fa, #fffaf0);
}

.documentary-heading h2 {
  margin: 2px 0 8px;
  color: var(--red-dark);
  font-size: clamp(25px, 3vw, 38px);
}

.documentary-heading > p:last-child {
  color: var(--muted);
  line-height: 1.8;
}

.documentary-row {
  display: grid;
  grid-template-columns: 128px minmax(0, 1fr);
  gap: 14px;
  align-items: center;
  padding: 14px 0;
  border-top: 1px solid var(--line);
}

.documentary-row :deep(.safe-image) {
  height: 88px;
  min-height: 88px;
  border-radius: 8px;
}

.documentary-row span {
  display: grid;
  gap: 6px;
}

.documentary-row strong {
  color: var(--red-dark);
}

.documentary-row small {
  color: var(--muted);
  line-height: 1.6;
}

.team-photo-band {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(320px, .85fr);
  gap: 30px;
  align-items: center;
  margin: 28px 0 60px;
  padding: 18px;
  background: linear-gradient(135deg, #eaf4f7, #fffaf0);
  border: 1px solid #cbdde2;
  border-radius: 18px;
  box-shadow: var(--shadow);
}

.team-photo-band :deep(.safe-image) {
  min-height: 390px;
  border-radius: 12px;
}

.team-photo-band > div {
  padding: 20px 28px 20px 0;
}

.team-photo-band h2 {
  margin: 0;
  color: #164b62;
  font-size: clamp(28px, 4vw, 46px);
}

.team-photo-band p {
  color: var(--muted);
  line-height: 1.9;
}

.stats-grid,
.category-grid,
.scenery-mosaic {
  margin-bottom: 54px;
}

.topic-showcase {
  display: grid;
  grid-template-columns: .95fr 1.35fr;
  gap: 28px;
  align-items: center;
  margin: 46px 0 56px;
  padding: 30px;
  color: #fff8e6;
  background:
    linear-gradient(120deg, rgba(49, 8, 11, .96), rgba(25, 65, 86, .84)),
    url('/assets/images/culture/maogongshan-red-park-2022.jpg') center/cover;
  border-radius: 18px;
  box-shadow: var(--shadow);
}

.topic-showcase h2 {
  margin: 0;
  font-size: clamp(28px, 4vw, 46px);
}

.topic-showcase p {
  line-height: 1.85;
}

.topic-links {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.topic-links a {
  display: grid;
  gap: 6px;
  min-height: 112px;
  padding: 16px;
  background: rgba(255, 248, 229, .12);
  border: 1px solid rgba(255, 248, 229, .22);
  border-radius: 12px;
  transition: transform .2s ease, background .2s ease;
}

.topic-links a:hover {
  background: rgba(255, 248, 229, .2);
  transform: translateY(-3px);
}

.topic-links span {
  color: rgba(255, 248, 229, .76);
  font-size: 13px;
}

.split-head {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 20px;
  margin-top: 52px;
}

.learning-picks {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 54px;
}

.home-motion {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(300px, .65fr);
  gap: 26px;
  align-items: center;
  margin: 48px 0 58px;
}

.home-motion .motion-story { min-height: 470px; }
.motion-menu h2 { color: var(--red-dark); font-size: clamp(28px, 4vw, 46px); }
.motion-menu p { color: var(--muted); line-height: 1.9; }
.motion-menu a { display: block; padding: 12px 0; color: var(--red); font-weight: 800; border-bottom: 1px solid var(--line); }

.learning-pick {
  position: relative;
  min-height: 330px;
  overflow: hidden;
  color: #fff8e6;
  border-radius: 10px;
  box-shadow: var(--shadow);
}

.learning-pick :deep(.safe-image) {
  position: absolute;
  inset: 0;
}

.learning-pick::after {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(49,8,11,.08), rgba(49,8,11,.96));
  content: '';
}

.learning-pick > div {
  position: absolute;
  inset: auto 0 0;
  z-index: 1;
  padding: 20px;
}

.learning-pick span { color: var(--gold-soft); font-size: 12px; }
.learning-pick strong { display: block; margin-top: 5px; }
.learning-pick h3 { margin: 8px 0; font-size: 21px; }
.learning-pick p { display: -webkit-box; margin: 0; overflow: hidden; color: rgba(255,248,230,.8); font-size: 13px; line-height: 1.7; -webkit-line-clamp: 3; -webkit-box-orient: vertical; }

.timeline-strip {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 52px;
}

.timeline-node {
  padding: 18px;
  cursor: pointer;
  background: #fffaf0;
  border: 1px solid var(--line);
  border-top: 4px solid var(--gold);
  border-radius: 12px;
  box-shadow: 0 12px 28px rgba(84, 16, 21, .08);
}

.timeline-node strong {
  color: var(--red);
}

.timeline-node h3 {
  min-height: 54px;
  color: var(--red-dark);
  font-size: 17px;
}

.timeline-node p {
  color: var(--muted);
  font-size: 13px;
  line-height: 1.7;
}

.scenery-mosaic {
  display: grid;
  grid-template-columns: 1.4fr 1fr 1fr;
  gap: 18px;
}

.scenery-mosaic .image-card:first-child {
  grid-row: span 2;
}

.scenery-mosaic .image-card:first-child :deep(.safe-image) {
  height: 478px;
}

.category-card,
.feature-entry {
  display: grid;
  gap: 10px;
  padding: 20px;
  background: #fffaf0;
  border: 1px solid var(--line);
  border-radius: 12px;
  box-shadow: 0 14px 30px rgba(84, 16, 21, .08);
  transition: transform .22s ease, box-shadow .22s ease;
}

.category-card:hover,
.feature-entry:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow);
}

.category-card .el-icon,
.feature-entry .el-icon {
  color: var(--red);
  font-size: 34px;
}

.category-card strong,
.feature-entry h3 {
  color: var(--red-dark);
}

.category-card span,
.feature-entry p {
  color: var(--muted);
  line-height: 1.8;
}

.project-band {
  margin: 36px 0 54px;
  padding: 34px;
  color: #fff8e6;
  background:
    linear-gradient(105deg, rgba(49, 8, 11, .94), rgba(143, 29, 34, .82)),
    url('/assets/images/activity/maogongshan-3a-plaque.jpg') center/cover;
  border-radius: 18px;
  box-shadow: var(--shadow);
}

.project-band h2 {
  margin: 0;
  font-size: clamp(26px, 4vw, 42px);
}

.project-band p {
  max-width: 780px;
  line-height: 1.9;
}

@media (max-width: 980px) {
  .intro-grid,
  .topic-showcase,
  .timeline-strip,
  .scenery-mosaic,
  .learning-picks,
  .documentary-grid,
  .team-photo-band {
    grid-template-columns: 1fr;
  }

  .home-motion { grid-template-columns: 1fr; }

  .home-photo-grid {
    grid-template-columns: 1fr 1fr;
  }

  .home-photo-card:first-child {
    grid-row: auto;
    grid-column: 1 / -1;
    min-height: 390px;
  }

  .team-photo-band > div {
    padding: 12px;
  }

  .topic-links {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .scenery-mosaic .image-card:first-child :deep(.safe-image) {
    height: 230px;
  }
}

@media (max-width: 620px) {
  .home-hero { min-height: calc(100svh - 74px); }
  .home-hero::after { height:22%; }
  .home-hero-inner { width: calc(100% - 32px); padding: 46px 0 120px; }
  .home-hero h1 { max-width: 100%; font-size: 36px; line-height: 1.18; white-space: normal; word-break: normal; }
  .home-hero p { max-width: 100%; font-size: 17px; overflow-wrap: anywhere; }
  .home-hero .hero-actions { display: grid; grid-template-columns: 1fr; }
  .home-hero .hero-actions .el-button { width: 100%; margin-left: 0; }
  .hero-carousel :deep(.el-carousel__arrow) { display: none; }
  .topic-links {
    grid-template-columns: 1fr;
  }

  .home-photo-grid {
    grid-template-columns: 1fr;
  }

  .home-photo-card,
  .home-photo-card:first-child {
    grid-column: auto;
    min-height: 300px;
  }

  .documentary-row {
    grid-template-columns: 96px minmax(0, 1fr);
  }

  .team-photo-band :deep(.safe-image) {
    min-height: 250px;
  }

  .split-head {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
