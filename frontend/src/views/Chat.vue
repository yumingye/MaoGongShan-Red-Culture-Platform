<template>
  <main class="chat-page page">
    <section class="chat-card">
      <header class="chat-header">
        <div><p>毛公山红色数字文化平台</p><h1>毛公山 AI 助手</h1><span>由大语言模型生成回答，支持连续对话与 Markdown。</span></div>
        <button :disabled="busy" @click="newChat">新对话</button>
      </header>
      <div ref="chatBox" class="chat-log" role="log" aria-live="polite">
        <div v-if="!messages.length" class="welcome"><b>山</b><h2>有什么想聊的？</h2><p>可以问毛公山、红色文化，也可以进行一般性的 AI 对话。</p><div><button v-for="item in suggestions" :key="item" :disabled="busy" @click="ask(item)">{{ item }}</button></div></div>
        <article v-for="(msg, index) in messages" :key="msg.id" class="message" :class="msg.role">
          <div class="avatar">{{ msg.role === 'user' ? '我' : '山' }}</div>
          <div class="message-content"><strong>{{ msg.role === 'user' ? '你' : '毛公山 AI 助手' }}</strong>
            <div v-if="msg.role === 'user'" class="markdown user-text">{{ msg.text }}</div>
            <div v-else class="markdown" v-html="renderMarkdown(msg.text)"></div>
            <div v-if="msg.role === 'assistant' && msg.text && !msg.pending" class="actions"><button @click="copyAnswer(msg.text)">复制</button><button v-if="index === lastAssistantIndex" :disabled="busy" @click="regenerate">重新生成</button></div>
          </div>
        </article>
        <div v-if="thinking" class="message assistant"><div class="avatar">山</div><div class="message-content thinking"><strong>毛公山 AI 助手</strong><span></span><span></span><span></span><em>AI 正在思考…</em></div></div>
      </div>
      <p v-if="error" class="error">{{ error }} <button v-if="lastQuestion && !busy" @click="regenerate">重试</button></p>
      <div class="composer"><textarea v-model="question" :disabled="busy" rows="1" maxlength="1000" placeholder="发送消息，Enter 发送，Shift + Enter 换行" @keydown.enter.exact.prevent="ask(question)" @input="resizeInput" ref="inputBox"></textarea><button v-if="busy" class="stop" @click="stopGeneration">停止生成</button><button v-else class="send" :disabled="!question.trim()" @click="ask(question)">发送</button></div>
      <p class="tip">对话由后端安全调用 DeepSeek；不会使用本地资料检索来冒充 AI 回答。</p>
    </section>
  </main>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { API_BASE_URL } from '../api/http'
import { copyText } from '../utils/clipboard'
import { readStorage, removeStorage, writeStorage } from '../utils/storage'

const HISTORY_KEY = 'mgs_deepseek_chat_v1'
const suggestions = ['毛公山在哪里？', '介绍一下毛公山的红色文化价值', '什么是人工智能？']
const stored = readStorage(HISTORY_KEY, [])
const messages = ref(Array.isArray(stored) ? stored.filter(x => ['user', 'assistant'].includes(x?.role) && typeof x.text === 'string').slice(-20) : [])
const question = ref(''), thinking = ref(false), error = ref(''), chatBox = ref(null), inputBox = ref(null)
const busy = computed(() => thinking.value)
const lastAssistantIndex = computed(() => { for (let i = messages.value.length - 1; i >= 0; i--) if (messages.value[i].role === 'assistant') return i; return -1 })
const lastQuestion = computed(() => [...messages.value].reverse().find(x => x.role === 'user')?.text || '')
let controller = null
const id = () => `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`
const apiUrl = `${API_BASE_URL || ''}/api/chat`

