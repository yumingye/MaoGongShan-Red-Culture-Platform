<template>
  <div>
    <PageHero title="毛公山三维数字沙盘" subtitle="以三维地形、路线光带和资源点标记展示毛公山核心景区与扩展导览关系。" image="/assets/images/scenery/maogongshan-mountain.jpg" eyebrow="3D Digital Sand Table" />
    <main class="page">
      <section class="sand-layout">
        <div class="sand-scene panel reveal">
          <div class="terrain">
            <div class="ridge ridge-a"></div>
            <div class="ridge ridge-b"></div>
            <div class="route-line"></div>
            <button v-for="(spot, index) in spots" :key="spot.id" class="pin3d" :style="pinStyle(index)" @click="selected = spot">
              <span></span>{{ index + 1 }}
            </button>
          </div>
        </div>
        <aside class="sand-info panel reveal">
          <p class="eyebrow">当前点位</p>
          <h2>{{ selected?.name || '毛公山景区' }}</h2>
          <SafeImage :src="selected?.image_url || '/assets/images/scenery/maogongshan-mountain.jpg'" :alt="selected?.name || '毛公山景区'" />
          <p>{{ selected?.description || '毛公山数字沙盘整合景点、路线、红色文化资源点和周边环境信息。' }}</p>
          <el-tag type="danger">{{ selected?.type || '核心景区' }}</el-tag>
        </aside>
      </section>

      <SectionTitle title="路线展示" desc="结合登山步道、红色文旅研学和登山节公开资料整理。" />
      <div class="grid grid-4">
        <article v-for="route in routes" :key="route.id" class="route-card reveal">
          <h3>{{ route.name }}</h3>
          <p>{{ route.summary }}</p>
          <span>{{ route.start_point }} → {{ route.end_point }}</span>
        </article>
      </div>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { http } from '../api/http'
import PageHero from '../components/PageHero.vue'
import SectionTitle from '../components/SectionTitle.vue'
import SafeImage from '../components/SafeImage.vue'

const spots = ref([])
const routes = ref([])
const selected = ref(null)

function pinStyle(index) {
  const points = [
    ['22%', '58%'], ['36%', '48%'], ['52%', '42%'], ['65%', '54%'], ['74%', '36%'], ['45%', '66%']
  ]
  const [left, top] = points[index % points.length]
  return { left, top }
}

onMounted(async () => { try { const [spotRes, routeRes] = await Promise.all([http.get('/api/scenic-spots'), http.get('/api/routes')]); spots.value = spotRes.data; routes.value = routeRes.data; selected.value = spots.value[0] } catch { spots.value=[]; routes.value=[] } })
</script>

<style scoped>
.sand-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 24px;
}

.sand-scene {
  min-height: 620px;
  padding: 28px;
  perspective: 1100px;
  background: linear-gradient(135deg, #1b2622, #5d191d);
}

.terrain {
  position: relative;
  width: 100%;
  height: 540px;
  transform: rotateX(58deg) rotateZ(-8deg);
  transform-style: preserve-3d;
  border-radius: 42px;
  background:
    radial-gradient(circle at 35% 40%, rgba(201, 162, 75, .72), transparent 18%),
    radial-gradient(circle at 62% 48%, rgba(47, 111, 94, .92), transparent 26%),
    linear-gradient(135deg, #315d45, #7e8b53 48%, #3a604b);
  box-shadow: 0 80px 110px rgba(0, 0, 0, .34);
}

.ridge {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, .18);
  filter: blur(1px);
}

.ridge-a { inset: 18% 42% 44% 18%; transform: translateZ(60px); }
.ridge-b { inset: 34% 18% 24% 46%; transform: translateZ(82px); }

.route-line {
  position: absolute;
  left: 18%;
  top: 60%;
  width: 62%;
  height: 8px;
  background: linear-gradient(90deg, #ffe08a, #c9342d);
  border-radius: 999px;
  transform: translateZ(96px) rotate(-14deg);
  box-shadow: 0 0 24px rgba(255, 224, 138, .86);
}

.pin3d {
  position: absolute;
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  color: #fff;
  cursor: pointer;
  background: #b9262d;
  border: 2px solid #ffe08a;
  border-radius: 50%;
  transform: translateZ(130px) rotateZ(8deg) rotateX(-58deg);
  box-shadow: 0 12px 22px rgba(0, 0, 0, .25);
}

.sand-info {
  padding: 22px;
}

.sand-info img {
  width: 100%;
  height: 210px;
  object-fit: cover;
  border-radius: 12px;
}

.sand-info h2,
.route-card h3 {
  color: var(--red-dark);
}

.sand-info p,
.route-card p,
.route-card span {
  color: var(--muted);
  line-height: 1.8;
}

.route-card {
  padding: 18px;
  background: #fffaf0;
  border: 1px solid var(--line);
  border-radius: 14px;
  box-shadow: 0 14px 34px rgba(84, 16, 21, .1);
}

@media (max-width: 900px) {
  .sand-layout {
    grid-template-columns: 1fr;
  }
}
</style>
