<template>
  <div>
    <PageHero
      title="项目成果展示"
      subtitle="集中呈现数字平台、调研资料、来源台账、质量检查和部署文档等可核验成果。"
      image="/assets/images/activity/xifu-grape-harvest.jpg"
    />
    <main class="page">
      <section v-if="featured" class="featured-result panel reveal">
        <div class="featured-mark">
          <el-icon><Monitor /></el-icon>
          <span>核心数字成果</span>
        </div>
        <div>
          <el-tag type="warning">{{ featured.status }}</el-tag>
          <h2>{{ featured.title }}</h2>
          <p>{{ featured.summary }}</p>
          <div class="featured-actions">
            <el-button type="primary" @click="$router.push('/overview')">查看平台内容</el-button>
            <el-button plain @click="$router.push('/sources')">查看资料依据</el-button>
          </div>
        </div>
      </section>

      <section class="result-ledger" aria-labelledby="ledger-title">
        <div class="ledger-heading">
          <span>DELIVERABLE LEDGER</span>
          <h2 id="ledger-title">阶段成果台账</h2>
          <p>列出已经形成并可在平台内核验的成果，不使用没有依据的数量和传播成效。</p>
        </div>
        <div class="ledger-list">
          <article v-for="(item, index) in remainingResults" :key="item.id" class="ledger-item reveal">
            <span class="ledger-index">{{ String(index + 2).padStart(2, '0') }}</span>
            <div class="resource-icon"><el-icon><Document /></el-icon></div>
            <div class="ledger-copy">
              <span>{{ item.status }}</span>
              <h3>{{ item.title }}</h3>
              <p>{{ item.summary }}</p>
            </div>
            <div class="ledger-source">
              <span>依据</span>
              <strong>{{ item.source_title }}</strong>
              <small>{{ item.verification_status }}</small>
            </div>
          </article>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { Document, Monitor } from '@element-plus/icons-vue'
import { computed, onMounted, ref } from 'vue'
import { http } from '../api/http'
import PageHero from '../components/PageHero.vue'
import { offlineProject } from '../data/offlineFallbacks'

const results = ref(offlineProject.results)
const featured = computed(() => results.value[0] || null)
const remainingResults = computed(() => results.value.slice(1))

onMounted(async () => {
  try {
    const rows = (await http.get('/api/project')).data?.results
    if (Array.isArray(rows) && rows.length) results.value = rows
  } catch {
    results.value = offlineProject.results
  }
})
</script>

<style scoped>
.featured-result {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  gap: clamp(24px, 5vw, 64px);
  align-items: center;
  padding: clamp(28px, 5vw, 58px);
  margin-bottom: 54px;
  background: linear-gradient(110deg, #fffaf0 0 62%, #edf5f4);
  border-top: 4px solid var(--red);
}
.featured-mark { display: grid; place-items: center; gap: 12px; min-height: 210px; color: #fff8e6; background: #711b20; }
.featured-mark .el-icon { font-size: 70px; }
.featured-mark span { font-weight: 800; letter-spacing: .14em; }
.featured-result h2 { margin: 14px 0; color: var(--red-dark); font-size: clamp(28px, 4vw, 44px); }
.featured-result p { color: var(--muted); line-height: 1.9; }
.featured-actions { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 22px; }
.result-ledger { display: grid; grid-template-columns: 280px minmax(0, 1fr); gap: 34px; }
.ledger-heading { position: sticky; top: 100px; align-self: start; }
.ledger-heading > span { color: var(--gold); font-size: 12px; font-weight: 900; letter-spacing: .14em; }
.ledger-heading h2 { margin: 8px 0; color: var(--red-dark); font-size: 32px; }
.ledger-heading p { color: var(--muted); line-height: 1.8; }
.ledger-list { display: grid; border-top: 1px solid var(--line); }
.ledger-item { display: grid; grid-template-columns: 44px 48px minmax(0, 1fr) 170px; gap: 16px; align-items: center; padding: 24px 0; border-bottom: 1px solid var(--line); }
.ledger-index { color: #a88654; font-family: Georgia, serif; font-weight: 800; }
.resource-icon { display: grid; place-items: center; width: 44px; height: 44px; color: var(--red); background: rgba(143, 29, 34, .08); border-radius: 50%; }
.ledger-copy > span { color: var(--gold); font-size: 12px; font-weight: 800; }
.ledger-copy h3 { margin: 4px 0 6px; color: var(--red-dark); }
.ledger-copy p { margin: 0; color: var(--muted); line-height: 1.75; }
.ledger-source { display: grid; gap: 4px; color: var(--muted); font-size: 12px; }
.ledger-source strong { color: #4f3a35; line-height: 1.5; }
@media (max-width: 900px) {
  .featured-result, .result-ledger { grid-template-columns: 1fr; }
  .featured-mark { min-height: 150px; }
  .ledger-heading { position: static; }
}
@media (max-width: 620px) {
  .ledger-item { grid-template-columns: 34px 42px minmax(0, 1fr); align-items: start; }
  .ledger-source { grid-column: 3; padding-top: 6px; }
  .featured-actions { display: grid; }
  .featured-actions :deep(.el-button) { width: 100%; margin-left: 0; }
}
</style>
