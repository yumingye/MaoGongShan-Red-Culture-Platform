<template>
  <div>
    <PageHero v-if="event" :title="event.title" :subtitle="event.summary" :image="assetUrl(event.image_url)" />
    <main class="page" v-loading="loading">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: '/history' }">红色历史</el-breadcrumb-item>
        <el-breadcrumb-item>{{ event?.title || '资料详情' }}</el-breadcrumb-item>
      </el-breadcrumb>

      <el-empty v-if="!loading && !event" description="资料不存在或加载失败" />
      <template v-if="event">
        <article class="detail-layout">
          <section class="detail-main panel reveal">
            <SafeImage class="detail-cover" :src="event.image_url" :alt="event.title" />
            <h1>{{ event.title }}</h1>
            <div class="meta-line">
              <el-tag type="danger">{{ event.category }}</el-tag>
              <el-tag>{{ event.event_time }}</el-tag>
              <el-tag type="info">{{ event.location }}</el-tag>
              <el-tag :type="event.verified ? 'success' : 'warning'">{{ event.verification_status || '来源已标注' }}</el-tag>
            </div>
            <p class="lead">{{ event.summary }}</p>
            <div class="article-body">
              <h2>详细正文</h2>
              <p>{{ event.details }}</p>
              <h2>资料来源</h2>
              <p>{{ event.source }}</p>
              <h2>参考资料</h2>
              <p>{{ event.reference_materials || '来源记录见详情页和资料来源说明。' }}</p>
            </div>
            <div class="actions">
              <el-button type="primary" @click="toggle">{{ favoriteLabel }}</el-button>
              <el-button plain @click="copyShare">复制分享链接</el-button>
              <el-button plain @click="$router.push('/history')">返回列表</el-button>
              <el-button plain @click="$router.push('/favorites')">查看收藏</el-button>
            </div>
          </section>

          <aside class="detail-side">
            <div class="panel side-box reveal">
              <h3>资料信息</h3>
              <p><strong>时间：</strong>{{ event.event_time }}</p>
              <p><strong>地点：</strong>{{ event.location }}</p>
              <p><strong>相关人物：</strong>{{ event.related_people || '公开资料未列明' }}</p>
              <p><strong>分类：</strong>{{ event.category }}</p>
              <p><strong>资料状态：</strong>{{ event.verification_status || '来源已标注' }}</p>
            </div>
            <div class="panel side-box reveal">
              <h3>相关历史推荐</h3>
              <router-link v-for="item in event.related" :key="item.id" class="related-link" :to="`/events/${item.id}`">
                <span>{{ item.event_time }}</span>
                <strong>{{ item.title }}</strong>
              </router-link>
            </div>
          </aside>
        </article>
      </template>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { http, assetUrl } from '../api/http'
import PageHero from '../components/PageHero.vue'
import SafeImage from '../components/SafeImage.vue'
import { addRecentView, isFavorite, toggleFavorite } from '../utils/library'
import { copyText } from '../utils/clipboard'

const route = useRoute()
const event = ref(null)
const loading = ref(false)
const favoriteVersion = ref(0)
const favoriteKey = computed(() => event.value ? `event:${event.value.id}` : '')
const favoriteLabel = computed(() => {
  favoriteVersion.value
  return favoriteKey.value && isFavorite(favoriteKey.value) ? '取消收藏' : '收藏资料'
})

function payload() {
  return {
    key: favoriteKey.value,
    type: '历史资料',
    title: event.value.title,
    summary: event.value.summary,
    url: `/events/${event.value.id}`
  }
}

async function load() {
  loading.value = true
  try {
    event.value = (await http.get(`/api/events/${route.params.id}`)).data
    addRecentView(payload())
  } finally {
    loading.value = false
  }
}

function toggle() {
  const added = toggleFavorite(payload())
  favoriteVersion.value += 1
  ElMessage.success(added ? '已收藏资料' : '已取消收藏')
}

async function copyShare() {
  const copied = await copyText(window.location.href)
  copied ? ElMessage.success('分享链接已复制') : ElMessage.warning('复制失败，请手动复制地址栏链接')
}

watch(() => route.params.id, load)
onMounted(load)
</script>

<style scoped>
.detail-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 24px;
  margin-top: 22px;
}

.detail-main {
  padding: 24px;
}

.detail-cover {
  width: 100%;
  max-height: 440px;
  object-fit: cover;
  border-radius: 12px;
}

.detail-main h1 {
  color: var(--red-dark);
  font-size: clamp(28px, 4vw, 42px);
}

.lead {
  color: #4e463f;
  font-size: 18px;
  line-height: 1.9;
}

.article-body {
  color: #3e352f;
  line-height: 2;
}

.article-body h2,
.side-box h3 {
  color: var(--red-dark);
}

.side-box {
  padding: 18px;
  margin-bottom: 18px;
}

.side-box p {
  color: var(--muted);
  line-height: 1.8;
}

.related-link {
  display: grid;
  gap: 4px;
  padding: 12px 0;
  border-bottom: 1px solid var(--line);
}

.related-link span {
  color: var(--gold);
  font-size: 12px;
}

.related-link strong {
  color: var(--red-dark);
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 20px;
}

@media (max-width: 900px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }
}
</style>
