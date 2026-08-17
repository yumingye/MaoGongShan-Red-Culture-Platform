<template>
  <div>
    <PageHero
      title="使用帮助"
      subtitle="面向课程展示、社会实践答辩和公众浏览的操作指南。"
      image="/assets/images/maogongshan/resource-021.jpg"
    />
    <main class="page help-page">
      <section class="help-grid">
        <article v-for="item in guides" :key="item.title" class="panel help-card reveal">
          <el-icon><component :is="item.icon" /></el-icon>
          <h2>{{ item.title }}</h2>
          <p>{{ item.summary }}</p>
          <RouterLink :to="item.to">进入功能</RouterLink>
        </article>
      </section>

      <section class="panel faq-panel">
        <SectionTitle title="常见问题" desc="遇到服务、地图、图片、问答或数据来源问题时，可以先查看这里。" />
        <el-collapse>
          <el-collapse-item v-for="item in faqs" :key="item.q" :title="item.q" :name="item.q">
            <p>{{ item.a }}</p>
          </el-collapse-item>
        </el-collapse>
      </section>
    </main>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import { Collection, MapLocation, Microphone, Picture, Search, Service, Setting, Star } from '@element-plus/icons-vue'
import PageHero from '../components/PageHero.vue'
import SectionTitle from '../components/SectionTitle.vue'

const guides = [
  { title: '全局搜索', summary: '输入关键词后可同时检索历史事件、人物、数字资源、图库和景点。搜索结果可以直接进入详情页。', to: '/search?q=毛公山', icon: Search },
  { title: '数字资源库', summary: '通过资源类型和关键词筛选文献、调研记录、实践成果、图片和音频资料。', to: '/resources', icon: Collection },
  { title: '全景图库', summary: '按自然风光、红色文化、实践记录等分类浏览图片，并查看来源和版权说明。', to: '/scenery', icon: Picture },
  { title: '数字地图', summary: '配置高德 Key 后显示在线地图；无 Key 时自动降级为静态导览和点位表。', to: '/map', icon: MapLocation },
  { title: '智能问答', summary: '基于本地知识库回答毛公山、城阳红色文化、山软青年和平台使用问题。', to: '/chat', icon: Service },
  { title: '音频讲解', summary: '提供毛公山概览、红色文化价值、实践项目和软件学院专题讲解稿。', to: '/audio', icon: Microphone },
  { title: '收藏中心', summary: '收藏喜欢的图片和资料，查看最近浏览记录，便于展示时快速回到重点内容。', to: '/favorites', icon: Star },
  { title: '后台管理', summary: '管理员可维护资源、历史、人物和图片资料；正式部署前请修改默认密码。', to: '/admin', icon: Setting }
]

const faqs = [
  { q: '后端无法访问怎么办？', a: '公网版本请检查 Render 后端服务状态与 VITE_API_BASE_URL；本地开发请确认 FastAPI 服务已经启动。接口暂时不可用时，页面会自动展示缓存或公开基础资料。' },
  { q: '前端没有数据怎么办？', a: '先检查页面错误提示和后端健康状态。开发环境通过 Vite 代理访问 /api，公网构建通过环境变量访问后端，不需要在页面中写死地址。' },
  { q: '地图没有显示高德地图怎么办？', a: '在 frontend/.env 中配置 VITE_AMAP_KEY 和 VITE_AMAP_SECURITY_CODE；未配置时页面会显示本地静态导览。' },
  { q: '问答会不会编造历史事实？', a: '当前问答使用本地知识库检索，并显示相关资料来源。知识库没有足够资料时会提示暂未收录，不会把不确定内容当作史实。' },
  { q: '图片可以用于正式宣传吗？', a: '平台记录了图片来源和版权说明。用于商业传播、出版或正式公开参赛前，应再次联系来源单位确认授权边界。' },
  { q: '收藏会上传个人信息吗？', a: '不会。收藏和最近浏览记录保存在本机浏览器 localStorage 中，平台不会收集手机号、邮箱、地址等隐私信息。' }
]
</script>

<style scoped>
.help-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
  margin-bottom: 24px;
}

.help-card {
  padding: 22px;
}

.help-card .el-icon {
  width: 44px;
  height: 44px;
  color: #fff;
  background: var(--red);
  border-radius: 12px;
}

.help-card h2 {
  color: var(--red-dark);
}

.help-card p,
.faq-panel p {
  color: var(--muted);
  line-height: 1.8;
}

.help-card a {
  color: var(--red);
  font-weight: 700;
}

.faq-panel {
  padding: 22px;
}

@media (max-width: 1100px) {
  .help-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .help-grid {
    grid-template-columns: 1fr;
  }
}
</style>
