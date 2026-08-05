<template>
  <main class="page">
    <h1 class="section-title">后台管理</h1>
    <el-alert
      :title="publicReadOnly
        ? '当前公网展示实例为只读模式：浏览、搜索和问答正常，后台写入与上传已关闭。'
        : '管理员凭据仅通过后端环境变量配置，前端不保存默认密码。'"
      type="warning"
      show-icon
    />

    <el-card v-if="publicReadOnly" class="login-card read-only-card" shadow="never">
      <h2>公开展示模式</h2>
      <p>Render 免费实例使用项目内置数据库种子，运行期文件不会作为永久数据保存。为避免产生误导，公网版本不开放新增、修改、删除和文件上传。</p>
      <div class="admin-actions">
        <RouterLink class="plain-button" to="/resources">浏览数字资源</RouterLink>
        <RouterLink class="plain-button" to="/sources">查看资料来源</RouterLink>
      </div>
    </el-card>

    <el-card v-else-if="!loggedIn" class="login-card" shadow="never">
      <el-form :model="loginForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="loginForm.username" autocomplete="username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="loginForm.password" type="password" show-password autocomplete="current-password" />
        </el-form-item>
        <el-button type="primary" @click="login">登录</el-button>
      </el-form>
    </el-card>

    <template v-else>
      <div class="admin-toolbar">
        <el-button plain @click="refreshAll">刷新数据</el-button>
        <el-button type="danger" plain @click="logout">退出登录</el-button>
      </div>

      <div class="grid grid-4 stats-row">
        <el-card v-for="item in statCards" :key="item.label" shadow="never">
          <el-statistic :title="item.label" :value="item.value" />
        </el-card>
      </div>

      <el-tabs v-model="active" @tab-change="loadActive">
        <el-tab-pane label="历史资料" name="events">
          <AdminTable :rows="events" :fields="eventFields" title-key="title" @create="saveEvent" @update="saveEvent" @remove="removeEvent" />
        </el-tab-pane>
        <el-tab-pane label="人物资料" name="figures">
          <AdminTable :rows="figures" :fields="figureFields" title-key="name" @create="saveFigure" @update="saveFigure" @remove="removeFigure" />
        </el-tab-pane>
        <el-tab-pane label="数字资源" name="resources">
          <AdminTable :rows="resources" :fields="resourceFields" title-key="name" @create="saveResource" @update="saveResource" @remove="removeResource" />
        </el-tab-pane>
        <el-tab-pane label="风景图片" name="images">
          <el-upload :http-request="uploadImage" :show-file-list="false" class="upload-row">
            <el-button type="success"><el-icon><Upload /></el-icon> 上传图片</el-button>
          </el-upload>
          <AdminTable :rows="images" :fields="imageFields" title-key="name" @create="saveImage" @update="saveImage" @remove="removeImage" />
        </el-tab-pane>
      </el-tabs>
    </template>
  </main>
</template>

