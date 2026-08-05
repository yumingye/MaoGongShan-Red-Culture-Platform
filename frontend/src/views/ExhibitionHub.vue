<template>
  <div class="exhibition-hub">
    <MotionStory title="红色文化数字专区" :frames="heroFrames" :captions="heroCaptions" />
    <main class="page">
      <section class="marquee" aria-label="专题关键词"><div>党史学习 · 红色人物 · 精神谱系 · 山东记忆 · 青岛文化 · 青年实践 · 数字技术 · 资料考证 ·</div></section>
      <section class="hub-intro reveal">
        <div><p class="eyebrow">DIGITAL EXHIBITION</p><h1>专题不是入口装饰，而是一条完整学习路径</h1><p>每个专题均拥有独立地址、分章节正文、动态图文、知识卡片、关联入口与来源边界。</p></div>
        <div class="orbit" aria-hidden="true"><i></i><b>15</b><span>独立专题</span></div>
      </section>
      <div class="category-tabs"><button v-for="item in categories" :key="item" :class="{active:activeCategory===item}" @click="activeCategory=item">{{ item }}</button></div>
      <section class="exhibition-grid">
        <RouterLink v-for="(item,index) in filtered" :key="item.slug" :to="`/exhibitions/${item.slug}`" class="exhibition-card reveal" :class="`tone-${index%4}`">
          <SafeImage :src="item.image" :alt="item.title" />
          <div><span>{{ item.category }}</span><h2>{{ item.title }}</h2><p>{{ item.summary }}</p><strong>进入动态专题 →</strong></div>
        </RouterLink>
      </section>
      <section class="quick-actions panel reveal"><div><h2>把阅读变成行动</h2><p>观看动态图文微课、完成知识闯关，系统会在本机保存进度与错题。</p></div><RouterLink to="/videos">进入红色影像馆</RouterLink><RouterLink to="/learning-challenge">开始知识闯关</RouterLink></section>
    </main>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import MotionStory from '../components/MotionStory.vue'
import SafeImage from '../components/SafeImage.vue'
import { exhibitions } from '../data/experienceContent'
const activeCategory=ref('全部')
const categories=computed(()=>['全部',...new Set(exhibitions.map(i=>i.category))])
const filtered=computed(()=>activeCategory.value==='全部'?exhibitions:exhibitions.filter(i=>i.category===activeCategory.value))
const heroFrames=exhibitions.slice(0,3).map(i=>i.image)
const heroCaptions=['沿历史脉络理解红色文化，而不是孤立背诵结论。','让人物、事件、地点和精神在数字空间中相互连接。','用可追溯资料和软件工程守护文化记忆。']
</script>

<style scoped>
.exhibition-hub{background:linear-gradient(180deg,#24080a 0 620px,var(--paper) 620px)}.exhibition-hub>.motion-story{border-radius:0;min-height:min(76vh,720px)}
.marquee{overflow:hidden;margin:0 0 48px;padding:12px 0;color:#fff3cf;background:var(--red-dark);font-weight:800}.marquee div{width:max-content;animation:marquee 22s linear infinite}
.hub-intro{display:grid;grid-template-columns:minmax(0,1fr) 190px;gap:40px;align-items:center;margin-bottom:38px}.hub-intro h1{max-width:760px;color:var(--red-dark);font-size:clamp(30px,5vw,54px)}.hub-intro p{line-height:1.9;color:var(--muted)}
.orbit{position:relative;display:grid;place-content:center;justify-items:center;width:170px;aspect-ratio:1;border:1px solid var(--gold);border-radius:50%}.orbit i{position:absolute;inset:-10px;border:2px dashed rgba(143,29,34,.35);border-radius:50%;animation:spin 12s linear infinite}.orbit b{font-size:48px;color:var(--red)}.orbit span{color:var(--muted)}
.category-tabs{display:flex;gap:8px;overflow-x:auto;margin-bottom:26px;padding-bottom:6px}.category-tabs button{flex:0 0 auto;padding:10px 16px;border:1px solid var(--line);border-radius:999px;background:#fffaf0;color:var(--red-dark);cursor:pointer}.category-tabs button.active{color:#fff;background:var(--red)}
.exhibition-grid{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:20px}.exhibition-card{position:relative;grid-column:span 4;min-height:430px;overflow:hidden;border-radius:14px}.exhibition-card:nth-child(5n+1),.exhibition-card:nth-child(5n+5){grid-column:span 8}.exhibition-card :deep(.safe-image){position:absolute;inset:0;width:100%;height:100%;transition:transform .7s ease}.exhibition-card:hover :deep(.safe-image){transform:scale(1.07)}.exhibition-card>div{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:flex-end;padding:28px;color:#fff8e6;background:linear-gradient(180deg,transparent 22%,rgba(31,5,8,.94))}.exhibition-card h2{font-size:clamp(25px,3vw,38px);margin:8px 0}.exhibition-card p{line-height:1.75}.exhibition-card strong{color:var(--gold-soft)}
.quick-actions{display:flex;align-items:center;gap:14px;margin-top:40px;padding:26px}.quick-actions div{flex:1}.quick-actions h2{color:var(--red-dark)}.quick-actions p{color:var(--muted)}.quick-actions>a{padding:12px 16px;color:#fff;background:var(--red);border-radius:8px}
@keyframes marquee{to{transform:translateX(-50%)}}@keyframes spin{to{transform:rotate(360deg)}}
@media(max-width:800px){.hub-intro{grid-template-columns:1fr}.orbit{display:none}.exhibition-grid{display:grid;grid-template-columns:1fr}.exhibition-card,.exhibition-card:nth-child(n){grid-column:auto;min-height:390px}.quick-actions{align-items:stretch;flex-direction:column}.exhibition-hub>.motion-story{min-height:560px}}
@media(prefers-reduced-motion:reduce){.marquee div,.orbit i{animation:none}}
</style>