function escapeHtml(value) { return String(value || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;') }
function inline(value) { return escapeHtml(value).replace(/`([^`]+)`/g, '<code>$1</code>').replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>').replace(/\*([^*]+)\*/g, '<em>$1</em>') }
function renderMarkdown(text) {
  const lines = String(text || '').split('\n'); let html = '', list = null, code = false
  const close = () => { if (list) html += `</${list}>`; list = null }
  for (const raw of lines) {
    if (/^```/.test(raw)) { close(); html += code ? '</code></pre>' : '<pre><code>'; code = !code; continue }
    if (code) { html += `${escapeHtml(raw)}\n`; continue }
    const heading = raw.match(/^(#{1,3})\s+(.+)/); const quote = raw.match(/^>\s?(.*)/); const unordered = raw.match(/^[-*+]\s+(.+)/); const ordered = raw.match(/^\d+\.\s+(.+)/)
    if (heading) { close(); html += `<h${heading[1].length}>${inline(heading[2])}</h${heading[1].length}>` }
    else if (quote) { close(); html += `<blockquote>${inline(quote[1])}</blockquote>` }
    else if (unordered || ordered) { const kind = unordered ? 'ul' : 'ol'; if (list !== kind) { close(); html += `<${kind}>`; list = kind }; html += `<li>${inline((unordered || ordered)[1])}</li>` }
    else { close(); html += raw.trim() ? `<p>${inline(raw)}</p>` : '' }
  }
  close(); return html + (code ? '</code></pre>' : '')
}
function history() { return messages.value.filter(x => x.text && !x.pending).slice(-10).map(x => ({ role: x.role, content: x.text.slice(0, 1800) })) }
function parseSse(buffer, onEvent) { const blocks = buffer.split('\n\n'); for (let i = 0; i < blocks.length - 1; i++) { const type = blocks[i].match(/^event:\s*(.+)$/m)?.[1]; const data = blocks[i].match(/^data:\s*(.+)$/m)?.[1]; if (type && data) { try { onEvent(type, JSON.parse(data)) } catch { /* incomplete/malformed provider event */ } } }; return blocks.at(-1) || '' }
async function submit(value, addUser = true) {
  const text = String(value || '').trim(); if (!text || busy.value) return
  const payloadHistory = history(); if (addUser) messages.value.push({ id: id(), role: 'user', text }); question.value = ''; error.value = ''; thinking.value = true
  const assistant = { id: id(), role: 'assistant', text: '', pending: true }; messages.value.push(assistant); controller = new AbortController()
  try {
    const response = await fetch(apiUrl, { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream' }, body: JSON.stringify({ question: text, history: payloadHistory, stream: true }), signal: controller.signal })
    if (!response.ok || !response.body) throw new Error(response.status === 429 ? 'AI 服务当前繁忙，请稍后重新提问。' : 'AI 服务暂时不可用，请稍后再试。')
    const reader = response.body.getReader(), decoder = new TextDecoder(); let buffer = '', remoteError = ''
    while (true) { const { done, value } = await reader.read(); if (done) break; buffer = parseSse(buffer + decoder.decode(value, { stream: true }), (type, data) => { if (type === 'delta') assistant.text += data.content || ''; if (type === 'error') remoteError = data.message || 'AI 服务暂时不可用，请稍后再试。' }); await scroll() }
    buffer = parseSse(buffer + decoder.decode(), () => {})
    if (remoteError) throw new Error(remoteError)
    if (!assistant.text) throw new Error('AI 服务暂时不可用，请稍后再试。')
  } catch (err) {
    if (err?.name !== 'AbortError') error.value = err?.message || 'AI 服务暂时不可用，请稍后再试。'
    if (!assistant.text) messages.value = messages.value.filter(x => x !== assistant)
  } finally { assistant.pending = false; thinking.value = false; controller = null; await scroll() }
}
function ask(text) { submit(text, true) }
function stopGeneration() { controller?.abort(); controller = null; thinking.value = false }
function regenerate() { const ai = lastAssistantIndex.value; const user = ai >= 0 ? [...messages.value.slice(0, ai)].reverse().find(x => x.role === 'user') : null; if (!user) return; if (ai >= 0) messages.value.splice(ai, 1); submit(user.text, false) }
function newChat() { stopGeneration(); messages.value = []; error.value = ''; removeStorage(HISTORY_KEY) }
async function copyAnswer(text) { const ok = await copyText(text); ElMessage[ok ? 'success' : 'warning'](ok ? '回答已复制' : '复制失败，请手动选择文本') }
async function scroll() { await nextTick(); if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight }
function resizeInput() { const el = inputBox.value; if (el) { el.style.height = 'auto'; el.style.height = `${Math.min(el.scrollHeight, 160)}px` } }
watch(messages, value => { writeStorage(HISTORY_KEY, value.map(({ pending, ...item }) => item).slice(-20)); scroll() }, { deep: true })
onBeforeUnmount(stopGeneration)
</script>

<style scoped>
.chat-page{max-width:1080px;padding:32px 0}.chat-card{overflow:hidden;border:1px solid rgba(90,47,29,.15);border-radius:24px;background:#fffdf8;box-shadow:0 22px 70px rgba(48,34,24,.12)}.chat-header{display:flex;justify-content:space-between;gap:18px;padding:28px 32px;color:#fff7e9;background:linear-gradient(125deg,#153d38,#74262a)}.chat-header p{margin:0;color:#e8c878;font-size:12px;font-weight:700;letter-spacing:.12em}.chat-header h1{margin:6px 0;font-size:30px}.chat-header span{opacity:.8}.chat-header button,.actions button{border:0;background:transparent;color:inherit;cursor:pointer}.chat-header button{align-self:start;padding:8px 12px;border:1px solid rgba(255,255,255,.4);border-radius:9px}.chat-log{min-height:520px;max-height:66vh;padding:24px 9%;overflow:auto;background:linear-gradient(180deg,#fffdfa,#f4f0e8)}.welcome{max-width:620px;margin:100px auto;text-align:center;color:#6e6257}.welcome>b,.avatar{display:grid;place-items:center;width:38px;height:38px;border-radius:12px;background:#1c5a52;color:#fff;font-weight:800}.welcome>b{width:56px;height:56px;margin:auto;border-radius:18px;font-size:25px}.welcome h2{color:#4d2022}.welcome button{margin:5px;padding:9px 13px;color:#6b3630;border:1px solid #ddc7b0;border-radius:99px;background:#fff;cursor:pointer}.message{display:flex;gap:12px;align-items:flex-start;margin:20px 0}.message.user{flex-direction:row-reverse}.user .avatar{background:#8b3035}.message-content{max-width:82%;padding:13px 17px;border:1px solid #e3dbcf;border-radius:5px 18px 18px;background:#fff;line-height:1.8}.user .message-content{color:#fff9ed;background:#873037;border:0;border-radius:18px 5px 18px 18px}.message-content>strong{display:block;margin-bottom:4px;font-size:12px;color:#807267}.user .message-content>strong{color:#f2d69b}.markdown :deep(p){margin:7px 0}.markdown :deep(h1),.markdown :deep(h2),.markdown :deep(h3){margin:15px 0 8px;color:#592021;line-height:1.35}.markdown :deep(ul),.markdown :deep(ol){padding-left:22px;margin:8px 0}.markdown :deep(blockquote){margin:10px 0;padding:4px 12px;border-left:3px solid #c3994c;background:#fbf4e4;color:#665b52}.markdown :deep(pre){overflow:auto;padding:11px;border-radius:8px;background:#282c2a;color:#f8f6ef}.markdown :deep(code){padding:1px 4px;border-radius:4px;background:#eee9df}.markdown :deep(pre code){padding:0;background:none}.user-text{white-space:pre-wrap}.actions{margin-top:9px}.actions button{margin-right:12px;color:#80553f;font-size:12px}.thinking{display:flex;align-items:center;gap:6px;color:#75695e}.thinking strong{margin-right:4px}.thinking span{width:6px;height:6px;background:#8b3035;border-radius:50%;animation:dot 1s infinite}.thinking span:nth-of-type(2){animation-delay:.15s}.thinking span:nth-of-type(3){animation-delay:.3s}.thinking em{margin-left:5px;font-size:12px;font-style:normal}.composer{display:flex;gap:10px;padding:18px 28px;border-top:1px solid #e8e0d5;background:#fff}.composer textarea{flex:1;max-height:160px;padding:12px 14px;border:1px solid #cfc3b5;border-radius:14px;outline:none;resize:none;font:inherit;line-height:1.5}.composer textarea:focus{border-color:#976744;box-shadow:0 0 0 3px rgba(151,103,68,.12)}.composer button{align-self:end;min-width:88px;height:44px;border:0;border-radius:12px;background:#1d5b52;color:#fff;cursor:pointer}.composer .stop{background:#8b3035}.composer button:disabled{opacity:.45;cursor:not-allowed}.error{margin:0 28px 10px;padding:9px 12px;color:#8b3035;background:#fff0ec;border-radius:9px}.error button{margin-left:8px;color:inherit;border:0;background:transparent;text-decoration:underline;cursor:pointer}.tip{margin:0;padding:0 28px 16px;color:#93887d;font-size:12px}@keyframes dot{50%{transform:translateY(-4px);opacity:.35}}@media(max-width:640px){.chat-page{width:100%;padding:0}.chat-card{border-radius:0}.chat-header{padding:22px 18px}.chat-header h1{font-size:25px}.chat-log{min-height:58vh;padding:18px}.welcome{margin:60px auto}.message-content{max-width:calc(100% - 44px);padding:11px 13px}.composer{padding:12px}.tip{padding:0 12px 14px}.error{margin:0 12px 8px}}@media(prefers-reduced-motion:reduce){.thinking span{animation:none}}
</style>
