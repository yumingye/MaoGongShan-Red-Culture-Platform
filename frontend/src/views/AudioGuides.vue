<template>
  <div>
    <PageHero title="音频讲解" subtitle="面向展厅、答辩和在线浏览的毛公山文化语音导览。" image="/assets/images/scenery/maogongshan-sunset-rock.png" eyebrow="Audio Guide" />
    <main class="page">
      <header class="audio-intro">
        <span>无需下载音频文件</span>
        <h2>选择讲解主题，浏览器即可自然语音朗读</h2>
        <p>讲解稿来自本站公开内容与资料整理；语音由浏览器本地朗读能力生成，不代表景区官方讲解。</p>
      </header>
      <div class="grid grid-4">
        <article v-for="item in displayList" :key="item.id" class="audio-card panel reveal">
          <SafeImage :src="item.image" :alt="item.title" />
          <h3>{{ item.title }}</h3>
          <p>{{ item.summary }}</p>
          <el-button type="primary" plain @click="$router.push(`/audio/${item.id}`)">进入讲解</el-button>
        </article>
      </div>
    </main>
  </div>
</template>
<script setup>
import { computed, onMounted, ref } from 'vue'
import { http } from '../api/http'
import PageHero from '../components/PageHero.vue'
import SafeImage from '../components/SafeImage.vue'
import { offlineNarrations } from '../data/offlineFallbacks'

const list = ref(offlineNarrations)
const displayList = computed(() => list.value.length ? list.value : offlineNarrations)
onMounted(async () => {
  try {
    const rows = (await http.get('/api/audio-guides')).data
    if (Array.isArray(rows) && rows.length) list.value = rows
  } catch {
    list.value = offlineNarrations
  }
})
</script>
<style scoped>
.audio-intro { max-width: 760px; margin: 0 0 28px; }
.audio-intro span { color: var(--gold); font-size: 13px; font-weight: 800; letter-spacing: .08em; }
.audio-intro h2 { margin: 7px 0; color: var(--red-dark); font-size: clamp(26px, 4vw, 38px); }
.audio-intro p { margin: 0; color: var(--muted); line-height: 1.8; }
.audio-card { padding: 18px; }
.audio-card :deep(.safe-image) { width: 100%; height: 170px; border-radius: 12px; }
.audio-card h3 { color: var(--red-dark); }
.audio-card p { color: var(--muted); line-height: 1.75; }
</style>
