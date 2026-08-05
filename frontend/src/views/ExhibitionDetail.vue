<template>
  <div v-if="item" class="exhibition-detail">
    <MotionStory :title="item.title" :frames="item.gallery" :captions="[item.summary,item.focus,item.practice]" />
    <main class="page">
      <el-breadcrumb separator="/"><el-breadcrumb-item to="/">首页</el-breadcrumb-item><el-breadcrumb-item to="/exhibitions">红色数字专区</el-breadcrumb-item><el-breadcrumb-item>{{ item.title }}</el-breadcrumb-item></el-breadcrumb>
      <section class="detail-nav panel"><a v-for="(section,index) in item.sections" :key="section.title" :href="`#section-${index}`">{{ String(index+1).padStart(2,'0') }} {{ section.title }}</a></section>
      <section v-if="item.slug === 'photo-compare'" class="compare-lab reveal">
        <PhotoCompare :before="item.gallery[0]" :after="item.gallery[1]" before-label="红色文化场景资料图" after-label="青岛山地环境资料图" />
        <p>两张图片来自不同地点，仅用于练习影像证据对照，不表示同一地点的历史今昔变化。</p>
      </section>
      <section v-if="sourcedImage" class="sourced-image panel reveal">
        <SafeImage :src="sourcedImage.path" :alt="sourcedImage.alt" kind="culture" />
        <div>
          <span>来源明确的专题配图</span>
          <h2>{{ sourcedImage.title }}</h2>
          <p>{{ sourcedImage.description }}</p>
          <small>作者：{{ sourcedImage.author }} · {{ sourcedImage.license }} · {{ sourcedImage.processing }}</small>
          <a :href="sourcedImage.sourceUrl" target="_blank" rel="noopener noreferrer">查看原始文件与许可</a>
        </div>
      </section>
      <section class="detail-grid">
        <article>
          <header class="article-lead reveal"><span>{{ item.category }}</span><h1>{{ item.title }}</h1><p>{{ item.summary }}</p></header>
          <section v-for="(section,index) in item.sections" :id="`section-${index}`" :key="section.title" class="chapter reveal">
            <b>{{ String(index+1).padStart(2,'0') }}</b><div><h2>{{ section.title }}</h2><p>{{ section.content }}</p><blockquote v-if="index===1">可靠的数字文化表达，首先要让资料来源和解释边界清晰可见。</blockquote></div>
          </section>
          <section class="knowledge-deck"><button v-for="word in item.keywords" :key="word" @click="flipped=word" :class="{flipped:flipped===word}"><span>{{ word }}</span><strong>{{ flipped===word?'点击继续探索':'翻开知识卡' }}</strong></button></section>
          <div class="source-box"><strong>资料说明</strong><p>{{ item.source }}。动态展示为平台信息设计，不作为历史影像证据。</p><RouterLink :to="item.sourceUrl">查看资料来源说明</RouterLink></div>
          <nav class="prev-next"><RouterLink v-if="previous" :to="`/exhibitions/${previous.slug}`">上一篇<br><strong>{{ previous.title }}</strong></RouterLink><RouterLink v-if="next" :to="`/exhibitions/${next.slug}`">下一篇<br><strong>{{ next.title }}</strong></RouterLink></nav>
        </article>
        <aside class="panel"><h3>继续学习</h3><RouterLink to="/timeline">动态历史时间轴</RouterLink><RouterLink to="/videos">红色影像馆</RouterLink><RouterLink to="/learning-challenge">知识闯关</RouterLink><RouterLink to="/chat">资源库问答</RouterLink></aside>
      </section>
    </main>
  </div>
  <NotFound v-else />