<script setup>
import { computed, defineComponent, h, onMounted, reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { Upload } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { http } from '../api/http'

const publicReadOnly = import.meta.env.VITE_PUBLIC_READ_ONLY === 'true'
const loginForm = reactive({ username: '', password: '' })
let savedToken = ''
try { savedToken = localStorage.getItem('admin_token') || '' } catch { savedToken = '' }
const loggedIn = ref(!publicReadOnly && Boolean(savedToken))
const active = ref('events')
const stats = ref({})
const events = ref([])
const figures = ref([])
const resources = ref([])
const images = ref([])

const eventFields = [
  ['title', '标题'], ['event_time', '时间'], ['location', '地点'], ['related_people', '相关人物'],
  ['summary', '简介'], ['details', '详细内容'], ['source', '资料来源'], ['reference_materials', '参考资料'],
  ['image_url', '图片'], ['category', '资料分类'], ['verification_status', '考证状态'], ['verified', '是否已考证']
]
const figureFields = [
  ['name', '姓名'], ['photo_url', '人物照片'], ['active_period', '活动时期'], ['biography', '生平简介'], ['deeds', '主要事迹'],
  ['relation_to_maogongshan', '与毛公山或城阳区关系'], ['related_events', '相关历史事件'], ['source', '资料来源'],
  ['verification_status', '考证状态'], ['verified', '是否已考证']
]
const resourceFields = [
  ['name', '资源名称'], ['type', '资源类型'], ['summary', '简介'], ['source', '来源'], ['file_url', '文件或链接'], ['tags', '标签']
]
const imageFields = [
  ['name', '图片名称'], ['category', '图片分类'], ['description', '简介'], ['location', '拍摄地点'], ['shot_time', '拍摄时间'],
  ['source', '图片来源'], ['image_url', '图片地址'], ['recommendation_index', '推荐指数']
]

const statCards = computed(() => [
  { label: '历史事件', value: stats.value.events || 0 },
  { label: '红色人物', value: stats.value.figures || 0 },
  { label: '文献资料', value: stats.value.documents || 0 },
  { label: '图片数量', value: stats.value.images || 0 },
  { label: '视频数量', value: stats.value.videos || 0 },
  { label: '总访问次数', value: stats.value.visits || 0 }
])

const AdminTable = defineComponent({
  props: ['rows', 'fields', 'titleKey'],
  emits: ['create', 'update', 'remove'],
  setup(props, { emit }) {
    const dialogVisible = ref(false)
    const form = ref({})
    const editingId = ref(null)

    function open(row = null) {
      editingId.value = row?.id || null
      form.value = row ? { ...row } : Object.fromEntries(props.fields.map(([key]) => [key, '']))
      dialogVisible.value = true
    }

    function submit() {
      emit(editingId.value ? 'update' : 'create', { ...form.value, id: editingId.value })
      dialogVisible.value = false
    }

    return () => h('div', [
      h('div', { class: 'admin-actions' }, [h('button', { class: 'plain-button', onClick: () => open() }, '新增')]),
      h('table', { class: 'admin-table' }, [
        h('thead', [h('tr', [h('th', '名称'), h('th', '分类/来源'), h('th', '操作')])]),
        h('tbody', props.rows.map((row) => h('tr', { key: row.id }, [
          h('td', row[props.titleKey]),
          h('td', row.category || row.type || row.source || ''),
          h('td', [
            h('button', { class: 'link-button', onClick: () => open(row) }, '编辑'),
            h('button', { class: 'danger-button', onClick: () => emit('remove', row) }, '删除')
          ])
        ])))
      ]),
      h('div', { class: ['simple-dialog', dialogVisible.value ? 'show' : ''] }, [
        h('div', { class: 'simple-dialog-panel' }, [
          h('h3', editingId.value ? '编辑资料' : '新增资料'),
          ...props.fields.map(([key, label]) => h('label', { class: 'form-line' }, [
            h('span', label),
            h(key.includes('details') || key.includes('summary') || key.includes('biography') || key.includes('deeds') ? 'textarea' : 'input', {
              value: form.value[key],
              onInput: (event) => { form.value[key] = event.target.value }
            })
          ])),
          h('div', { class: 'dialog-actions' }, [
            h('button', { class: 'plain-button', onClick: () => { dialogVisible.value = false } }, '取消'),
            h('button', { class: 'primary-button', onClick: submit }, '保存')
          ])
        ])
      ])
    ])
  }
})

async function login() {
  try {
    const res = await http.post('/api/auth/login', loginForm)
    localStorage.setItem('admin_token', res.data.token)
    loggedIn.value = true
    ElMessage.success('登录成功')
    await refreshAll()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '登录失败，请检查管理员配置')
  }
}

function logout() {
  localStorage.removeItem('admin_token')
  loggedIn.value = false
}

