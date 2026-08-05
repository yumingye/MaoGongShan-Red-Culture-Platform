<template>
  <div>
    <PageHero
      v-if="article"
      :title="article.title"
      :subtitle="article.summary"
      :image="article.image"
      :eyebrow="article.scope"
    />

    <main class="page" v-loading="loading">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: '/party-history' }">红色党史学习</el-breadcrumb-item>
        <el-breadcrumb-item>{{ article?.title || '专题详情' }}</el-breadcrumb-item>
      </el-breadcrumb>

      <el-alert v-if="error" :title="error" type="error" show-icon class="detail-alert" />

      <article v-if="article" class="detail-shell">
        <section class="article-main">
          <div class="boundary-note">
            <strong>{{ article.scope }}</strong>
            <span>{{ article.scope === '毛公山核心资源' ? '本条与毛公山主题直接相关。' : '本条为拓展学习资料，不作为毛公山地方历史事实。' }}</span>
          </div>

          <div class="fact-grid">
            <div><span>时间</span><strong>{{ article.event_time }}</strong></div>
            <div><span>地点</span><strong>{{ article.location }}</strong></div>
            <div><span>相关人物</span><strong>{{ article.related_people }}</strong></div>
            <div><span>资料分类</span><strong>{{ article.category }} · {{ article.sub_category }}</strong></div>
          </div>

          <div class="article-copy">
            <section v-for="section in contentSections" :key="section.title" class="copy-section reveal">
              <h2>{{ section.title }}</h2>
              <p>{{ section.content }}</p>
              <figure v-for="media in mediaFor(section.title)" :key="media.media_key" class="section-media">
                <SafeImage
                  :src="media.image_url"
                  :fallback="media.fallback_image"
                  :alt="media.alt"
                  show-status
                />
                <figcaption>
                  <div class="media-labels">
                    <el-tag effect="dark">{{ media.media_type }}</el-tag>
                    <el-tag type="success">{{ media.verification_status }}</el-tag>
                  </div>
                  <strong>{{ media.title }}</strong>
                  <p>{{ media.caption }}</p>
                  <dl>
                    <div><dt>地点</dt><dd>{{ media.location || '见正文' }}</dd></div>
                    <div><dt>时间</dt><dd>{{ media.year || '见来源页' }}</dd></div>
                    <div><dt>来源</dt><dd><a v-if="media.source_url" :href="media.source_url" target="_blank" rel="noopener noreferrer">{{ media.source_name }}</a><span v-else>{{ media.source_name }}</span></dd></div>
                    <div><dt>版权</dt><dd>{{ media.copyright_note }}</dd></div>
                  </dl>
                </figcaption>
              </figure>
            </section>
          </div>

          <section class="mini-timeline reveal">
            <h2>专题学习路径</h2>
            <div><i></i><strong>回到历史现场</strong><span>{{ article.event_time }} · {{ article.location }}</span></div>
            <div><i></i><strong>理解实践主体</strong><span>{{ article.related_people }}</span></div>
            <div><i></i><strong>连接当代行动</strong><span>{{ article.youth_insight }}</span></div>
          </section>

          <section class="knowledge-card">
            <span>精神内涵</span>
            <h2>{{ article.spirit }}</h2>
            <p>{{ article.youth_insight }}</p>
          </section>

          <section class="source-panel panel">
            <h3>资料来源与核验说明</h3>
            <p>{{ article.source_name }}</p>
            <a v-if="article.source_url" :href="article.source_url" target="_blank" rel="noopener noreferrer">打开原始公开来源</a>
            <el-tag type="success">{{ article.verification_status }}</el-tag>
          </section>

          <section class="detail-interactions">
            <RouterLink v-if="relatedVideo" class="media-entry" :to="relatedVideo.url"><strong>{{ relatedVideo.title }}</strong><span>画面与当前专题对应，并逐幅标注媒体性质</span></RouterLink>
            <RouterLink v-else class="media-entry" to="/timeline"><strong>在准确时间轴中定位本专题</strong><span>节点显示对应时间、地点、人物、图片性质与说明</span></RouterLink>
            <button type="button" class="quiz-entry" @click="showAnswer = !showAnswer"><strong>知识自测：为什么要把精神放回具体历史条件中理解？</strong><span>{{ showAnswer ? '因为精神来自具体实践，脱离背景容易变成空泛标签。' : '点击翻开答案' }}</span></button>
          </section>

          <div class="actions">
            <el-button type="primary" @click="toggle">{{ favoriteLabel }}</el-button>
            <el-button plain @click="share">复制分享链接</el-button>
            <el-button plain @click="$router.push('/party-history')">返回专题列表</el-button>
          </div>
          <nav class="article-pager">
            <RouterLink v-if="previous" :to="`/learning/${previous.id}`">上一篇<br><strong>{{ previous.title }}</strong></RouterLink>
            <RouterLink v-if="next" :to="`/learning/${next.id}`">下一篇<br><strong>{{ next.title }}</strong></RouterLink>
          </nav>
        </section>

        <aside class="article-side">
          <div class="panel toc">
            <span>阅读线索</span>
            <strong>背景与概况</strong>
            <strong>主要过程</strong>
            <strong>历史意义与精神内涵</strong>
            <strong>青年启示</strong>
          </div>
          <div class="panel related">
            <h3>相关推荐</h3>
            <RouterLink v-for="item in article.related" :key="item.id" :to="`/learning/${item.id}`">
              <span>{{ item.category }}</span>
              <strong>{{ item.title }}</strong>
            </RouterLink>
          </div>
        </aside>
      </article>

      <el-empty v-if="!loading && !article" description="该专题链接无效或资料读取失败">
        <el-button type="primary" @click="$router.push('/party-history')">进入党史学习馆</el-button>
      </el-empty>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { http } from '../api/http'
