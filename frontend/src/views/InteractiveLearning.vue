<template>
  <div>
    <PageHero title="红色知识互动学习" subtitle="通过即时解析、事件排序、精神配对、错题回顾与本地学习报告，把浏览转化为可持续的学习过程。" image="/assets/images/commons/shandong-university-charter-1901-jpg.jpg" eyebrow="INTERACTIVE LEARNING" />
    <main class="page">
      <section class="progress-board panel">
        <div><span>学习积分</span><strong>{{ score }}</strong></div>
        <div><span>已完成</span><strong>{{ completed }}</strong></div>
        <div><span>正确率</span><strong>{{ accuracy }}%</strong></div>
        <el-progress :percentage="overallProgress" :stroke-width="12" color="#8f1d22" />
      </section>

      <el-tabs v-model="mode" class="learning-tabs" stretch>
        <el-tab-pane label="知识闯关" name="quiz">
          <section v-if="current" class="quiz-stage">
            <div class="question-card panel">
              <span>第 {{ cursor + 1 }} 题 · {{ current.category }}</span>
              <h1>{{ current.question }}</h1>
              <button v-for="(option,index) in current.options" :key="option" :disabled="answered" :class="optionClass(index)" @click="answer(index)"><b>{{ String.fromCharCode(65+index) }}</b>{{ option }}</button>
              <Transition name="answer"><div v-if="answered" class="explanation"><strong>{{ selected===current.answer?'回答正确':'再想一步' }}</strong><p>{{ current.explanation }}</p><RouterLink :to="current.link">阅读相关专题</RouterLink></div></Transition>
              <el-button v-if="answered" type="primary" @click="nextQuestion">{{ cursor===questions.length-1?'查看学习报告':'下一题' }}</el-button>
            </div>
            <aside class="panel tool-box"><h3>学习工具</h3><button @click="randomFact">随机知识</button><button @click="showMistakes=!showMistakes">错题回顾（{{ mistakes.length }}）</button><button @click="resetQuiz">重新闯关</button><p v-if="fact">{{ fact }}</p></aside>
          </section>
          <section v-else class="report panel"><h1>本次学习报告</h1><p>你完成了 {{ quizAnswers.length }} 道题，知识闯关获得 {{ quizCorrect*10 }} 分，正确率 {{ quizAccuracy }}%。学习记录只保存在当前浏览器。</p><div class="report-bars"><i :style="{width:`${quizAccuracy}%`}"></i></div><RouterLink to="/exhibitions">继续专题学习</RouterLink><button @click="resetQuiz">重新挑战</button></section>
          <section v-if="showMistakes" class="mistakes panel"><h2>错题回顾</h2><article v-for="item in mistakes" :key="item.id"><strong>{{ item.question }}</strong><p>{{ item.explanation }}</p></article><p v-if="!mistakes.length">本轮还没有错题，继续保持严谨阅读。</p></section>
        </el-tab-pane>

        <el-tab-pane label="事件排序" name="sorting">
          <section class="challenge panel"><span>按时间先后排序</span><h2>点击下方事件，将它们依次放入时间轴</h2><p>不要求死记细节，重点是理解事件之间的历史联系。</p>
            <div class="choice-bank"><button v-for="item in remainingEvents" :key="item.id" @click="chooseEvent(item)">{{ item.title }}</button></div>
            <ol class="ordered-list"><li v-for="item in orderedEvents" :key="item.id"><b>{{ item.year }}</b><span>{{ item.title }}</span><button aria-label="移除此事件" @click="removeEvent(item)">×</button></li></ol>
            <div class="challenge-actions"><el-button type="primary" :disabled="orderedEvents.length!==eventOrder.length" @click="checkOrder">提交排序</el-button><el-button @click="resetOrder">重置</el-button></div>
            <el-alert v-if="orderResult" :title="orderResult" :type="orderCorrect?'success':'warning'" show-icon :closable="false" />
          </section>
        </el-tab-pane>

        <el-tab-pane label="精神配对" name="matching">
          <section class="challenge panel"><span>精神谱系关键词配对</span><h2>{{ activeMatch?.description || '本轮配对已经完成' }}</h2><p>选择与描述最匹配的精神专题，完成后可进入独立详情页继续学习。</p>
            <div v-if="activeMatch" class="match-options"><button v-for="option in activeMatch.options" :key="option" :disabled="matchAnswered" :class="{correct:matchAnswered&&option===activeMatch.answer,wrong:matchAnswered&&option===matchChoice&&option!==activeMatch.answer}" @click="answerMatch(option)">{{ option }}</button></div>
            <div v-if="matchAnswered" class="explanation"><strong>{{ matchChoice===activeMatch.answer?'配对正确':'正确答案：'+activeMatch.answer }}</strong><p>{{ activeMatch.explanation }}</p><el-button type="primary" @click="nextMatch">下一组</el-button></div>
            <div v-else-if="!activeMatch" class="report"><h2>精神配对完成</h2><p>你完成了 {{ matches.length }} 组配对，获得 {{ matchCorrect*8 }} 分。</p><button @click="resetMatches">重新配对</button></div>
          </section>
        </el-tab-pane>
      </el-tabs>
    </main>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import PageHero from '../components/PageHero.vue'
