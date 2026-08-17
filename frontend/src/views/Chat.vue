<template>
  <div class="ai-page-shell">
    <PageHero
      title="毛公山文化智能助手"
      subtitle="先检索本地知识库，再由大模型组织自然中文回答；每条事实都以页面下方的资料来源为依据。"
      image="/assets/images/banners/peak-red-flags-hero.webp"
      eyebrow="RAG · Local Knowledge · Grounded AI"
    />
    <main class="page chat-page">
      <section class="assistant-layout">
        <aside class="assistant-panel reveal">
          <div class="assistant-portrait">
            <SafeImage src="/assets/images/scenery/summit-terrace-panorama-detail.webp" alt="毛公山观景平台实景" kind="scenery" loading="eager" />
            <div class="assistant-emblem"><span>山</span><small>AI</small></div>
          </div>
          <p class="eyebrow">山河知语</p>
          <h2>资源库智能助手</h2>
          <p>融合毛公山自然景观、红色文化资料与山东大学软件学院社会实践成果。</p>

          <dl class="service-stats">
            <div><dt>知识文档</dt><dd>{{ service.knowledge_documents ?? '—' }}</dd></div>
            <div><dt>回答模式</dt><dd>{{ serviceLabel }}</dd></div>
            <div><dt>可靠降级</dt><dd>{{ service.fallback_available === false ? '不可用' : '已启用' }}</dd></div>
          </dl>
          <div class="service-state" :class="service.configured ? 'online' : 'fallback'">
            <i></i>
            <span>{{ service.configured ? `${service.provider} · ${service.model}` : '本地知识库模式' }}</span>
          </div>
          <div class="assistant-boundary">
            <strong>可信回答边界</strong>
            <span>不编造历史、票价、电话、开放时间和实时信息；资料不足时会直接说明。</span>
          </div>
          <RouterLink class="guide-link" to="/guide">进入语音讲解模式 →</RouterLink>
        </aside>

        <section class="chat-workspace reveal">
          <header class="workspace-head">
            <div>
              <span>毛公山知识库在线</span>
              <h2>想了解什么？</h2>
            </div>
            <button type="button" :disabled="busy || !messages.length" @click="clearChat">清空对话</button>
          </header>

          <div class="suggestions" aria-label="推荐问题">
            <button v-for="item in suggestions" :key="item" type="button" :disabled="busy" @click="ask(item)">{{ item }}</button>
          </div>

          <div ref="chatBox" class="chat-box" role="log" aria-live="polite" aria-label="知识助手对话记录">
            <div v-if="!messages.length && !busy" class="empty-conversation">
              <span>问</span>
              <h3>从一座山开始，连接地方记忆与红色文化</h3>
              <p>可以询问毛公山特色、红色文化内容、游览路线、资料来源或社会实践过程。</p>
            </div>

            <article v-for="(msg, index) in messages" :key="msg.id || index" class="message-row" :class="msg.role">
              <div class="avatar" aria-hidden="true">{{ msg.role === 'user' ? '我' : '山' }}</div>
              <div class="bubble">
                <p class="message-text">{{ msg.text }}</p>
                <p v-if="msg.notice" class="degrade-notice">{{ msg.notice }}</p>
                <div v-if="msg.sources?.length" class="sources">
                  <strong>参考资料</strong>
                  <a
                    v-for="(source, sourceIndex) in msg.sources"
                    :key="`${source.title}-${source.source_url}`"
                    :href="source.source_url || '/sources'"
                    :target="source.source_url?.startsWith('http') ? '_blank' : undefined"
                    :rel="source.source_url?.startsWith('http') ? 'noopener noreferrer' : undefined"
                  >
                    <b>{{ sourceIndex + 1 }}</b>
                    <span>{{ source.title }}</span>
                    <small>{{ source.source_name }} · {{ source.verification_status }}</small>
                  </a>
                </div>
                <div v-if="msg.role === 'assistant' && msg.text" class="message-actions">
                  <button type="button" @click="copyAnswer(msg.text)">复制</button>
                  <button type="button" @click="speak(msg.text)">朗读</button>
                  <button v-if="index === messages.length - 1" type="button" :disabled="busy" @click="regenerate">重新生成</button>
                  <span>{{ msg.mode === 'rag_llm' ? 'RAG 大模型' : '本地检索' }}</span>
                </div>
              </div>
            </article>

            <div v-if="loading" class="message-row assistant" role="status">
              <div class="avatar" aria-hidden="true">山</div>
              <div class="bubble loading-bubble"><span></span><span></span><span></span><em>正在检索资料并组织回答</em></div>
            </div>
          </div>

          <div v-if="followUps.length && !busy" class="follow-ups">
            <span>继续追问</span>
            <button v-for="item in followUps" :key="item" type="button" @click="ask(item)">{{ item }}</button>
          </div>

          <div class="chat-input">
            <el-input
              v-model="question"
              type="textarea"
              :autosize="{ minRows: 1, maxRows: 5 }"
              maxlength="300"
              show-word-limit
              resize="none"
              placeholder="请输入问题，Enter 发送，Shift + Enter 换行"
              :disabled="loading"
              @keydown.enter.exact.prevent="ask(question)"
            />
            <el-button v-if="busy" class="stop-button" @click="stopGeneration">停止生成</el-button>
            <el-button v-else type="primary" :disabled="!question.trim()" @click="ask(question)">发送问题</el-button>
          </div>
          <el-alert v-if="error" :title="error" type="error" show-icon :closable="false" />
          <p class="privacy-note">对话仅用于本次知识库问答；API Key 始终保存在后端环境变量中，不会发送到浏览器。</p>
        </section>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { http } from '../api/http'