async function refreshAll() {
  const [statsRes, eventRes, figureRes, resourceRes, imageRes] = await Promise.all([
    http.get('/api/stats'),
    http.get('/api/events'),
    http.get('/api/figures'),
    http.get('/api/resources'),
    http.get('/api/scenic-images')
  ])
  stats.value = statsRes.data
  events.value = eventRes.data.items || eventRes.data
  figures.value = figureRes.data.items || figureRes.data
  resources.value = resourceRes.data.items || resourceRes.data
  images.value = imageRes.data
}

function loadActive() {
  refreshAll()
}

async function saveEvent(row) {
  row.verified = Number(row.verified || 0)
  row.id ? await http.put(`/api/admin/events/${row.id}`, row) : await http.post('/api/admin/events', row)
  await refreshAll()
}

async function saveFigure(row) {
  row.verified = Number(row.verified || 0)
  row.id ? await http.put(`/api/admin/figures/${row.id}`, row) : await http.post('/api/admin/figures', row)
  await refreshAll()
}

async function saveResource(row) {
  row.id ? await http.put(`/api/admin/resources/${row.id}`, row) : await http.post('/api/admin/resources', row)
  await refreshAll()
}

async function saveImage(row) {
  row.recommendation_index = Number(row.recommendation_index || 4)
  row.id ? await http.put(`/api/admin/scenic-images/${row.id}`, row) : await http.post('/api/admin/scenic-images', row)
  await refreshAll()
}

async function removeRow(message, callback) {
  try {
    await ElMessageBox.confirm(message, '确认删除', { type: 'warning' })
    await callback()
    await refreshAll()
  } catch {
    // 用户取消删除时不需要额外提示。
  }
}

function removeEvent(row) { removeRow(`删除历史资料：${row.title}？`, () => http.delete(`/api/admin/events/${row.id}`)) }
function removeFigure(row) { removeRow(`删除人物资料：${row.name}？`, () => http.delete(`/api/admin/figures/${row.id}`)) }
function removeResource(row) { removeRow(`删除资源：${row.name}？`, () => http.delete(`/api/admin/resources/${row.id}`)) }
function removeImage(row) { removeRow(`删除图片：${row.name}？`, () => http.delete(`/api/admin/scenic-images/${row.id}`)) }

async function uploadImage(option) {
  const formData = new FormData()
  formData.append('file', option.file)
  formData.append('category', 'scenic')
  const res = await http.post('/api/admin/upload', formData)
  ElMessage.success(`上传成功：${res.data.url}，可复制到图片地址字段。`)
}

onMounted(() => {
  if (loggedIn.value) refreshAll()
})
</script>

<style scoped>
.login-card,
.stats-row,
.admin-toolbar {
  margin: 18px 0;
}

.admin-toolbar,
.admin-actions,
.upload-row {
  margin: 12px 0;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
}

.admin-table th,
.admin-table td {
  padding: 12px;
  border: 1px solid var(--line);
  text-align: left;
}

.plain-button,
.primary-button,
.link-button,
.danger-button {
  min-height: 32px;
  margin-right: 8px;
  padding: 0 12px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
}

.primary-button {
  color: #fff;
  background: var(--red);
}

.link-button {
  color: var(--red);
}

.danger-button {
  color: #b00020;
}

.simple-dialog {
  position: fixed;
  inset: 0;
  z-index: 90;
  display: none;
  place-items: center;
  padding: 18px;
  background: rgba(0, 0, 0, .35);
}

.simple-dialog.show {
  display: grid;
}

.simple-dialog-panel {
  width: min(760px, 100%);
  max-height: 88vh;
  overflow: auto;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
}

.form-line {
  display: grid;
  gap: 6px;
  margin-bottom: 12px;
}

.form-line input,
.form-line textarea {
  width: 100%;
  min-height: 36px;
  padding: 8px;
  border: 1px solid var(--line);
  border-radius: 6px;
  font: inherit;
}

.form-line textarea {
  min-height: 88px;
}

.dialog-actions {
  text-align: right;
}
</style>
