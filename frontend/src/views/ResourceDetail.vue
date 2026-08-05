<template>
  <div>
    <PageHero
      :title="item?.name || '数字资源详情'"
      :subtitle="item?.summary || '查看资源来源、分类、标签和公开说明。'"
      :image="assetUrl(item?.file_url || '/assets/images/culture/maogongshan-red-park-2022.jpg')"
      eyebrow="数字资源详情"
    />
    <main class="page" v-loading="loading">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: '/resources' }">数字资源库</el-breadcrumb-item>
        <el-breadcrumb-item>{{ item?.name || '资源详情' }}</el-breadcrumb-item>
      </el-breadcrumb>

      <el-alert v-if="error" :title="error" type="warning" show-icon :closable="false" />
      <el-empty v-if="!loading && !item" description="资源不存在或加载失败">
        <el-button type="primary" @click="$router.push('/resources')">返回资源库</el-button>
      </el-empty>
      <article v-if="item" class="resource-detail panel reveal">
        <el-tag type="danger">{{ item.type }}</el-tag>
        <h1>{{ item.name }}</h1>
        <p class="lead">{{ item.summary }}</p>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="来源">{{ item.source }}</el-descriptions-item>
          <el-descriptions-item label="发布时间">{{ item.uploaded_at }}</el-descriptions-item>
          <el-descriptions-item label="标签">{{ item.tags }}</el-descriptions-item>
          <el-descriptions-item label="浏览次数">{{ item.views }}</el-descriptions-item>
        </el-descriptions>
        <div class="actions">
          <el-button type="primary" @click="toggle">{{ favoriteLabel }}</el-button>
          <el-button plain @click="share">复制分享链接</el-button>
          <el-button v-if="item.file_url" plain tag="a" :href="assetUrl(item.file_url)" target="_blank">打开来源</el-button>
          <el-button plain @click="$router.push('/resources')">返回列表</el-button>
          <el-button plain @click="$router.push('/favorites')">查看收藏</el-button>
        </div>
      </article>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { http, assetUrl } from '../api/http'
import PageHero from '../components/PageHero.vue'
import { addRecentView, isFavorite, toggleFavorite } from '../utils/library'
import { copyText } from '../utils/clipboard'

const route = useRoute()
const item = ref(null)
const loading = ref(false)
const error = ref('')
const favoriteVersion = ref(0)
const favoriteKey = computed(() => item.value ? `resource:${item.value.id}` : '')
const favoriteLabel = computed(() => {
  favoriteVersion.value
  return favoriteKey.value && isFavorite(favoriteKey.value) ? '取消收藏' : '收藏资源'
})

function favoritePayload() {
  return {
    key: favoriteKey.value,
    type: '数字资源',
    title: item.value.name,
    summary: item.value.summary,
    url: `/resources/${item.value.id}`
  }
}

function toggle() {
  const added = toggleFavorite(favoritePayload())
  favoriteVersion.value += 1
  ElMessage.success(added ? '已收藏到本机浏览器' : '已取消收藏')
}

async function share() {
  const copied = await copyText(window.location.href)
  copied ? ElMessage.success('分享链接已复制') : ElMessage.warning('复制失败，请手动复制地址栏链接')
}

onMounted(async () => {
  loading.value = true
  try {
    item.value = (await http.get(`/api/resources/${route.params.id}`)).data
    addRecentView(favoritePayload())
  } catch {
    error.value = '该资源暂时无法读取，可能是链接无效或后端服务不可用。'
    item.value = null
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.resource-detail {
  max-width: 920px;
  padding: 28px;
  margin: 24px auto 0;
}

.resource-detail h1 {
  color: var(--red-dark);
  font-size: clamp(30px, 5vw, 52px);
}

.lead {
  color: var(--muted);
  font-size: 18px;
  line-height: 1.9;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 20px;
}
</style>