import { readStorage, removeStorage, writeStorage } from '../utils/storage'

const questions = [
  {id:1,category:'党史',question:'中共一大最后阶段转移到哪里继续举行？',options:['浙江嘉兴南湖','江西井冈山','陕西延安','河北西柏坡'],answer:0,explanation:'中共一大会议最后阶段转移至浙江嘉兴南湖游船上继续举行。',link:'/party-history/stage/party-founding'},
  {id:2,category:'精神谱系',question:'“实事求是闯新路、艰苦奋斗攻难关”与哪一精神密切相关？',options:['井冈山精神','抗疫精神','工匠精神','探月精神'],answer:0,explanation:'井冈山精神强调坚定执着追理想、实事求是闯新路、艰苦奋斗攻难关和依靠群众求胜利。',link:'/spirits'},
  {id:3,category:'资料考证',question:'专题页中的红色文化主题配图可以直接作为事件现场证据吗？',options:['可以','不可以，应核对来源与说明','只要清晰就可以','无需记录来源'],answer:1,explanation:'主题配图用于辅助阅读，不等于历史现场照片，必须查看来源、时间和版权说明。',link:'/sources'},
  {id:4,category:'毛公山',question:'平台如何处理毛公山名称由来的不同说法？',options:['全部写成史实','选择最传奇的说法','保留来源并标明考证边界','删除所有介绍'],answer:2,explanation:'平台区分公开资料、文化叙事和待核验内容，不把网络传说直接写成确定史实。',link:'/overview'},
{id:5,category:'青年实践',question:'数字文化调研首先应当重视什么？',options:['特效数量','资料来源、授权与版权','页面颜色','宣传口号'],answer:1,explanation:'可靠资料、规范授权和版权登记是数字化传播的基础。',link:'/school'},
  {id:6,category:'技术',question:'未配置大模型 API 时，平台问答采用什么方式？',options:['随机回答','本地知识库检索','页面白屏','停止服务'],answer:1,explanation:'平台自动降级为本地检索式问答，并显示引用来源。',link:'/chat'},
  {id:7,category:'地图',question:'未配置高德地图 Key 时页面如何工作？',options:['整页报错','显示本地静态导览和点位列表','删除点位','跳转外站'],answer:1,explanation:'地图模块具备无 Key 降级方案，核心点位和文字导览仍可使用。',link:'/map'},
  {id:8,category:'历史',question:'学习遵义会议时，哪种方法更可靠？',options:['只背日期','理解危急背景、问题与纠错过程','忽略前因后果','使用传说替代史料'],answer:1,explanation:'重要会议应放回具体历史条件，理解其解决的问题和形成的影响。',link:'/red-events'}
]
const eventOrder = [{id:'a',year:1921,title:'中国共产党成立'},{id:'b',year:1927,title:'南昌起义'},{id:'c',year:1935,title:'遵义会议'},{id:'d',year:1949,title:'中华人民共和国成立'},{id:'e',year:1978,title:'改革开放新时期开启'}]
const matches = [
  {description:'自主创新、开放融合、万众一心、追求卓越',answer:'新时代北斗精神',options:['新时代北斗精神','长征精神','沂蒙精神'],explanation:'这一表述来自北斗卫星导航系统建设实践。'},
  {description:'党群同心、军民情深、水乳交融、生死与共',answer:'沂蒙精神',options:['延安精神','沂蒙精神','工匠精神'],explanation:'沂蒙精神是山东红色文化的重要组成。'},
  {description:'追逐梦想、勇于探索、协同攻坚、合作共赢',answer:'探月精神',options:['探月精神','焦裕禄精神','抗战精神'],explanation:'探月精神形成于中国探月工程实践。'},
  {description:'自主创新、艰苦奋斗、大力协同、勇于登攀',answer:'两弹一星精神',options:['雷锋精神','两弹一星精神','劳模精神'],explanation:'两弹一星精神体现科技工作者爱国奉献与协同攻关。'}
]

