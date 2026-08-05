<template>
  <div v-if="stage">
    <PageHero :title="stage.title" :subtitle="stage.summary" :image="stage.cover" :eyebrow="`${stage.period} · ${stage.scope}`" />
    <main class="page stage-page">
      <nav class="breadcrumb" aria-label="面包屑"><RouterLink to="/">首页</RouterLink><span>/</span><RouterLink to="/party-history">党史学习</RouterLink><span>/</span><b>{{ stage.title }}</b></nav>
      <el-alert title="内容边界" description="本页属于全国党史学习专题，不作为毛公山地方历史叙述；时间划分与基本结论依据权威公开党史资料整理。" type="warning" :closable="false" show-icon />
      <section class="stage-lead panel reveal">
        <div><span>{{ stage.period }}</span><h1>{{ stage.title }}</h1><p>{{ stage.summary }}</p><div class="tag-row"><em v-for="tag in stage.tags" :key="tag">{{ tag }}</em></div></div>
        <figure class="stage-media">
          <SafeImage :src="stage.cover" :alt="stage.coverNote" loading="eager" show-status />
          <figcaption><el-tag effect="dark">{{ stage.coverType }}</el-tag><p>{{ stage.coverNote }}</p></figcaption>
        </figure>
      </section>
      <section class="stage-timeline reveal" aria-label="阶段节点">
        <article v-for="(item,index) in stage.milestones" :key="item" class="panel"><i>{{ index+1 }}</i><p>{{ item }}</p></article>
      </section>
      <section class="article-layout">
        <aside class="panel stage-nav"><strong>本页目录</strong><a v-for="(section,index) in stage.sections" :key="section.title" :href="`#stage-${index}`">{{ section.title }}</a></aside>
        <article class="stage-article panel">
          <section v-for="(section,index) in stage.sections" :id="`stage-${index}`" :key="section.title" class="reveal"><h2>{{ section.title }}</h2><p>{{ section.content }}</p></section>
          <div class="source-box"><strong>参考来源</strong><p>{{ stage.source }}</p><a :href="stage.sourceUrl" target="_blank" rel="noopener noreferrer">查看公开来源</a></div>
        </article>
      </section>
      <section class="stage-switcher panel">
        <RouterLink :to="previous ? `/party-history/stage/${previous.slug}` : '/party-history'">← {{ previous?.title || '返回党史学习' }}</RouterLink>
        <RouterLink :to="next ? `/party-history/stage/${next.slug}` : '/timeline'">{{ next?.title || '进入历史时间轴' }} →</RouterLink>
      </section>
    </main>
  </div>
  <NotFound v-else />
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import PageHero from '../components/PageHero.vue'
import SafeImage from '../components/SafeImage.vue'
import NotFound from './NotFound.vue'
import { getHistoryStage, historyStages } from '../data/historyStages'
const route = useRoute()
const stage = computed(() => getHistoryStage(route.params.slug))
const index = computed(() => historyStages.findIndex((item) => item.slug === route.params.slug))
const previous = computed(() => index.value > 0 ? historyStages[index.value - 1] : null)
const next = computed(() => index.value >= 0 && index.value < historyStages.length - 1 ? historyStages[index.value + 1] : null)
</script>

<style scoped>
.breadcrumb{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:20px;color:var(--muted)}.breadcrumb a{color:var(--red)}.stage-lead{display:grid;grid-template-columns:minmax(0,1fr) minmax(320px,.8fr);margin:24px 0 38px;overflow:hidden}.stage-lead>div{padding:clamp(26px,5vw,54px)}.stage-lead>div>span{color:var(--gold);font-weight:800}.stage-lead h1{margin:10px 0;color:var(--red-dark);font-size:clamp(30px,4vw,48px)}.stage-lead p,.stage-article p{line-height:2;color:#4f4943}.stage-lead :deep(.safe-image){min-height:400px}.tag-row em{padding:5px 9px;color:var(--red-dark);background:#f4e4bb;border-radius:999px;font-style:normal}.stage-timeline{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:34px}.stage-timeline article{position:relative;padding:22px 18px 16px;border-top:4px solid var(--red)}.stage-timeline i{display:grid;place-items:center;width:28px;height:28px;color:#fff;background:var(--red);border-radius:50%;font-style:normal}.article-layout{display:grid;grid-template-columns:220px minmax(0,1fr);gap:22px}.stage-nav{position:sticky;top:100px;align-self:start;display:grid;gap:10px;padding:20px}.stage-nav a{padding:8px 0;border-bottom:1px solid var(--line)}.stage-article{padding:clamp(24px,5vw,56px)}.stage-article section{scroll-margin-top:100px;padding-bottom:22px}.stage-article h2{color:var(--red-dark);font-size:28px}.source-box{margin-top:28px;padding:20px;background:#fff4d7;border-left:4px solid var(--gold)}.source-box a{color:var(--red);font-weight:800}.stage-switcher{display:flex;justify-content:space-between;gap:20px;margin-top:28px;padding:20px;color:var(--red);font-weight:800}@media(max-width:800px){.stage-lead,.article-layout{grid-template-columns:1fr}.stage-lead :deep(.safe-image){min-height:260px}.stage-timeline{grid-template-columns:1fr}.stage-nav{position:static}.stage-switcher{align-items:stretch;flex-direction:column}}
.stage-media{display:grid;margin:0;background:#fff4d7}.stage-media :deep(.safe-image){min-height:400px}.stage-media figcaption{padding:12px 16px}.stage-media figcaption p{margin:8px 0 0;font-size:13px;line-height:1.7}@media(max-width:800px){.stage-media :deep(.safe-image){min-height:260px}}
</style>
