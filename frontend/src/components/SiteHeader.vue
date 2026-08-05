<template>
  <header class="site-header" :class="{ 'is-scrolled': scrolled }">
    <RouterLink class="brand" to="/" @click="opened = false">
      <span class="brand-mark">毛</span>
      <span class="brand-copy">
        <strong>毛公山红色数字文化平台</strong>
        <small>城阳红色文化 · 山软数字实践</small>
      </span>
    </RouterLink>

    <nav class="desktop-nav" aria-label="主导航">
      <RouterLink class="nav-link" to="/">首页</RouterLink>
      <el-dropdown v-for="group in navGroups" :key="group.label" trigger="hover" popper-class="nav-popper">
        <button class="nav-link nav-group" :class="{ active: isGroupActive(group) }" type="button">
          {{ group.label }}<el-icon><ArrowDown /></el-icon>
        </button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item v-for="item in group.items" :key="item.path">
              <RouterLink :to="item.path" class="dropdown-link">
                <el-icon><component :is="item.icon" /></el-icon>
                <span><strong>{{ item.label }}</strong><small>{{ item.desc }}</small></span>
              </RouterLink>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </nav>

    <el-input v-model="keyword" class="top-search" placeholder="搜索资料" clearable @keyup.enter="goSearch">
      <template #prefix><el-icon><Search /></el-icon></template>
    </el-input>

    <button class="menu-toggle" type="button" :aria-expanded="opened" aria-label="展开网站导航" @click="opened = !opened">
      <el-icon><Close v-if="opened" /><Menu v-else /></el-icon>
    </button>

    <Transition name="mobile-menu">
      <nav v-if="opened" class="mobile-nav" aria-label="移动端导航">
        <RouterLink to="/" @click="opened = false">首页</RouterLink>
        <section v-for="group in navGroups" :key="group.label">
          <h3>{{ group.label }}</h3>
          <RouterLink v-for="item in group.items" :key="item.path" :to="item.path" @click="opened = false">
            {{ item.label }}
          </RouterLink>
        </section>
      </nav>
    </Transition>
  </header>
</template>