const saved = readStorage('mgs-learning-progress-v3', {})
const mode=ref('quiz'), cursor=ref(saved.cursor||0), selected=ref(null), answered=ref(false), quizAnswers=ref(Array.isArray(saved.quizAnswers)?saved.quizAnswers:[]), showMistakes=ref(false), fact=ref('')
const orderedEvents=ref([]), orderResult=ref(''), orderCorrect=ref(false), matchIndex=ref(saved.matchIndex||0), matchChoice=ref(''), matchAnswered=ref(false), matchCorrect=ref(saved.matchCorrect||0)
const current=computed(()=>questions[cursor.value]||null), quizCorrect=computed(()=>quizAnswers.value.filter(i=>i.correct).length), quizAccuracy=computed(()=>quizAnswers.value.length?Math.round(quizCorrect.value/quizAnswers.value.length*100):0)
const mistakes=computed(()=>quizAnswers.value.filter(i=>!i.correct).map(i=>questions.find(q=>q.id===i.id)).filter(Boolean))
const remainingEvents=computed(()=>eventOrder.filter(item=>!orderedEvents.value.some(chosen=>chosen.id===item.id)).sort(()=>.5-Math.random()))
const activeMatch=computed(()=>matches[matchIndex.value]||null)
const completed=computed(()=>quizAnswers.value.length+(orderCorrect.value?1:0)+matchIndex.value)
const score=computed(()=>quizCorrect.value*10+(orderCorrect.value?20:0)+matchCorrect.value*8)
const accuracy=computed(()=>{const attempts=quizAnswers.value.length+(orderResult.value?1:0)+matchIndex.value;return attempts?Math.round((quizCorrect.value+(orderCorrect.value?1:0)+matchCorrect.value)/attempts*100):0})
const overallProgress=computed(()=>Math.min(100,Math.round(completed.value/(questions.length+matches.length+1)*100)))

function persist(){writeStorage('mgs-learning-progress-v3',{cursor:cursor.value,quizAnswers:quizAnswers.value,matchIndex:matchIndex.value,matchCorrect:matchCorrect.value})}
function answer(index){if(answered.value)return;selected.value=index;answered.value=true;quizAnswers.value=quizAnswers.value.filter(i=>i.id!==current.value.id).concat({id:current.value.id,correct:index===current.value.answer});persist()}
function optionClass(index){return{selected:selected.value===index,correct:answered.value&&index===current.value.answer,wrong:answered.value&&selected.value===index&&index!==current.value.answer}}
function nextQuestion(){cursor.value+=1;selected.value=null;answered.value=false;persist()}
function resetQuiz(){cursor.value=0;quizAnswers.value=[];selected.value=null;answered.value=false;removeStorage('mgs-learning-progress-v3')}
function randomFact(){const facts=['平台知识库内容均保留来源和考证状态。','主题配图不自动等同于历史现场照片。','收藏和学习进度只保存在当前浏览器。','毛公山核心资源与全国党史拓展资料分区展示。'];fact.value=facts[Math.floor(Math.random()*facts.length)]}
function chooseEvent(item){orderedEvents.value.push(item);orderResult.value=''}
function removeEvent(item){orderedEvents.value=orderedEvents.value.filter(entry=>entry.id!==item.id);orderResult.value=''}
function checkOrder(){orderCorrect.value=orderedEvents.value.every((item,index)=>item.id===eventOrder[index].id);orderResult.value=orderCorrect.value?'排序正确：你已经建立了基本时间坐标。':'顺序还不准确，可结合红色时间轴再次核对。'}
function resetOrder(){orderedEvents.value=[];orderResult.value='';orderCorrect.value=false}
function answerMatch(option){matchChoice.value=option;matchAnswered.value=true;if(option===activeMatch.value.answer)matchCorrect.value+=1;persist()}
function nextMatch(){matchIndex.value+=1;matchChoice.value='';matchAnswered.value=false;persist()}
function resetMatches(){matchIndex.value=0;matchCorrect.value=0;matchChoice.value='';matchAnswered.value=false;persist()}
</script>