import PageHero from '../components/PageHero.vue'
import SafeImage from '../components/SafeImage.vue'
import { copyText } from '../utils/clipboard'
import { readStorage, removeStorage, writeStorage } from '../utils/storage'

const HISTORY_KEY = 'mg_chat_history_v2'
const defaultSuggestions = [
  '毛公山为什么叫毛公山？',
  '毛公山有哪些红色文化内容？',
  '怎么规划毛公山游览路线？',
  '山东大学软件学院为什么建设这个平台？',
  '团队进行了哪些社会实践？',
  '这些图片来自哪里？'
]

const storedMessages = readStorage(HISTORY_KEY, [])
const messages = ref(Array.isArray(storedMessages)
  ? storedMessages.filter((item) => ['user', 'assistant'].includes(item?.role) && typeof item?.text === 'string').slice(-24)
  : [])
const suggestions = ref(defaultSuggestions)
const followUps = ref([])
const service = ref({ configured: false, fallback_available: true, knowledge_documents: null, mode: 'local_retrieval' })
const question = ref('')
const loading = ref(false)
const typing = ref(false)
const error = ref('')
const chatBox = ref(null)
const busy = computed(() => loading.value || typing.value)
const serviceLabel = computed(() => service.value.configured ? 'RAG 大模型' : '本地检索')
let activeController = null
let typingTimer = 0

function messageId() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

function formatApiError(err) {
  if (err?.code === 'ERR_CANCELED') return '已停止本次生成。'
  const detail = err?.response?.data?.detail
  if (Array.isArray(detail)) return detail.map((item) => item.msg).filter(Boolean).join('；') || '输入内容不符合要求。'
  if (typeof detail === 'string') return detail
  return '问答服务暂时不可用，请稍后重试。'
}

function historyPayload() {
  return messages.value
    .filter((item) => item.text && !item.typing)
    .slice(-10)
    .map((item) => ({ role: item.role, content: item.text.slice(0, 2000) }))
}

function typeAnswer(message, fullText) {
  window.clearInterval(typingTimer)
  const reducedMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
  if (reducedMotion || fullText.length < 24) {
    message.text = fullText
    typing.value = false
    return
  }
  message.text = ''
  message.typing = true
  typing.value = true
  let cursor = 0
  typingTimer = window.setInterval(() => {
    const step = /[，。！？\n]/.test(fullText[cursor] || '') ? 1 : 3
    cursor = Math.min(fullText.length, cursor + step)
    message.text = fullText.slice(0, cursor)
    if (cursor >= fullText.length) {
      window.clearInterval(typingTimer)
      message.typing = false
      typing.value = false
    }
  }, 18)
}

