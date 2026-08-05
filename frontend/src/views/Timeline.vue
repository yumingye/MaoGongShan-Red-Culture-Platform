<template>
  <div class="timeline-page">
    <PageHero title="红色历史时间轴" subtitle="阶段筛选、横竖切换、自动播放和节点展开共同构成可交互的历史长卷。" image="/assets/images/party-history/info-overview-timeline.jpg" eyebrow="项目自制时间轴导览图" />
    <main class="page" v-loading="loading">
      <el-alert v-if="error" :title="error" type="error" show-icon class="timeline-alert" />
      <section class="timeline-dashboard panel">
        <div><span>当前阶段</span><strong>{{ activeStage }}</strong></div>
        <div><span>节点数量</span><strong>{{ filtered.length }}</strong></div>
        <div class="timeline-actions">
          <el-segmented v-model="mode" :options="['横向长卷','纵向时间轴']" />
          <el-button type="primary" @click="togglePlay">{{ playing ? '暂停自动播放' : '自动播放历史进程' }}</el-button>
        </div>
      </section>
      <div class="stage-tabs">
        <button v-for="stage in stages" :key="stage" :class="{ active: activeStage === stage }" @click="selectStage(stage)">{{ stage }}</button>
      </div>

      <section v-if="mode === '横向长卷'" class="horizontal-scroll" ref="horizontalEl">
        <div class="history-line"></div>
        <article v-for="(item,index) in filtered" :key="item.key" :class="['timeline-node', { active: activeIndex === index, major: item.featured }]" @click="activeIndex=index">
          <button type="button" :aria-label="`展开${item.title}`"><i></i><span>{{ item.year }}</span></button>
          <SafeImage :src="item.image" :alt="item.cover_caption || item.title" />
          <div><small>{{ item.stage }} · {{ item.cover_media_type }}</small><h2>{{ item.title }}</h2><p>{{ item.summary }}</p><p class="media-caption">{{ item.cover_caption }}</p><p class="node-facts">{{ item.event_time }} · {{ item.location }} · {{ item.related_people }}</p><RouterLink :to="item.url">查看完整资料</RouterLink></div>
        </article>
      </section>

      <section v-else class="vertical-timeline">
        <article v-for="(item,index) in filtered" :key="item.key" :class="['vertical-node', { active: activeIndex === index }]" @mouseenter="activeIndex=index">
          <div class="year"><span>{{ item.year }}</span><i></i></div>
          <SafeImage :src="item.image" :alt="item.cover_caption || item.title" />
          <div><small>{{ item.stage }} · {{ item.cover_media_type }}</small><h2>{{ item.title }}</h2><p>{{ item.summary }}</p><p class="media-caption">{{ item.cover_caption }}</p><p class="node-facts">{{ item.event_time }} · {{ item.location }} · {{ item.related_people }}</p><RouterLink :to="item.url">人物、地点与详细资料 →</RouterLink></div>
        </article>
      </section>

      <section v-if="!loading && !filtered.length" class="panel timeline-fallback"><h2>当前阶段未匹配到节点</h2><p>切换“全部阶段”可继续浏览已收录资料。</p><el-button type="primary" @click="activeStage='全部阶段'">显示全部</el-button></section>
    </main>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { http } from '../api/http'
import PageHero from '../components/PageHero.vue'
import SafeImage from '../components/SafeImage.vue'

const list=ref([]),loading=ref(false),error=ref(''),activeStage=ref('全部阶段'),mode=ref('横向长卷'),activeIndex=ref(0),playing=ref(false),horizontalEl=ref(null)
let timer
const stages=['全部阶段','1919—1921','建党初期','土地革命战争时期','全民族抗日战争时期','解放战争时期','社会主义革命和建设时期','改革开放时期','中国特色社会主义新时代']
function inferStage(item){const text=`${item.event_time||''}${item.sub_category||''}${item.title||''}`;if(/1919|1920|1921/.test(text))return'1919—1921';if(/1922|1923|1924|1925|1926|建党初期/.test(text))return'建党初期';if(/1927|1928|1929|1930|1931|1932|1933|1934|1935|1936|土地革命|长征|井冈山|遵义/.test(text))return'土地革命战争时期';if(/1937|1938|1939|1940|1941|1942|1943|1944|1945|抗日/.test(text))return'全民族抗日战争时期';if(/1946|1947|1948|1949|解放战争|西柏坡/.test(text))return'解放战争时期';if(/195\d|196\d|197[0-7]|社会主义革命和建设/.test(text))return'社会主义革命和建设时期';if(/1978|198\d|199\d|200\d|改革开放/.test(text))return'改革开放时期';return'中国特色社会主义新时代'}
function yearOf(text){const match=String(text||'').match(/(?:19|20)\d{2}/);return match?.[0]||'专题'}
const filtered=computed(()=>activeStage.value==='全部阶段'?list.value:list.value.filter(i=>i.stage===activeStage.value))
function stop(){clearInterval(timer);playing.value=false}
function togglePlay(){if(playing.value){stop();return}playing.value=true;timer=window.setInterval(async()=>{if(!filtered.value.length)return;activeIndex.value=(activeIndex.value+1)%filtered.value.length;await nextTick();const nodes=horizontalEl.value?.querySelectorAll('.timeline-node');nodes?.[activeIndex.value]?.scrollIntoView({behavior:'smooth',block:'nearest',inline:'center'})},2600)}
function selectStage(stage){activeStage.value=stage;activeIndex.value=0;stop()}
onMounted(async()=>{loading.value=true;try{const learning=await http.get('/api/learning-articles',{params:{page:1,page_size:100}});list.value=(learning.data.items||learning.data).map(i=>({...i,key:`learning-${i.id}`,year:yearOf(i.event_time),stage:inferStage(i),url:`/learning/${i.id}`})).sort((a,b)=>String(a.year).localeCompare(String(b.year),'zh-CN'))}catch(err){error.value=err?.response?.data?.detail||'时间轴加载失败，其他专题仍可正常浏览。'}finally{loading.value=false}})
onBeforeUnmount(stop)
</script>

