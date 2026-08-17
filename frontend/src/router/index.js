import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'

const views = {
  HistorySearch: () => import('../views/HistorySearch.vue'),
  Overview: () => import('../views/Overview.vue'),
  EventDetail: () => import('../views/EventDetail.vue'),
  Figures: () => import('../views/Figures.vue'),
  FigureDetail: () => import('../views/FigureDetail.vue'),
  Timeline: () => import('../views/Timeline.vue'),
  Scenery: () => import('../views/Scenery.vue'),
  ImageDetail: () => import('../views/ImageDetail.vue'),
  MapGuide: () => import('../views/MapGuide.vue'),
  Resources: () => import('../views/Resources.vue'),
  ResourceDetail: () => import('../views/ResourceDetail.vue'),
  Research: () => import('../views/Research.vue'),
  ResearchDetail: () => import('../views/ResearchDetail.vue'),
  Search: () => import('../views/Search.vue'),
  Admin: () => import('../views/Admin.vue'),
  About: () => import('../views/About.vue'),
  Project: () => import('../views/Project.vue'),
  PracticePlan: () => import('../views/PracticePlan.vue'),
  Results: () => import('../views/Results.vue'),
  Team: () => import('../views/Team.vue'),
  News: () => import('../views/News.vue'),
  Sources: () => import('../views/Sources.vue'),
  Chat: () => import('../views/Chat.vue'),
  Guide: () => import('../views/Guide.vue'),
  AudioGuides: () => import('../views/AudioGuides.vue'),
  AudioDetail: () => import('../views/AudioDetail.vue'),
  SandTable: () => import('../views/SandTable.vue'),
  School: () => import('../views/School.vue'),
  Favorites: () => import('../views/Favorites.vue'),
  Help: () => import('../views/Help.vue'),
  Stories: () => import('../views/Stories.vue'),
  StoryDetail: () => import('../views/StoryDetail.vue'),
  Places: () => import('../views/Places.vue'),
  PlaceDetail: () => import('../views/PlaceDetail.vue'),
  Achievements: () => import('../views/Achievements.vue'),
  AchievementDetail: () => import('../views/AchievementDetail.vue'),
  LearningHub: () => import('../views/LearningHub.vue'),
  LearningDetail: () => import('../views/LearningDetail.vue'),
  HistoryStageDetail: () => import('../views/HistoryStageDetail.vue'),
  ExhibitionHub: () => import('../views/ExhibitionHub.vue'),
  ExhibitionDetail: () => import('../views/ExhibitionDetail.vue'),
  VideoHub: () => import('../views/VideoHub.vue'),
  VideoDetail: () => import('../views/VideoDetail.vue'),
  InteractiveLearning: () => import('../views/InteractiveLearning.vue'),
  TopicDetail: () => import('../views/TopicDetail.vue'),
  NotFound: () => import('../views/NotFound.vue')
}

