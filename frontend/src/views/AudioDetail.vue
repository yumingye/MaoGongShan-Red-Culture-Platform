<template>
  <div>
    <PageHero :title="item?.title || '音频讲解详情'" :subtitle="item?.summary || '使用浏览器普通话语音朗读平台讲解稿。'" :image="assetUrl(item?.image)" eyebrow="音频讲解详情" />
    <main class="page">
      <el-alert v-if="error" :title="error" type="warning" show-icon :closable="false" />
      <article v-if="item" class="audio-detail panel">
        <h1>{{ item.title }}</h1>
        <p>{{ item.script }}</p>
        <div class="player">
          <el-button type="primary" @click="speak">播放</el-button>
          <el-button plain @click="pause">暂停</el-button>
          <el-button plain @click="stop">停止</el-button>
          <span>时长：{{ item.duration }} · 音量由系统控制</span>
        </div>
      </article>
      <el-empty v-else description="该讲解条目不存在或暂时无法读取">
        <el-button type="primary" @click="$router.push('/audio')">返回音频列表</el-button>
      </el-empty>
    </main>
  </div>
</template>
<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { http, assetUrl } from '../api/http'
import PageHero from '../components/PageHero.vue'
const route=useRoute(); const item=ref(null); const error=ref('')
function speak(){ if(!item.value || !window.speechSynthesis) return; window.speechSynthesis.cancel(); const u=new SpeechSynthesisUtterance(item.value.script); u.lang='zh-CN'; u.rate=.9; u.pitch=1.03; window.speechSynthesis.speak(u) }
function pause(){ window.speechSynthesis?.pause() }
function stop(){ window.speechSynthesis?.cancel() }
onMounted(async()=>{
  try { item.value=(await http.get(`/api/audio-guides/${route.params.id}`)).data }
  catch { error.value='讲解资料暂时无法读取，其他音频条目仍可继续浏览。' }
})
</script>
<style scoped>
.audio-detail { max-width: 880px; margin: 24px auto 0; padding: 32px; }
.audio-detail h1 { color: var(--red-dark); font-size: clamp(30px, 5vw, 52px); }
.audio-detail p { color: var(--muted); line-height: 2; font-size: 18px; }
.player { display:flex; gap:12px; flex-wrap:wrap; align-items:center; margin-top:22px; }
.player span { color: var(--muted); }
</style>