async function submit(value, appendUser = true) {
  const text = String(value || '').trim()
  if (!text || busy.value) return
  const history = historyPayload()
  if (appendUser) messages.value.push({ id: messageId(), role: 'user', text })
  question.value = ''
  loading.value = true
  error.value = ''
  followUps.value = []
  activeController = new AbortController()
  try {
    const res = await http.post('/api/chat', { question: text, history }, {
      signal: activeController.signal,
      timeout: 28000
    })
    const assistant = {
      id: messageId(),
      role: 'assistant',
      text: '',
      sources: res.data.sources || [],
      mode: res.data.mode || 'local_retrieval',
      notice: res.data.notice || ''
    }
    messages.value.push(assistant)
    followUps.value = Array.isArray(res.data.follow_up_suggestions) ? res.data.follow_up_suggestions : []
    loading.value = false
    typeAnswer(assistant, res.data.answer || '当前资源库暂未收录足够资料。')
  } catch (err) {
    loading.value = false
    error.value = formatApiError(err)
  } finally {
    activeController = null
  }
}

function ask(text) { return submit(text, true) }

function stopGeneration() {
  activeController?.abort()
  activeController = null
  window.clearInterval(typingTimer)
  const current = messages.value.at(-1)
  if (current?.typing) current.typing = false
  loading.value = false
  typing.value = false
}

function regenerate() {
  const assistantIndex = [...messages.value].reverse().findIndex((item) => item.role === 'assistant')
  if (assistantIndex < 0) return
  const actualAssistantIndex = messages.value.length - 1 - assistantIndex
  const user = [...messages.value.slice(0, actualAssistantIndex)].reverse().find((item) => item.role === 'user')
  if (!user) return
  messages.value.splice(actualAssistantIndex, 1)
  submit(user.text, false)
}

function clearChat() {
  stopGeneration()
  window.speechSynthesis?.cancel()
  messages.value = []
  followUps.value = []
  error.value = ''
  removeStorage(HISTORY_KEY)
}

async function copyAnswer(text) {
  const copied = await copyText(text)
  ElMessage[copied ? 'success' : 'warning'](copied ? '回答已复制' : '复制失败，请手动选择文本')
}

function speak(text) {
  if (!window.speechSynthesis || !text) return
  window.speechSynthesis.cancel()
  const utterance = new SpeechSynthesisUtterance(text.replace(/\n/g, '。'))
  utterance.lang = 'zh-CN'
  utterance.rate = 0.92
  window.speechSynthesis.speak(utterance)
}

async function scrollToLatest() {
  await nextTick()
  if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight
}

watch(messages, (value) => {
  writeStorage(HISTORY_KEY, value.map(({ typing: _typing, ...item }) => item).slice(-24))
  scrollToLatest()
}, { deep: true })
watch(busy, scrollToLatest)

onMounted(async () => {
  const [suggestionResult, statusResult] = await Promise.allSettled([
    http.get('/api/chat/suggestions'),
    http.get('/api/chat/status')
  ])
  if (suggestionResult.status === 'fulfilled' && Array.isArray(suggestionResult.value.data)) {
    suggestions.value = suggestionResult.value.data
  }
  if (statusResult.status === 'fulfilled') service.value = statusResult.value.data
  scrollToLatest()
})

onBeforeUnmount(() => {
  stopGeneration()
  window.speechSynthesis?.cancel()
})
</script>

