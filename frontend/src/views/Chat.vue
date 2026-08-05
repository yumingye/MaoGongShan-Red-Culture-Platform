<template>
  <div>
    <PageHero
      title="毛公山文化助手"
      subtitle="基于资源库知识库的自然语言问答，可回答毛公山、城阳、山东大学软件学院和项目技术相关问题。"
      image="/assets/images/culture/maogongshan-red-park-2022.jpg"
      eyebrow="AI Knowledge Assistant"
    />
    <main class="page chat-page">
      <section class="assistant-layout">
        <aside class="assistant-panel panel reveal">
          <div class="assistant-face">
            <span>AI</span>
          </div>
          <h2>资源库智能助手</h2>
          <p>回答来源优先来自 SQLite 知识库、公开资料来源和项目专题数据。</p>
          <el-button type="primary" @click="$router.push('/guide')">进入语音讲解模式</el-button>
        </aside>

        <section class="chat-workspace panel reveal">
          <div class="suggestions">
            <el-button v-for="item in suggestions" :key="item" plain @click="ask(item)">{{ item }}</el-button>
          </div>

          <div class="chat-box">
            <div v-for="(msg, index) in messages" :key="index" class="bubble" :class="msg.role">
              <p>{{ msg.text }}</p>
              <div v-if="msg.sources?.length" class="sources">
                <strong>参考来源</strong>
                <span v-for="source in msg.sources" :key="source.title">{{ source.title }} · {{ source.verification_status }}</span>
              </div>
              <el-button v-if="msg.role === 'assistant'" link type="primary" @click="speak(msg.text)">朗读</el-button>
            </div>
            <el-empty v-if="!messages.length" description="请选择推荐问题或输入问题" />
          </div>

          <div class="chat-input">
            <el-input v-model="question" placeholder="请输入你的问题" clearable @keyup.enter="ask(question)" />
            <el-button type="primary" :loading="loading" @click="ask(question)">发送</el-button>
            <el-button @click="messages = []">清空</el-button>
          </div>
          <el-alert v-if="error" :title="error" type="error" show-icon />
        </section>
      </section>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { http } from '../api/http'
import PageHero from '../components/PageHero.vue'

const defaultSuggestions = [
  '毛公山在哪里？',
  '毛公山有什么特色？',
  '如何规划毛公山游览路线？',
  '平台有哪些主要功能？',
  '山东大学软件学院团队进行了哪些工作？',
  '平台中的资料都经过考证了吗？'
]
const suggestions = ref(defaultSuggestions)
const messages = ref([])
const question = ref('')
const loading = ref(false)
const error = ref('')

async function ask(text) {
  const value = String(text || '').trim()
  if (!value) return
  question.value = ''
  messages.value.push({ role: 'user', text: value })
  loading.value = true
  error.value = ''
  try {
    const res = await http.post('/api/chat', { question: value })
    messages.value.push({ role: 'assistant', text: res.data.answer, sources: res.data.sources })
  } catch (err) {
    error.value = err?.response?.data?.detail || '问答服务暂时不可用，请稍后重试。'
  } finally {
    loading.value = false
  }
}

function speak(text) {
  if (!window.speechSynthesis || !text) return
  window.speechSynthesis.cancel()
  const utterance = new SpeechSynthesisUtterance(text.replace(/\n/g, '。'))
  utterance.lang = 'zh-CN'
  utterance.rate = 0.9
  utterance.pitch = 1.02
  window.speechSynthesis.speak(utterance)
}

onMounted(async () => {
  try {
    const payload = (await http.get('/api/chat/suggestions')).data
    suggestions.value = Array.isArray(payload) && payload.length ? payload : defaultSuggestions
  } catch {
    suggestions.value = defaultSuggestions
  }
})
</script>

<style scoped>
.chat-page {
  max-width: 1180px;
}

.assistant-layout {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  gap: 24px;
}

.assistant-panel,
.chat-workspace {
  padding: 24px;
}

.assistant-face {
  display: grid;
  place-items: center;
  width: 160px;
  height: 160px;
  margin: 0 auto 18px;
  color: #fff8e6;
  border-radius: 42% 58% 48% 52%;
  background:
    radial-gradient(circle at 35% 25%, rgba(255, 255, 255, .3), transparent 18%),
    linear-gradient(135deg, #8f1d22, #194156);
  box-shadow: 0 26px 55px rgba(84, 16, 21, .24);
}

.assistant-face span {
  font-size: 48px;
  font-weight: 900;
}

.assistant-panel h2 {
  color: var(--red-dark);
}

.assistant-panel p {
  color: var(--muted);
  line-height: 1.85;
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 18px;
}

.chat-box {
  min-height: 420px;
  padding: 18px;
  margin-bottom: 16px;
  background: linear-gradient(135deg, rgba(255, 250, 240, .8), rgba(239, 247, 244, .72));
  border: 1px solid var(--line);
  border-radius: 16px;
}

.bubble {
  max-width: 82%;
  padding: 14px 16px;
  margin: 10px 0;
  border-radius: 16px;
  line-height: 1.85;
}

.bubble.user {
  margin-left: auto;
  color: #fff8e6;
  background: var(--red);
}

.bubble.assistant {
  background: #fffaf0;
  border: 1px solid var(--line);
}

.sources {
  display: grid;
  gap: 6px;
  margin-top: 10px;
  color: var(--muted);
  font-size: 13px;
}

.chat-input {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 10px;
}

@media (max-width: 900px) {
  .assistant-layout,
  .chat-input {
    grid-template-columns: 1fr;
  }

  .bubble {
    max-width: 100%;
  }
}
</style>