<style scoped>
.progress-board{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;align-items:center;padding:22px;margin-bottom:26px}.progress-board div{display:grid;gap:6px}.progress-board span{color:var(--muted)}.progress-board strong{font-size:34px;color:var(--red-dark)}.progress-board .el-progress{grid-column:1/-1}.learning-tabs{padding:20px;background:rgba(255,250,240,.7);border-radius:12px}.quiz-stage{display:grid;grid-template-columns:minmax(0,1fr) 250px;gap:22px}.question-card{padding:clamp(22px,5vw,48px)}.question-card>span,.challenge>span{color:var(--gold);font-weight:800}.question-card h1{font-size:clamp(26px,4vw,42px);color:var(--red-dark)}.question-card>button:not(.el-button){display:flex;gap:14px;width:100%;margin:12px 0;padding:16px;text-align:left;background:#fffaf0;border:1px solid var(--line);border-radius:10px;cursor:pointer}.question-card>button b{display:grid;place-items:center;width:28px;height:28px;color:#fff;background:var(--red);border-radius:50%}.question-card>button.correct,.match-options button.correct{background:#e7f5e9;border-color:#58a565}.question-card>button.wrong,.match-options button.wrong{background:#fff0ed;border-color:#c35b52}.explanation{margin:20px 0;padding:20px;background:#fff2d5;border-left:4px solid var(--gold)}.explanation p{line-height:1.8}.explanation a{color:var(--red);font-weight:800}.tool-box{display:grid;align-content:start;gap:10px;padding:18px}.tool-box button,.report button{padding:10px;border:1px solid var(--line);background:#fff;cursor:pointer}.tool-box p{line-height:1.8;color:var(--muted)}.report,.mistakes,.challenge{padding:clamp(24px,5vw,46px)}.report-bars{height:12px;margin:22px 0;background:#eadcc2;border-radius:9px;overflow:hidden}.report-bars i{display:block;height:100%;background:var(--red);transition:width .6s}.report a,.report button{display:inline-flex;margin-right:10px;padding:12px 16px}.report a{color:#fff;background:var(--red);border-radius:8px}.mistakes{margin-top:24px}.mistakes article{padding:14px 0;border-top:1px solid var(--line)}.challenge h2{color:var(--red-dark);font-size:clamp(25px,4vw,38px)}.choice-bank,.match-options{display:flex;flex-wrap:wrap;gap:12px;margin:24px 0}.choice-bank button,.match-options button{padding:12px 16px;background:#fffaf0;border:1px solid var(--line);border-radius:8px;cursor:pointer}.ordered-list{display:grid;gap:10px;padding:0;list-style:none}.ordered-list li{display:grid;grid-template-columns:70px 1fr 34px;align-items:center;padding:12px;background:#fff;border-left:4px solid var(--red)}.ordered-list button{border:0;background:transparent;font-size:22px;cursor:pointer}.challenge-actions{display:flex;gap:10px;margin:20px 0}.answer-enter-active{transition:.3s}.answer-enter-from{opacity:0;transform:translateY(12px)}@media(max-width:760px){.quiz-stage{grid-template-columns:1fr}.progress-board{grid-template-columns:repeat(3,1fr);padding:15px}.progress-board strong{font-size:25px}.learning-tabs{padding:10px}}
</style>