<style scoped>
.timeline-page{background:linear-gradient(180deg,#f7efdf,#fffaf0)}.timeline-alert{margin-bottom:18px}.timeline-dashboard{display:grid;grid-template-columns:180px 150px 1fr;gap:20px;align-items:center;padding:20px}.timeline-dashboard>div{display:grid;gap:6px}.timeline-dashboard span{color:var(--muted)}.timeline-dashboard strong{font-size:24px;color:var(--red-dark)}.timeline-actions{display:flex!important;flex-direction:row;justify-content:flex-end;align-items:center}.stage-tabs{display:flex;gap:8px;overflow-x:auto;padding:26px 0}.stage-tabs button{flex:0 0 auto;padding:10px 15px;border:1px solid var(--line);border-radius:999px;background:#fffaf0;cursor:pointer}.stage-tabs button.active{color:#fff;background:var(--red);border-color:var(--red)}
.horizontal-scroll{position:relative;display:flex;gap:22px;overflow-x:auto;scroll-snap-type:x mandatory;padding:54px 30px 35px;background:#2c0a0d;border-radius:14px}.history-line{position:absolute;top:37px;left:30px;right:30px;height:3px;background:linear-gradient(90deg,var(--gold),var(--red),var(--gold))}.timeline-node{position:relative;flex:0 0 min(390px,82vw);scroll-snap-align:center;overflow:hidden;color:#fff8e6;background:#4c1116;border:1px solid rgba(243,216,145,.28);border-radius:12px;transition:.35s}.timeline-node.active{transform:translateY(-10px);box-shadow:0 22px 50px rgba(0,0,0,.35);border-color:var(--gold)}.timeline-node>button{position:absolute;z-index:3;top:-40px;left:20px;color:#fff;background:none;border:0}.timeline-node>button i{display:block;width:17px;height:17px;margin:auto;background:var(--gold);border:4px solid #fff;border-radius:50%;box-shadow:0 0 0 0 rgba(243,216,145,.6);animation:pulse 1.8s infinite}.timeline-node>button span{display:block;margin-top:5px}.timeline-node :deep(.safe-image){height:220px}.timeline-node>div{padding:20px}.timeline-node small{color:var(--gold-soft)}.timeline-node h2{font-size:25px}.timeline-node p{line-height:1.8;color:#eadfd6}.timeline-node a{color:var(--gold-soft);font-weight:800}
.vertical-timeline{position:relative;max-width:1000px;margin:auto}.vertical-timeline:before{position:absolute;top:0;bottom:0;left:112px;width:3px;background:linear-gradient(var(--gold),var(--red),var(--gold));content:''}.vertical-node{position:relative;display:grid;grid-template-columns:90px 220px 1fr;gap:34px;align-items:center;padding:28px 0;opacity:.78;transition:.3s}.vertical-node.active{opacity:1;transform:translateX(8px)}.vertical-node .year{text-align:right;color:var(--red-dark);font-weight:900}.vertical-node .year i{position:absolute;left:104px;width:19px;height:19px;background:var(--gold);border:5px solid #fff;border-radius:50%}.vertical-node :deep(.safe-image){height:150px;border-radius:10px}.vertical-node h2{color:var(--red-dark)}.vertical-node p{line-height:1.8;color:var(--muted)}.vertical-node a{color:var(--red);font-weight:800}.timeline-fallback{padding:32px;text-align:center}
.media-caption{font-size:13px!important;line-height:1.65!important}.node-facts{font-size:13px!important;color:var(--gold-soft)!important}.vertical-node .node-facts{color:var(--gold)!important}
@keyframes pulse{70%{box-shadow:0 0 0 14px transparent}}@media(max-width:760px){.timeline-dashboard{grid-template-columns:1fr 1fr}.timeline-actions{grid-column:1/-1;justify-content:flex-start;flex-wrap:wrap}.vertical-timeline:before{left:18px}.vertical-node{grid-template-columns:45px 1fr;gap:14px;padding-left:0}.vertical-node .year{font-size:12px}.vertical-node .year i{left:10px}.vertical-node :deep(.safe-image){grid-column:2;height:190px}.vertical-node>div:last-child{grid-column:2}.horizontal-scroll{padding-left:18px;padding-right:18px}}@media(prefers-reduced-motion:reduce){.timeline-node>button i{animation:none}.timeline-node.active,.vertical-node.active{transform:none}}
</style>