</template>
<script setup>
import { computed, ref } from 'vue';import { RouterLink,useRoute } from 'vue-router';import MotionStory from '../components/MotionStory.vue';import PhotoCompare from '../components/PhotoCompare.vue';import SafeImage from '../components/SafeImage.vue';import NotFound from './NotFound.vue';import { exhibitions,getExhibition } from '../data/experienceContent';import { supplementalImages } from '../data/supplementalImages'
const props=defineProps({fixedSlug:{type:String,default:''}});const route=useRoute();const flipped=ref('');const item=computed(()=>getExhibition(props.fixedSlug||route.params.slug));const index=computed(()=>exhibitions.findIndex(i=>i.slug===item.value?.slug));const previous=computed(()=>index.value>0?exhibitions[index.value-1]:null);const next=computed(()=>index.value>=0&&index.value<exhibitions.length-1?exhibitions[index.value+1]:null)
const sourcedImage=computed(()=>item.value?.slug==='qingdao-red'?supplementalImages.qingdaoMayFourth:item.value?.slug==='sdu-practice'?supplementalImages.sduQingdaoCampus:null)
</script>
<style scoped>
.exhibition-detail>.motion-story{border-radius:0;min-height:min(68vh,660px)}.detail-nav{display:flex;gap:10px;overflow-x:auto;margin:24px 0;padding:14px}.detail-nav a{flex:0 0 auto;padding:8px 12px;color:var(--red-dark);border-radius:8px}.detail-grid{display:grid;grid-template-columns:minmax(0,1fr) 270px;gap:28px}.article-lead{padding:20px 0 34px}.article-lead span{color:var(--gold);font-weight:800}.article-lead h1{font-size:clamp(34px,5vw,62px);color:var(--red-dark)}.article-lead p{font-size:20px;line-height:1.9;color:var(--muted)}.chapter{display:grid;grid-template-columns:60px 1fr;gap:20px;padding:32px 0;border-top:1px solid var(--line)}.chapter>b{font-size:30px;color:var(--gold)}.chapter h2{margin-top:0;color:var(--red-dark);font-size:28px}.chapter p{font-size:17px;line-height:2}.chapter blockquote{margin:22px 0 0;padding:20px;color:var(--red-dark);background:#fff2d5;border-left:4px solid var(--gold)}.detail-grid>aside{position:sticky;top:96px;align-self:start;display:grid;gap:8px;padding:20px}.detail-grid>aside h3{color:var(--red-dark)}.detail-grid>aside a{padding:10px;border-bottom:1px solid var(--line)}.knowledge-deck{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:30px 0}.knowledge-deck button{min-height:150px;padding:18px;border:1px solid var(--gold);border-radius:12px;background:var(--red-dark);color:#fff8e6;cursor:pointer;transform-style:preserve-3d;transition:transform .5s}.knowledge-deck button.flipped{transform:rotateY(180deg);background:#fff3d7;color:var(--red-dark)}.knowledge-deck span,.knowledge-deck strong{display:block;margin:8px}.source-box{padding:22px;background:#fff8e7;border:1px solid var(--line);border-radius:12px}.source-box a{color:var(--red);font-weight:800}.prev-next{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:24px}.prev-next a{padding:16px;background:#fffaf0;border:1px solid var(--line);border-radius:10px;color:var(--red-dark)}
.compare-lab{margin:30px 0}.compare-lab>p{padding:12px 16px;color:#6b3f13;background:#fff4d7;border-radius:8px}
.sourced-image{display:grid;grid-template-columns:minmax(280px,.9fr) minmax(0,1.1fr);gap:24px;padding:20px;margin:30px 0}.sourced-image :deep(.safe-image){min-height:320px;border-radius:8px}.sourced-image>div{display:grid;align-content:center;gap:10px}.sourced-image span{color:var(--gold);font-weight:800}.sourced-image h2{margin:0;color:var(--red-dark)}.sourced-image p{color:var(--muted);line-height:1.85}.sourced-image a{color:var(--red);font-weight:800}.sourced-image small{color:#675c54}
@media(max-width:850px){.detail-grid,.sourced-image{grid-template-columns:1fr}.detail-grid>aside{position:static}.knowledge-deck{grid-template-columns:1fr}.chapter{grid-template-columns:42px 1fr}.prev-next{grid-template-columns:1fr}}
</style>
