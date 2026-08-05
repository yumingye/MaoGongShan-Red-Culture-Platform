<template>
  <div>
    <PageHero
      title="收藏中心"
      subtitle="本地保存感兴趣的图片、资源、历史资料和最近浏览记录，便于答辩演示时快速回到重点内容。"
      image="/assets/images/commons/shandong-university-charter-1901-jpg.jpg"
    />

    <main class="page">
      <section class="favorite-actions panel">
        <div>
          <strong>本地收藏与浏览记录</strong>
          <p>收藏和最近浏览仅保存在当前浏览器，不上传个人信息，也不收集访问者隐私。</p>
        </div>
        <div class="action-buttons">
          <el-button type="danger" plain @click="clearAllFavorites">清空收藏</el-button>
          <el-button plain @click="clearAllRecent">清空最近浏览</el-button>
        </div>
      </section>

      <section class="content-grid">
        <article class="panel list-panel">
          <h2>我的收藏</h2>
          <el-empty
            v-if="!favorites.length"
            description="还没有收藏内容。可以在图片、资源和详情页点击收藏。"
          />
          <RouterLink v-for="item in favorites" :key="item.key" class="library-row" :to="item.url">
            <span>{{ item.type }}</span>
            <strong>{{ item.title }}</strong>
            <small>{{ formatTime(item.savedAt) }}</small>
            <el-button text type="danger" @click.prevent="remove(item.key)">取消收藏</el-button>
          </RouterLink>
        </article>

        <article class="panel list-panel">
          <h2>最近浏览</h2>
          <el-empty v-if="!recent.length" description="浏览详情页后会自动记录在这里。" />
          <RouterLink v-for="item in recent" :key="item.key" class="library-row" :to="item.url">
            <span>{{ item.type }}</span>
            <strong>{{ item.title }}</strong>
            <small>{{ formatTime(item.viewedAt) }}</small>
          </RouterLink>
        </article>
      </section>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import PageHero from '../components/PageHero.vue'
import { clearFavorites, clearRecentViews, getFavorites, getRecentViews, removeFavorite } from '../utils/library'

const favorites = ref([])
const recent = ref([])

function refresh() {
  favorites.value = getFavorites()
  recent.value = getRecentViews()
}

function formatTime(value) {
  if (!value) return ''
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}

function remove(key) {
  removeFavorite(key)
  refresh()
  ElMessage.success('已取消收藏')
}

async function clearAllFavorites() {
  try {
    await ElMessageBox.confirm('确定清空全部收藏吗？', '确认操作', { type: 'warning' })
    clearFavorites()
    refresh()
    ElMessage.success('收藏已清空')
  } catch {
    // 用户取消时不需要提示。
  }
}

async function clearAllRecent() {
  try {
    await ElMessageBox.confirm('确定清空最近浏览记录吗？', '确认操作', { type: 'warning' })
    clearRecentViews()
    refresh()
    ElMessage.success('最近浏览已清空')
  } catch {
    // 用户取消时不需要提示。
  }
}

onMounted(refresh)
</script>

<style scoped>
.favorite-actions,
.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 18px;
  align-items: center;
  margin-bottom: 22px;
}

.favorite-actions {
  padding: 18px;
}

.favorite-actions p {
  margin: 6px 0 0;
  color: var(--muted);
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.content-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  align-items: stretch;
}

.list-panel {
  padding: 20px;
}

.list-panel h2 {
  margin-top: 0;
  color: var(--red-dark);
}

.library-row {
  display: grid;
  grid-template-columns: 90px minmax(0, 1fr) 150px auto;
  gap: 12px;
  align-items: center;
  padding: 14px 0;
  color: inherit;
  text-decoration: none;
  border-bottom: 1px solid var(--line);
}

.library-row span {
  color: var(--gold);
  font-weight: 700;
}

.library-row strong {
  color: var(--red-dark);
}

.library-row small {
  color: var(--muted);
}

@media (max-width: 900px) {
  .favorite-actions,
  .content-grid,
  .library-row {
    grid-template-columns: 1fr;
  }

  .action-buttons {
    flex-wrap: wrap;
  }
}
</style>
