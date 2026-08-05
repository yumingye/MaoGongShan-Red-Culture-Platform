<template>
  <div>
    <PageHero
      :title="topic?.title || '专题未找到'"
      :subtitle="topic?.subtitle || '当前专题不存在或路径输入有误。'"
      :image="topic?.image || fallbackImage"
      :eyebrow="topic?.category || '专题页面'"
    />

    <main class="page">
      <el-breadcrumb separator="/" class="topic-breadcrumb">
        <el-breadcrumb-item to="/">首页</el-breadcrumb-item>
        <el-breadcrumb-item>{{ topic?.category || '专题' }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ topic?.title || '未找到' }}</el-breadcrumb-item>
      </el-breadcrumb>

      <template v-if="topic">
        <section class="topic-layout">
          <article class="panel topic-main reveal">
            <SafeImage :src="topic.image" :alt="topic.title" />
            <p class="topic-summary">{{ topic.subtitle }}</p>
            <el-alert
              v-if="topic.notice"
              class="content-notice"
              title="内容性质说明"
              :description="topic.notice"
              type="warning"
              :closable="false"
              show-icon
            />
            <section v-for="section in topic.sections" :key="section.title" class="topic-section">
              <h2>{{ section.title }}</h2>
              <p>{{ section.content }}</p>
            </section>
          </article>

          <aside class="panel topic-aside reveal">
            <strong>专题信息</strong>
            <dl>
              <div>
                <dt>栏目</dt>
                <dd>{{ topic.category }}</dd>
              </div>
              <div>
                <dt>来源</dt>
                <dd>{{ topic.source }}</dd>
              </div>
              <div>
                <dt>标签</dt>
                <dd>
                  <el-tag v-for="tag in topic.tags" :key="tag" size="small" type="danger">{{ tag }}</el-tag>
                </dd>
              </div>
            </dl>
            <el-button type="primary" plain @click="copyLink">复制专题链接</el-button>
            <el-button @click="$router.back()">返回上一页</el-button>
          </aside>
        </section>

        <SectionTitle title="相关入口" desc="继续浏览同一主题下的列表、地图、问答或资源详情。" />
        <div class="grid grid-3">
          <RouterLink v-for="link in topic.links" :key="link" class="related-entry panel reveal" :to="link">
            <el-icon><Connection /></el-icon>
            <strong>{{ labelFor(link) }}</strong>
            <span>{{ link }}</span>
          </RouterLink>
        </div>
      </template>

      <el-empty v-else description="没有找到对应专题，请从导航栏重新进入。">
        <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
      </el-empty>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Connection } from '@element-plus/icons-vue'
import PageHero from '../components/PageHero.vue'
import SectionTitle from '../components/SectionTitle.vue'
import SafeImage from '../components/SafeImage.vue'
import { getTopicPage } from '../data/topicPages'
import { copyText } from '../utils/clipboard'

const props = defineProps({
  slugPrefix: { type: String, default: '' },
  fixedSlug: { type: String, default: '' }
})

const route = useRoute()
const fallbackImage = '/assets/images/fallback/fallback-real-scenery.jpg'
const topic = computed(() => getTopicPage(props.fixedSlug || `${props.slugPrefix}${route.params.slug || ''}`))

const routeLabels = {
  '/overview': '毛公山概览',
  '/map': '数字地图',
  '/places': '地点资源',
  '/sources': '资料来源',
  '/guide': 'AI 数字讲解',
  '/chat': '智能问答',
  '/scenery': '全景图库',
  '/school': '山软青年',
  '/project': '实践项目',
  '/resources': '数字资源库',
  '/history': '红色历史',
  '/stories': '红色故事',
  '/timeline': '历史时间轴',
  '/research': '实践调研',
  '/achievements': '成果展示',
  '/team': '团队介绍',
  '/help': '使用帮助',
  '/audio': '音频讲解'
}

function labelFor(link) {
  if (routeLabels[link]) return routeLabels[link]
  if (link.startsWith('/gallery')) return '图库专题'
  if (link.startsWith('/resources/category')) return '资源分类'
  if (link.startsWith('/map/topic')) return '地图专题'
  if (link.startsWith('/overview')) return '概览专题'
  return '相关页面'
}

async function copyLink() {
  const copied = await copyText(window.location.href)
  copied ? ElMessage.success('专题链接已复制') : ElMessage.warning('复制失败，请手动复制地址栏链接')
}
</script>

<style scoped>
.topic-breadcrumb {
  margin-bottom: 22px;
}

.topic-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 22px;
  margin-bottom: 40px;
}

.topic-main {
  overflow: hidden;
}

.topic-main :deep(.safe-image) {
  width: 100%;
  max-height: 460px;
  object-fit: cover;
  display: block;
}

.topic-summary {
  margin: 0;
  padding: 24px 28px 4px;
  color: var(--muted);
  font-size: 18px;
  line-height: 1.9;
}

.content-notice {
  width: auto;
  margin: 18px 28px 20px;
}

.content-notice :deep(.el-alert__description) {
  line-height: 1.8;
}

.topic-section {
  padding: 10px 28px 26px;
}

.topic-section h2 {
  margin: 0 0 10px;
  color: var(--red-dark);
}

.topic-section p {
  margin: 0;
  color: var(--ink);
  line-height: 2;
  white-space: pre-line;
}

.topic-aside {
  position: sticky;
  top: 94px;
  align-self: start;
  padding: 20px;
}

.topic-aside strong {
  color: var(--red-dark);
  font-size: 20px;
}

.topic-aside dl {
  display: grid;
  gap: 14px;
  margin: 18px 0;
}

.topic-aside dt {
  color: var(--muted);
  font-size: 13px;
}

.topic-aside dd {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 4px 0 0;
  line-height: 1.7;
}

.topic-aside .el-button {
  width: 100%;
  margin: 8px 0 0;
}

.related-entry {
  display: grid;
  gap: 8px;
  padding: 20px;
}

.related-entry .el-icon {
  color: var(--red);
  font-size: 30px;
}

.related-entry strong {
  color: var(--red-dark);
}

.related-entry span {
  color: var(--muted);
  font-size: 13px;
}

@media (max-width: 900px) {
  .topic-layout {
    grid-template-columns: 1fr;
  }

  .topic-aside {
    position: static;
  }
}
</style>