<script setup>
import { markRaw, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import {
  ArrowDown, ChatDotRound, Close, Collection, Compass, DataAnalysis, Document,
  Guide, Headset, HomeFilled, MapLocation, Menu, Picture, Reading, Search,
  Star, TrendCharts, User, UserFilled
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const opened = ref(false)
const keyword = ref('')
const scrolled = ref(false)

const navGroups = [
  {
    label: '走进毛公山',
    items: [
      { path: '/overview', label: '走进毛公山', desc: '地理、景观、路线与文化价值', icon: markRaw(Compass) },
      { path: '/history', label: '毛公山历史文化', desc: '地方文化资料查询与考证', icon: markRaw(Document) },
      { path: '/red-scenic', label: '红色景区', desc: '景点、服务设施与周边资源', icon: markRaw(MapLocation) },
      { path: '/scenery', label: '图片影像馆', desc: '125 条本地化真实图片资料', icon: markRaw(Picture) },
      { path: '/map', label: '地图导览', desc: '点位、路线与无密钥降级导览', icon: markRaw(Guide) }
    ]
  },
  {
    label: '党史学习',
    items: [
      { path: '/party-history', label: '红色党史学习', desc: '四个历史时期与重要会议', icon: markRaw(Reading) },
      { path: '/figures', label: '红色人物', desc: '人物档案与相关事件', icon: markRaw(User) },
      { path: '/red-events', label: '红色事件', desc: '重大事件的背景、过程与意义', icon: markRaw(TrendCharts) },
      { path: '/spirits', label: '红色精神', desc: '中国共产党人精神谱系', icon: markRaw(Star) },
      { path: '/timeline', label: '红色时间轴', desc: '自动播放、阶段筛选与节点展开', icon: markRaw(DataAnalysis) },
      { path: '/conferences', label: '重大会议专题', desc: '理解会议背景、问题和影响', icon: markRaw(Document) }
    ]
  },
  {
    label: '数字展馆',
    items: [
      { path: '/resources', label: '数字资源库', desc: '文章、图片、音视频和研学资料', icon: markRaw(Collection) },
      { path: '/red-culture', label: '红色文化拓展', desc: '全国、山东与青岛专题资料', icon: markRaw(HomeFilled) },
      { path: '/exhibitions', label: '红色数字专区', desc: '15 个独立动态专题展馆', icon: markRaw(DataAnalysis) },
      { path: '/videos', label: '红色影像馆', desc: '可暂停的本地图文动态微课', icon: markRaw(Picture) },
      { path: '/learning-challenge', label: '红色知识闯关', desc: '积分、错题与本地学习报告', icon: markRaw(Star) },
      { path: '/chat', label: '红色知识问答', desc: '基于本站知识库检索回答', icon: markRaw(ChatDotRound) },
      { path: '/audio', label: '音频讲解', desc: '讲解稿与浏览器自然语音播放', icon: markRaw(Headset) }
    ]
  },
  {
    label: '青年实践',
    items: [
      { path: '/research', label: '研学实践', desc: '调研路线、日志与访谈记录', icon: markRaw(UserFilled) },
      { path: '/news', label: '新闻与活动', desc: '现场调研与团队活动影像纪实', icon: markRaw(Picture) },
      { path: '/school', label: '山东大学软件学院专题', desc: '软件赋能红色文化传承', icon: markRaw(DataAnalysis) },
      { path: '/about', label: '关于平台', desc: '建设背景、资料边界与版权说明', icon: markRaw(Document) }
    ]
  }
]

function isGroupActive(group) {
  return group.items.some((item) => route.path === item.path || route.path.startsWith(`${item.path}/`))
}

function goSearch() {
  const q = keyword.value.trim()
  if (!q) return
  opened.value = false
  router.push({ path: '/search', query: { q } })
}

function updateScrollState() {
  scrolled.value = window.scrollY > 16
}

function handleKeydown(event) {
  if (event.key === 'Escape') opened.value = false
}

watch(() => route.fullPath, () => { opened.value = false })
watch(opened, (value) => { document.body.style.overflow = value && window.innerWidth <= 720 ? 'hidden' : '' })
onMounted(() => {
  window.addEventListener('scroll', updateScrollState, { passive: true })
  window.addEventListener('keydown', handleKeydown)
})
onBeforeUnmount(() => {
  document.body.style.overflow = ''
  window.removeEventListener('scroll', updateScrollState)
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.site-header { min-height: 76px; }
.site-header.is-scrolled { box-shadow: 0 12px 30px rgba(84,16,21,.14); }
.brand { min-width: 250px; }
.brand-copy { display: grid; gap: 3px; }
.brand-copy strong { color: var(--red-dark); line-height: 1.2; }
.brand-copy small { color: var(--muted); font-size: 11px; font-weight: 500; }
.desktop-nav { display: flex; align-items: center; justify-content: center; gap: 4px; flex: 1; min-width: 0; }
.nav-group { display: inline-flex; align-items: center; gap: 4px; border: 0; font: inherit; cursor: pointer; }
.nav-group.active { color: var(--red); background: rgba(143,29,34,.08); }
.dropdown-link { display: grid; grid-template-columns: 22px 1fr; gap: 10px; align-items: center; width: 280px; padding: 5px 2px; }
.dropdown-link .el-icon { color: var(--red); font-size: 18px; }
.dropdown-link span { display: grid; gap: 3px; }
.dropdown-link strong { color: var(--red-dark); }
.dropdown-link small { color: var(--muted); font-size: 12px; }
.top-search { width: 180px; }
.mobile-nav { display: none; }
.mobile-menu-enter-active, .mobile-menu-leave-active { transition: opacity .2s ease, transform .2s ease; }
.mobile-menu-enter-from, .mobile-menu-leave-to { opacity: 0; transform: translateY(-10px); }
@media (max-width: 1180px) {
  .desktop-nav { display: none; }
  .menu-toggle { display: grid; place-items: center; margin-left: auto; }
  .top-search { order: initial; width: min(260px, 32vw); }
  .mobile-nav { position: absolute; top: 100%; left: 0; right: 0; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 22px; max-height: calc(100vh - 76px); overflow-y: auto; padding: 26px clamp(18px,5vw,64px); background: rgba(255,250,240,.98); border-bottom: 1px solid var(--line); box-shadow: 0 22px 38px rgba(84,16,21,.14); }
  .mobile-nav > a { grid-column: 1 / -1; color: var(--red); font-weight: 800; }
  .mobile-nav section { display: grid; align-content: start; gap: 10px; }
  .mobile-nav h3 { margin: 0 0 4px; color: var(--red-dark); font-size: 16px; }
  .mobile-nav a { color: #554a42; line-height: 1.5; }
}
@media (max-width: 720px) {
  .site-header { flex-wrap: nowrap; }
  .brand { flex: 1 1 auto; min-width: 0; max-width: none; }
  .menu-toggle { flex: 0 0 40px; margin-left: 0; }
  .brand-copy { min-width: 0; }
  .brand-copy strong { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 15px; }
  .brand-copy small { display: none; }
  .top-search { display: none; }
  .mobile-nav { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 460px) {
  .mobile-nav { grid-template-columns: 1fr; }
}
</style>