<style scoped>
.ai-page-shell {
  background:
    linear-gradient(180deg, rgba(13, 35, 37, .94), rgba(244, 238, 220, .96) 42%),
    url('/assets/images/banners/mountain-view-west-hero.webp') center top/cover fixed;
}
.chat-page { max-width: 1260px; }
.assistant-layout { display:grid;grid-template-columns:minmax(260px,340px) minmax(0,1fr);gap:clamp(18px,3vw,34px);align-items:start; }
.assistant-panel,.chat-workspace { border:1px solid rgba(255,255,255,.38);box-shadow:0 24px 70px rgba(20,34,32,.16);backdrop-filter:blur(18px); }
.assistant-panel { position:sticky;top:94px;padding:18px;color:#f8efdc;background:linear-gradient(155deg,rgba(37,72,67,.95),rgba(74,18,23,.94));border-radius:24px;overflow:hidden; }
.assistant-panel::after { position:absolute;right:-60px;bottom:-70px;width:190px;height:190px;border:1px solid rgba(229,191,93,.3);border-radius:50%;content:""; }
.assistant-portrait { position:relative;height:210px;border-radius:17px;overflow:hidden; }
.assistant-portrait::after { position:absolute;inset:0;background:linear-gradient(180deg,transparent 30%,rgba(20,40,38,.8));content:""; }
.assistant-emblem { position:absolute;z-index:2;right:16px;bottom:14px;display:grid;place-items:center;width:68px;height:68px;color:#fff5d6;background:rgba(139,30,36,.92);border:1px solid rgba(240,205,119,.7);border-radius:50%; }
.assistant-emblem span { font:700 26px/1 Georgia,"STSong",serif; }.assistant-emblem small{font-size:10px;letter-spacing:.16em}
.assistant-panel h2 { margin:4px 0 8px;font-size:28px; }.assistant-panel>p:not(.eyebrow){color:rgba(255,245,220,.76);line-height:1.8}
.service-stats { display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin:18px 0; }
.service-stats div { padding:10px 6px;text-align:center;background:rgba(255,255,255,.07);border-radius:10px; }.service-stats dt{font-size:11px;color:rgba(255,245,220,.58)}.service-stats dd{margin:6px 0 0;font-weight:800;font-size:13px}
.service-state { display:flex;align-items:center;gap:8px;padding:9px 11px;background:rgba(0,0,0,.13);border-radius:10px;font-size:12px; }.service-state i{width:8px;height:8px;background:#72d2a1;border-radius:50%;box-shadow:0 0 0 5px rgba(114,210,161,.12)}.service-state.fallback i{background:#e8bf60}
.assistant-boundary { display:grid;gap:5px;padding:13px;margin:15px 0;background:rgba(255,255,255,.07);border-left:3px solid #e8bf60;border-radius:0 9px 9px 0; }.assistant-boundary span{font-size:12px;line-height:1.7;color:rgba(255,245,220,.7)}
.guide-link { position:relative;z-index:1;color:#f1ce76;font-weight:700; }
.chat-workspace { min-height:720px;padding:clamp(16px,2.5vw,28px);background:rgba(255,252,244,.9);border-radius:24px; }
.workspace-head { display:flex;align-items:center;justify-content:space-between;gap:14px;margin-bottom:16px; }.workspace-head span{color:#3b746a;font-size:12px;font-weight:800;letter-spacing:.1em}.workspace-head h2{margin:4px 0;color:#491218;font-size:clamp(24px,3vw,36px)}.workspace-head button,.message-actions button{padding:6px 9px;color:#6c403e;background:transparent;border:0;cursor:pointer}.workspace-head button:disabled{opacity:.4}
.suggestions { display:flex;gap:8px;overflow-x:auto;padding:2px 2px 14px;scrollbar-width:thin; }.suggestions button,.follow-ups button{flex:none;padding:9px 13px;color:#704237;background:#fff;border:1px solid rgba(139,30,36,.16);border-radius:999px;cursor:pointer}.suggestions button:hover,.follow-ups button:hover{color:#8b1e24;border-color:#b7863c;background:#fff8e9}
.chat-box { min-height:470px;max-height:610px;padding:clamp(12px,2vw,22px);overflow-y:auto;overscroll-behavior:contain;background:linear-gradient(rgba(248,244,232,.86),rgba(239,247,243,.8)),url('/assets/images/red-culture/exhibition-calligraphy-thumb.webp') center/cover;border:1px solid rgba(83,87,73,.14);border-radius:18px; }
.empty-conversation { display:grid;place-items:center;max-width:560px;margin:90px auto;text-align:center;color:#5f6256}.empty-conversation>span{display:grid;place-items:center;width:58px;height:58px;color:#fff;background:linear-gradient(135deg,#8b1e24,#315f58);border-radius:20px;font:700 28px Georgia}.empty-conversation h3{margin:18px 0 6px;color:#491218;font-size:24px}.empty-conversation p{line-height:1.8}
.message-row { display:flex;gap:10px;align-items:flex-start;margin:15px 0; }.message-row.user{flex-direction:row-reverse}.avatar{flex:none;display:grid;place-items:center;width:34px;height:34px;color:#fff;background:#315f58;border-radius:12px;font-weight:800}.user .avatar{background:#8b1e24}
.bubble { max-width:min(82%,720px);padding:13px 15px;color:#393d37;background:#fffdf7;border:1px solid rgba(83,87,73,.15);border-radius:4px 16px 16px;box-shadow:0 8px 24px rgba(31,46,42,.07);line-height:1.85}.user .bubble{color:#fff8e6;background:linear-gradient(135deg,#8b1e24,#a52d32);border:0;border-radius:16px 4px 16px 16px}.message-text{margin:0;white-space:pre-wrap}.degrade-notice{padding:8px 10px;color:#795311;background:#fff3cc;border-radius:8px;font-size:12px}
.sources { display:grid;gap:7px;padding-top:12px;margin-top:12px;border-top:1px solid rgba(83,87,73,.13)}.sources>strong{color:#6c241f;font-size:13px}.sources a{display:grid;grid-template-columns:24px 1fr;column-gap:7px;padding:8px;color:#4e4038;background:#f8f3e7;border-radius:9px}.sources b{grid-row:1/3;display:grid;place-items:center;width:22px;height:22px;color:#fff;background:#a67b35;border-radius:50%;font-size:11px}.sources small{color:#82766a;font-size:11px}
.message-actions { display:flex;align-items:center;gap:3px;margin-top:8px;color:#81766b;font-size:11px}.message-actions span{margin-left:auto}.message-actions button:hover{color:#8b1e24}.message-actions button:disabled{opacity:.4}
.loading-bubble{display:flex;align-items:center;gap:6px}.loading-bubble span{width:7px;height:7px;background:#8b1e24;border-radius:50%;animation:typing-dot 1.1s infinite ease-in-out}.loading-bubble span:nth-child(2){animation-delay:.14s}.loading-bubble span:nth-child(3){animation-delay:.28s}.loading-bubble em{margin-left:5px;color:#766e64;font-size:12px;font-style:normal}@keyframes typing-dot{0%,70%,100%{opacity:.3;transform:translateY(0)}35%{opacity:1;transform:translateY(-3px)}}
.follow-ups{display:flex;align-items:center;gap:7px;overflow-x:auto;padding:12px 2px}.follow-ups>span{flex:none;color:#73675e;font-size:12px;font-weight:700}.follow-ups button{padding:7px 10px;font-size:12px}
.chat-input{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;align-items:end}.chat-input :deep(.el-textarea__inner){min-height:48px;padding:12px 14px;background:#fff;border-radius:12px;box-shadow:0 0 0 1px rgba(83,87,73,.2) inset}.chat-input :deep(.el-button){min-height:46px;margin:0}.stop-button{color:#8b1e24;border-color:#8b1e24}.privacy-note{margin:10px 2px 0;color:#887e73;font-size:11px}
@media(max-width:900px){.assistant-layout{grid-template-columns:1fr}.assistant-panel{position:relative;top:auto}.assistant-portrait{height:170px}.service-stats{grid-template-columns:repeat(3,1fr)}.chat-workspace{min-height:0}.chat-box{min-height:420px;max-height:60vh}.bubble{max-width:92%}}
@media(max-width:600px){.chat-page{width:calc(100% - 16px);padding-top:18px}.assistant-panel,.chat-workspace{padding:14px;border-radius:16px}.assistant-panel{display:grid;grid-template-columns:92px 1fr;column-gap:12px}.assistant-portrait{grid-row:1/4;width:92px;height:112px}.assistant-emblem{width:44px;height:44px}.assistant-emblem span{font-size:18px}.assistant-panel .eyebrow,.assistant-panel h2,.assistant-panel>p{grid-column:2}.service-stats,.service-state,.assistant-boundary,.guide-link{grid-column:1/-1}.assistant-panel h2{font-size:22px}.workspace-head{align-items:flex-start}.workspace-head button{font-size:12px}.chat-box{min-height:390px;padding:9px}.message-row{gap:6px}.avatar{width:29px;height:29px;border-radius:9px;font-size:12px}.bubble{max-width:calc(100% - 35px);padding:11px 12px}.sources a{grid-template-columns:22px 1fr}.chat-input{grid-template-columns:1fr}.chat-input :deep(.el-button){width:100%}.empty-conversation{margin:55px auto}.empty-conversation h3{font-size:20px}}
@media(prefers-reduced-motion:reduce){.loading-bubble span{animation:none}.ai-page-shell{background-attachment:scroll}}
</style>
