<template>
  <div>
    <PageHero
      title="毛公山数字讲解员"
      subtitle="基于资源库知识库、景点讲解词和语音合成能力，提供可听、可问、可浏览的智能导览。"
      image="/assets/images/culture/maogongshan-red-park-2022.jpg"
      eyebrow="AI智能讲解"
    />
    <main class="page">
      <section class="guide-shell">
        <aside class="guide-avatar panel reveal">
          <div class="avatar-orbit">
            <div class="avatar-core">讲</div>
          </div>
          <h2>毛公山数字讲解员</h2>
          <p>语音风格：博物馆讲解员 · 景区导游</p>
          <div class="voice-controls">
            <el-button type="primary" @click="speak(currentScript)">播放讲解</el-button>
            <el-button plain @click="stopSpeak">停止</el-button>
          </div>
        </aside>

        <section class="guide-main panel reveal">
          <h2>自然语言提问</h2>
          <div class="question-row">
            <el-input v-model="question" placeholder="例如：毛公山在哪里？怎么游览？这个项目是谁开发的？" @keyup.enter="ask" />
            <el-button type="primary" :loading="asking" @click="ask">提问</el-button>
          </div>
          <div class="quick-questions">
            <button v-for="item in quick" :key="item" @click="question = item; ask()">{{ item }}</button>
          </div>
          <article v-if="answer" class="answer-box">
            <h3>讲解回答</h3>
            <p>{{ answer }}</p>
            <el-button plain @click="speak(answer)">朗读回答</el-button>
          </article>
        </section>
      </section>

      <SectionTitle title="景点语音讲解" desc="每个主要点位均配有讲解词，可直接播放。" />
      <div class="grid grid-3">
        <article v-for="item in narrations" :key="item.id" class="narration-card reveal">
          <h3>{{ item.target_title }}</h3>
          <p>{{ item.script }}</p>
          <el-button type="primary" plain @click="speak(item.script)">播放</el-button>
        </article>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { http } from '../api/http'
import PageHero from '../components/PageHero.vue'
import SectionTitle from '../components/SectionTitle.vue'
import { offlineNarrations } from '../data/offlineFallbacks'

const question = ref('')
const answer = ref('')
const asking = ref(false)
const narrations = ref(offlineNarrations)
const quick = ['介绍一下毛公山', '毛公山有什么红色故事', '怎么游览毛公山', '这个项目是谁开发的', '软件学院为什么做这个项目']
const currentScript = computed(() => narrations.value[0]?.script || '欢迎来到青岛城阳毛公山红色文化数字资源库。')

async function ask() {
  const text = question.value.trim()
  if (!text) return
  asking.value = true
  try {
    const res = await http.post('/api/chat', { question: text })
    answer.value = res.data?.answer || '当前没有取得有效回答，请从推荐问题或资料来源页面继续浏览。'
  } catch {
    answer.value = '问答服务暂时无法连接。你仍可通过顶部搜索、全景图库、红色历史和资料来源页面浏览本地内容。'
  } finally {
    asking.value = false
  }
}

function speak(text) {
  if (!window.speechSynthesis || !text) return
  window.speechSynthesis.cancel()
  const parts = text.replace(/\n/g, '。').split('。').filter(Boolean)
  parts.forEach((part, index) => {
    const utterance = new SpeechSynthesisUtterance(`${part}。`)
    utterance.lang = 'zh-CN'
    utterance.rate = index % 2 ? 0.92 : 0.86
    utterance.pitch = index % 3 === 0 ? 1.05 : 0.98
    utterance.volume = 1
    window.speechSynthesis.speak(utterance)
  })
}

function stopSpeak() {
  window.speechSynthesis?.cancel()
}

onMounted(async () => {
  try {
    const rows = (await http.get('/api/narrations')).data
    if (Array.isArray(rows) && rows.length) narrations.value = rows
  } catch {
    narrations.value = offlineNarrations
  }
})
</script>

<style scoped>
.guide-shell {
  display: grid;
  grid-template-columns: 340px minmax(0, 1fr);
  gap: 24px;
}

.guide-avatar,
.guide-main,
.narration-card {
  padding: 24px;
}

.avatar-orbit {
  display: grid;
  place-items: center;
  width: 180px;
  height: 180px;
  margin: 0 auto 18px;
  border-radius: 50%;
  background:
    radial-gradient(circle, rgba(201, 162, 75, .34), transparent 58%),
    conic-gradient(from 0deg, var(--red), var(--gold), #2f6f5e, var(--red));
  animation: spin 9s linear infinite;
}

.avatar-core {
  display: grid;
  place-items: center;
  width: 118px;
  height: 118px;
  color: #fff8e6;
  background: linear-gradient(135deg, #541015, #8f1d22);
  border-radius: 50%;
  font-size: 54px;
  font-weight: 800;
}

.voice-controls,
.question-row {
  display: flex;
  gap: 12px;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 16px 0;
}

.quick-questions button {
  padding: 8px 12px;
  color: var(--red-dark);
  cursor: pointer;
  background: #fffaf0;
  border: 1px solid var(--line);
  border-radius: 999px;
}

.answer-box {
  padding: 18px;
  color: var(--muted);
  background: rgba(255, 250, 240, .82);
  border: 1px solid var(--line);
  border-radius: 12px;
  line-height: 1.9;
}

.narration-card {
  background:
    linear-gradient(135deg, rgba(255, 250, 240, .96), rgba(239, 247, 244, .9));
}

.narration-card h3 {
  color: var(--red-dark);
}

.narration-card p {
  color: var(--muted);
  line-height: 1.85;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 900px) {
  .guide-shell,
  .question-row {
    grid-template-columns: 1fr;
    flex-direction: column;
  }
}
</style>
