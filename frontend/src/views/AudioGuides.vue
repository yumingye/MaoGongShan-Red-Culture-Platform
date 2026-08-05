<template>
  <div>
    <PageHero title="音频讲解" subtitle="面向展厅、答辩和在线浏览的毛公山文化语音导览。" image="/assets/images/scenery/maogongshan-sunset-rock.png" eyebrow="Audio Guide" />
    <main class="page">
      <div class="grid grid-4">
        <article v-for="item in list" :key="item.id" class="audio-card panel reveal">
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
import { onMounted, ref } from 'vue'
import { http } from '../api/http'
import PageHero from '../components/PageHero.vue'
import SafeImage from '../components/SafeImage.vue'
const list = ref([])
onMounted(async()=>{ try { list.value=(await http.get('/api/audio-guides')).data } catch { list.value=[] } })
</script>
<style scoped>
.audio-card { padding: 18px; }
.audio-card :deep(.safe-image) { width: 100%; height: 170px; border-radius: 12px; }
.audio-card h3 { color: var(--red-dark); }
.audio-card p { color: var(--muted); line-height: 1.75; }
</style>