import PageHero from '../components/PageHero.vue'
import SafeImage from '../components/SafeImage.vue'
import { addRecentView, isFavorite, toggleFavorite } from '../utils/library'

const route = useRoute()
const article = ref(null)
const loading = ref(false)
const error = ref('')
const version = ref(0)
const showAnswer = ref(false)
const allArticles = ref([])
const key = computed(() => article.value ? `learning:${article.value.id}` : '')
const favoriteLabel = computed(() => {
  version.value
  return key.value && isFavorite(key.value) ? '取消收藏' : '收藏专题'
})
const contentSections = computed(() => {
  const blocks = String(article.value?.content || '').split(/\n\s*\n/).filter(Boolean)
  return blocks.map((block, index) => {
    const lines = block.split('\n')
    return { title: lines.length > 1 ? lines.shift() : `专题解读 ${index + 1}`, content: lines.join('\n') || block }
  })
})
const relatedVideo = computed(() => {
  const exact = {
    'long-march': { url: '/videos/long-march-route', title: '观看长征路线动态图解' }
  }
  return exact[article.value?.slug] || null
})
const currentIndex = computed(() => allArticles.value.findIndex((item) => String(item.id) === String(article.value?.id)))
const previous = computed(() => currentIndex.value > 0 ? allArticles.value[currentIndex.value - 1] : null)
const next = computed(() => currentIndex.value >= 0 && currentIndex.value < allArticles.value.length - 1 ? allArticles.value[currentIndex.value + 1] : null)

function mediaFor(sectionTitle) {
  return (article.value?.media || []).filter((item) => item.section_id === sectionTitle)
}

function libraryPayload() {
  return { key: key.value, type: '党史学习', title: article.value.title, summary: article.value.summary, url: `/learning/${article.value.id}` }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [response, listResponse] = await Promise.all([
      http.get(`/api/learning-articles/${route.params.id}`),
      http.get('/api/learning-articles', { params: { page: 1, page_size: 100 } })
    ])
    article.value = response.data
    allArticles.value = listResponse.data.items || listResponse.data
    addRecentView(libraryPayload())
  } catch (requestError) {
    article.value = null
    error.value = requestError?.response?.data?.detail || '专题资料加载失败，请稍后重试。'
  } finally {
    loading.value = false
  }
}

function toggle() {
  const added = toggleFavorite(libraryPayload())
  version.value += 1
  ElMessage.success(added ? '已收藏专题' : '已取消收藏')
}

async function share() {
  try {
    await navigator.clipboard.writeText(window.location.href)
    ElMessage.success('分享链接已复制')
  } catch {
    ElMessage.warning('浏览器未授予复制权限，请手动复制地址栏链接')
  }
}

watch(() => route.params.id, load)
onMounted(load)
</script>

