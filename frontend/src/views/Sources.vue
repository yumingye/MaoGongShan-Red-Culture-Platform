<template>
  <div>
    <PageHero title="资料来源与考证说明" subtitle="记录公开资料来源、检索日期、版权状态和考证状态。" image="/assets/images/culture/maogongshan-red-park-2022.jpg" />
    <main class="page">
      <section class="source-intro panel" aria-labelledby="source-heading">
        <div>
          <span>资料治理</span>
          <h2 id="source-heading">看见内容，也看见依据</h2>
        </div>
        <p>本站将公开网页、团队资料与管理说明分开登记。状态字段表示当前核验进度，不代表平台获得相关单位官方背书；外部页面内容与可用性以来源网站为准。</p>
      </section>

      <el-table :data="sources" class="panel sources-table" stripe>
        <el-table-column prop="title" label="资料标题" min-width="180" />
        <el-table-column prop="source_name" label="来源名称" min-width="160" />
        <el-table-column prop="source_type" label="类型" width="130" />
        <el-table-column prop="retrieved_at" label="检索日期" width="120" />
        <el-table-column prop="verification_status" label="状态" width="120" />
        <el-table-column label="链接" width="110">
          <template #default="{ row }">
            <el-link v-if="row.source_url" :href="row.source_url" target="_blank" rel="noopener noreferrer" type="primary">打开</el-link>
            <span v-else>本地项目资料</span>
          </template>
        </el-table-column>
      </el-table>

      <section class="source-list" aria-label="资料来源列表">
        <article v-for="item in sources" :key="`${item.title}-${item.source_name}`" class="source-card panel">
          <div class="source-card__head">
            <span>{{ item.source_type || '资料' }}</span>
            <strong>{{ item.verification_status || '待核验' }}</strong>
          </div>
          <h3>{{ item.title }}</h3>
          <dl>
            <div><dt>来源</dt><dd>{{ item.source_name || '平台整理' }}</dd></div>
            <div><dt>检索日期</dt><dd>{{ item.retrieved_at || '未标注' }}</dd></div>
          </dl>
          <a v-if="item.source_url" :href="item.source_url" target="_blank" rel="noopener noreferrer">查看原始来源</a>
          <span v-else class="local-label">本地项目资料</span>
        </article>
      </section>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { http } from '../api/http'
import PageHero from '../components/PageHero.vue'
import { offlineSources } from '../data/offlineFallbacks'
const sources = ref(offlineSources)
onMounted(async () => {
  try {
    const rows = (await http.get('/api/sources')).data
    if (Array.isArray(rows) && rows.length) sources.value = rows
  } catch {
    sources.value = offlineSources
  }
})
</script>

<style scoped>
.source-intro {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  gap: 28px;
  align-items: center;
  padding: 26px 30px;
  margin-bottom: 22px;
  border-left: 4px solid var(--gold);
}
.source-intro span { color: var(--gold); font-size: 13px; font-weight: 800; letter-spacing: .12em; }
.source-intro h2 { margin: 6px 0 0; color: var(--red-dark); }
.source-intro p { margin: 0; color: var(--muted); line-height: 1.85; }
.source-list { display: none; }
.source-card { padding: 18px; }
.source-card__head { display: flex; justify-content: space-between; gap: 12px; color: var(--muted); font-size: 13px; }
.source-card__head strong { color: var(--red); }
.source-card h3 { margin: 12px 0; color: var(--red-dark); }
.source-card dl { display: grid; gap: 8px; margin: 0 0 14px; }
.source-card dl div { display: grid; grid-template-columns: 70px 1fr; gap: 8px; }
.source-card dt { color: var(--muted); }
.source-card dd { margin: 0; }
.source-card a { color: var(--red); font-weight: 800; }
.local-label { color: var(--muted); font-size: 13px; }
@media (max-width: 720px) {
  .source-intro { grid-template-columns: 1fr; gap: 10px; padding: 22px; }
  .sources-table { display: none; }
  .source-list { display: grid; gap: 14px; }
}
</style>