const routes = [
  { path: '/', component: Home },
  { path: '/history', component: views.HistorySearch },
  {
    path: '/party-history',
    component: views.LearningHub,
    props: {
      title: '红色党史学习',
      subtitle: '按历史时期、重要会议和重大事件建立可追溯的学习路径。',
      category: '党史学习',
      hero: '/assets/images/party-history/info-overview-party-history.jpg'
    }
  },
  {
    path: '/red-events',
    component: views.LearningHub,
    props: {
      title: '红色事件',
      subtitle: '从时代背景、主要过程、历史意义和青年启示理解重大历史节点。',
      category: '红色事件',
      hero: '/assets/images/party-history/info-overview-red-events.jpg'
    }
  },
  {
    path: '/spirits',
    component: views.LearningHub,
    props: {
      title: '中国共产党人精神谱系',
      subtitle: '以公开发布的精神谱系资料为依据，连接历史实践与青年责任。',
      category: '红色精神',
      hero: '/assets/images/party-history/info-overview-red-spirit.jpg'
    }
  },
  {
    path: '/red-culture',
    component: views.LearningHub,
    props: {
      title: '红色文化拓展馆',
      subtitle: '汇聚全国党史、山东与青岛红色文化、山大实践专题，并明确资料边界。',
      hero: '/assets/images/party-history/info-overview-red-expansion.jpg'
    }
  },
  { path: '/learning/:id', component: views.LearningDetail },
  { path: '/party-history/stage/:slug', component: views.HistoryStageDetail },
  { path: '/exhibitions', component: views.ExhibitionHub },
  { path: '/videos', component: views.VideoHub },
  { path: '/videos/:slug', component: views.VideoDetail },
  { path: '/learning-challenge', component: views.InteractiveLearning },
  { path: '/shandong-red', component: views.ExhibitionDetail, props: { fixedSlug: 'shandong-red' } },
  { path: '/qingdao-red', component: views.ExhibitionDetail, props: { fixedSlug: 'qingdao-red' } },
  { path: '/youth-mission', component: views.ExhibitionDetail, props: { fixedSlug: 'youth-mission' } },
  { path: '/conferences', component: views.ExhibitionDetail, props: { fixedSlug: 'major-conferences' } },
  { path: '/red-books', component: views.ExhibitionDetail, props: { fixedSlug: 'red-books' } },
  { path: '/red-relics', component: views.ExhibitionDetail, props: { fixedSlug: 'red-relics' } },
  { path: '/photo-compare', component: views.ExhibitionDetail, props: { fixedSlug: 'photo-compare' } },
  { path: '/study-routes', component: views.ExhibitionDetail, props: { fixedSlug: 'study-routes' } },
  { path: '/heroes', component: views.Figures },
  { path: '/revolutionary-sites', component: views.Places },
  { path: '/red-stories', component: views.Stories },
  { path: '/overview', component: views.Overview },
  { path: '/overview/:slug', component: views.TopicDetail, props: { slugPrefix: 'overview-' } },
  { path: '/events/:id', component: views.EventDetail },
  { path: '/figures', component: views.Figures },
  { path: '/figures/:id', component: views.FigureDetail },
  { path: '/timeline', component: views.Timeline },
  { path: '/history/topic/:slug', component: views.TopicDetail, props: { slugPrefix: 'history-' } },
  { path: '/scenery', component: views.Scenery },
  { path: '/gallery/:slug', component: views.TopicDetail, props: { slugPrefix: 'gallery-' } },
  { path: '/images/:id', component: views.ImageDetail },
  { path: '/photos/:slug', component: views.ImageDetail },
  { path: '/map', component: views.MapGuide },
  { path: '/map/topic/:slug', component: views.TopicDetail, props: { slugPrefix: 'map-' } },
  { path: '/resources', component: views.Resources },
  { path: '/resources/category/:slug', component: views.TopicDetail, props: { slugPrefix: 'resources-' } },
  { path: '/resources/:id', component: views.ResourceDetail },
  { path: '/research', component: views.Research },
  { path: '/research/topic/:slug', component: views.TopicDetail, props: { slugPrefix: 'research-' } },
  { path: '/research/:id', component: views.ResearchDetail },
  { path: '/search', component: views.Search },
  { path: '/admin', component: views.Admin },
  { path: '/about', component: views.About },
  { path: '/project', component: views.Project },
  { path: '/plan', component: views.PracticePlan },
  { path: '/results', component: views.Results },
  { path: '/team', component: views.Team },
  { path: '/news', component: views.News },
  { path: '/sources', component: views.Sources },
  { path: '/chat', component: views.Chat },
  { path: '/guide', component: views.Guide },
  { path: '/audio', component: views.AudioGuides },
  { path: '/audio/:id', component: views.AudioDetail },
  { path: '/sandtable', component: views.SandTable },
  { path: '/school', component: views.School },
  { path: '/school/topic/:slug', component: views.TopicDetail, props: { slugPrefix: 'school-' } },
  { path: '/favorites', component: views.Favorites },
  { path: '/help', component: views.Help },
  { path: '/stories', component: views.Stories },
  { path: '/stories/:id', component: views.StoryDetail },
  { path: '/places', component: views.Places },
  { path: '/red-scenic', component: views.Places },
  { path: '/places/:id', component: views.PlaceDetail },
  { path: '/achievements', component: views.Achievements },
  { path: '/achievements/:id', component: views.AchievementDetail },
  { path: '/exhibitions/:slug', component: views.ExhibitionDetail },
  { path: '/:pathMatch(.*)*', component: views.NotFound }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 })
})