<style scoped>
.detail-alert { margin: 22px 0; }
.detail-shell { display: grid; grid-template-columns: minmax(0, 1fr) 300px; gap: 36px; margin-top: 28px; }
.article-main { min-width: 0; }
.boundary-note { display: flex; flex-wrap: wrap; gap: 10px 18px; align-items: center; padding: 16px 18px; margin-bottom: 20px; color: #6b3f13; background: #fff4d7; border-left: 4px solid var(--gold); }
.fact-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
.fact-grid div { display: grid; gap: 7px; padding: 18px; border-right: 1px solid var(--line); border-bottom: 1px solid var(--line); }
.fact-grid span, .toc > span, .related span { color: var(--gold); font-size: 13px; }
.fact-grid strong { color: var(--red-dark); line-height: 1.6; }
.article-copy { margin: 38px 0; color: #3d3732; font-size: 17px; line-height: 2.15; }
.copy-section { padding: 24px 0; border-top: 1px solid var(--line); }
.copy-section h2 { margin: 0 0 12px; color: var(--red-dark); font-size: clamp(23px, 3vw, 31px); }
.copy-section p { margin: 0; white-space: pre-line; }
.section-media { display: grid; grid-template-columns: minmax(260px, .9fr) minmax(0, 1.1fr); gap: 22px; margin: 24px 0 4px; padding: 18px; background: #fffaf0; border: 1px solid var(--line); border-radius: 10px; }
.section-media :deep(.safe-image) { min-height: 300px; border-radius: 7px; }
.section-media figcaption { min-width: 0; }
.section-media figcaption > strong { display: block; margin: 14px 0 8px; color: var(--red-dark); font-size: 21px; }
.section-media figcaption > p { color: #4f4841; font-size: 15px; line-height: 1.85; }
.media-labels { display: flex; flex-wrap: wrap; gap: 8px; }
.section-media dl { display: grid; gap: 8px; margin: 16px 0 0; font-size: 13px; }
.section-media dl div { display: grid; grid-template-columns: 54px 1fr; gap: 8px; }
.section-media dt { color: var(--gold); font-weight: 800; }
.section-media dd { margin: 0; color: var(--muted); overflow-wrap: anywhere; }
.section-media a { color: var(--red); font-weight: 700; }
.mini-timeline { position: relative; display: grid; gap: 18px; padding: 28px; margin: 32px 0; color: #fff8e6; background: #321014; border-radius: 12px; overflow: hidden; }
.mini-timeline::after { position: absolute; top: 0; right: -60px; width: 230px; height: 230px; border: 1px solid rgba(243,216,145,.3); border-radius: 50%; content: ''; animation: orbit 9s linear infinite; }
.mini-timeline h2 { margin: 0; color: var(--gold-soft); }
.mini-timeline div { position: relative; z-index: 1; display: grid; grid-template-columns: 18px 150px 1fr; gap: 12px; align-items: start; }
.mini-timeline i { width: 12px; height: 12px; margin-top: 5px; background: var(--gold); border-radius: 50%; box-shadow: 0 0 0 7px rgba(201,162,75,.15); }
.mini-timeline span { color: #eadfd6; line-height: 1.7; }
.knowledge-card { padding: clamp(24px, 5vw, 46px); color: #fff7df; background: linear-gradient(135deg, #541015, #8f1d22 62%, #2e6357); border-radius: 8px; box-shadow: var(--shadow); }
.knowledge-card span { color: var(--gold-soft); }
.knowledge-card h2 { margin: 12px 0; font-size: clamp(24px, 4vw, 38px); line-height: 1.45; }
.knowledge-card p { margin: 0; line-height: 1.9; }
.source-panel { padding: 24px; margin-top: 26px; }
.source-panel h3 { margin-top: 0; color: var(--red-dark); }
.source-panel a { display: inline-block; margin-right: 14px; color: var(--red); font-weight: 700; }
.actions { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 24px; }
.detail-interactions { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 24px; }
.detail-interactions > * { display: grid; gap: 8px; min-height: 130px; padding: 20px; text-align: left; border: 1px solid var(--line); border-radius: 10px; cursor: pointer; }
.media-entry { color: #fff8e6; background: linear-gradient(135deg,var(--red-dark),var(--red)); }
.quiz-entry { color: var(--red-dark); background: #fff2d5; }
.detail-interactions span { line-height: 1.7; }
.article-pager { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 24px; }
.article-pager a { padding: 16px; color: var(--red-dark); background: #fffaf0; border: 1px solid var(--line); border-radius: 10px; }
@keyframes orbit { to { transform: rotate(360deg); } }
.article-side { display: grid; align-content: start; gap: 18px; position: sticky; top: 96px; }
.toc, .related { padding: 20px; }
.toc { display: grid; gap: 13px; }
.toc strong { padding-bottom: 10px; color: var(--red-dark); border-bottom: 1px solid var(--line); }
.related a { display: grid; gap: 5px; padding: 13px 0; border-bottom: 1px solid var(--line); }
.related strong { color: var(--red-dark); line-height: 1.5; }
@media (max-width: 900px) {
  .detail-shell { grid-template-columns: 1fr; }
  .article-side { position: static; }
  .section-media { grid-template-columns: 1fr; }
}
@media (max-width: 620px) {
  .fact-grid { grid-template-columns: 1fr; }
  .cover { min-height: 260px; }
  .detail-interactions, .article-pager { grid-template-columns: 1fr; }
  .mini-timeline div { grid-template-columns: 18px 1fr; }
  .mini-timeline span { grid-column: 2; }
}
@media (prefers-reduced-motion: reduce) { .mini-timeline::after { animation: none; } }
</style>