const pageTitles = [
  [/^\/$/, '首页'],
  [/^\/overview/, '走进毛公山'],
  [/^\/(party-history|red-events|spirits|red-culture|timeline|history)/, '红色文化与党史学习'],
  [/^\/(figures|heroes)/, '红色人物档案'],
  [/^\/(exhibitions|shandong-red|qingdao-red|youth-mission|conferences|red-books|red-relics|photo-compare|study-routes)/, '数字展馆'],
  [/^\/(scenery|gallery|images|photos)/, '毛公山全景图库'],
  [/^\/map/, '毛公山数字导览'],
  [/^\/(research|plan|results|team|achievements|project)/, '山大社会实践'],
  [/^\/(resources|audio|videos)/, '数字资源库'],
  [/^\/(stories|places|red-scenic)/, '红色故事与红色地标'],
  [/^\/chat/, 'AI 红色文化助手'],
  [/^\/search/, '全站搜索'],
  [/^\/learning-challenge/, '红色文化互动学习'],
  [/^\/guide/, '毛公山参观指南'],
  [/^\/news/, '实践动态'],
  [/^\/sandtable/, '毛公山数字沙盘'],
  [/^\/favorites/, '个人收藏与足迹'],
  [/^\/admin/, '内容管理'],
  [/^\/school/, '山东大学软件学院'],
  [/^\/sources/, '资料来源与版权'],
  [/^\/about/, '关于平台'],
  [/^\/help/, '使用帮助']
]

function updateDocumentMetadata(to) {
  const section = pageTitles.find(([pattern]) => pattern.test(to.path))?.[1] || '页面未找到'
  document.title = `${section}｜毛公山红色数字文化平台`
  const ogTitle = document.querySelector('meta[property="og:title"]')
  if (ogTitle) ogTitle.setAttribute('content', document.title)
}

const routeThemes = [
  [/^\/$/, 'home'],
  [/^\/(scenery|gallery|images|photos|overview)/, 'forest'],
  [/^\/(party-history|red-events|spirits|red-culture|timeline|history|figures|heroes|stories|places|red-scenic|learning)/, 'history'],
  [/^\/(exhibitions|shandong-red|qingdao-red|youth-mission|conferences|red-books|red-relics|photo-compare|study-routes|videos)/, 'exhibition'],
  [/^\/(research|plan|team|project)/, 'research'],
  [/^\/school/, 'school'],
  [/^\/chat/, 'ai'],
  [/^\/(map|guide|sandtable)/, 'route'],
  [/^\/(results|achievements|news)/, 'results'],
  [/^\/(resources|audio|sources|favorites|search)/, 'archive']
]

function updateRouteTheme(to) {
  document.documentElement.dataset.theme = routeThemes.find(([pattern]) => pattern.test(to.path))?.[1] || 'paper'
}

// Vite 代码分包在浏览器缓存过旧时可能加载失败，仅自动刷新一次避免循环。
router.onError((error) => {
  const isChunkError = /Failed to fetch dynamically imported module|Importing a module script failed|Loading chunk/i.test(error?.message || '')
  if (!isChunkError) return
  const key = 'mgs-chunk-reload'
  let alreadyRetried = false
  try {
    alreadyRetried = sessionStorage.getItem(key) === '1'
  } catch {
    alreadyRetried = window.__mgsChunkReloaded === true
  }
  if (alreadyRetried) {
    try { sessionStorage.removeItem(key) } catch { window.__mgsChunkReloaded = false }
    window.location.replace('/?loadError=chunk')
    return
  }
  try { sessionStorage.setItem(key, '1') } catch { window.__mgsChunkReloaded = true }
  window.location.reload()
})

router.afterEach((to) => {
  updateDocumentMetadata(to)
  updateRouteTheme(to)
  try { sessionStorage.removeItem('mgs-chunk-reload') } catch { window.__mgsChunkReloaded = false }
})

export default router
