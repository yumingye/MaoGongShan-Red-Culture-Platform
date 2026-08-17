<template>
  <div>
    <PageHero
      title="毛公山地图导览"
      subtitle="以地图点位、路线说明和图文列表联动展示毛公山、城阳区红色文化资源与实践调研路线。"
      image="/assets/images/maogongshan/resource-018.jpg"
      eyebrow="Digital Map"
    />

    <main class="page">
      <p class="data-note">
        地图密钥通过环境变量读取，不写入源码。点位坐标来自公开资料与项目整理，正式导览前建议由景区或地图平台复核。
      </p>

      <section class="map-topic-row reveal">
        <RouterLink to="/map/topic/red-points">红色文化点位</RouterLink>
        <RouterLink to="/map/topic/research-route">调研路线地图</RouterLink>
        <RouterLink to="/map/topic/service">服务设施提示</RouterLink>
        <RouterLink to="/places">地点资源详情</RouterLink>
      </section>

      <el-alert
        v-if="mapMessage"
        :title="mapMessage"
        type="warning"
        show-icon
        class="map-alert"
      />

      <section class="map-layout">
        <div class="map-panel panel">
          <div v-if="hasAmapKey" ref="mapEl" class="amap-box"></div>
          <div v-else class="map-board" aria-label="毛公山静态导览图">
            <div class="map-route"></div>
            <button
              v-for="(spot, index) in filteredSpots"
              :key="spot.id"
              class="map-pin"
              :class="{ active: activeSpot?.id === spot.id }"
              :style="{ left: pinPositions[index % pinPositions.length].left, top: pinPositions[index % pinPositions.length].top }"
              @click="activeSpot = spot"
            >
              <strong>{{ spot.name }}</strong>
              <span>{{ spot.type }} · {{ spot.route_hint || '导览点位' }}</span>
            </button>
          </div>
        </div>

        <aside class="panel spot-card" v-if="activeSpot">
          <SafeImage :src="activeSpot.image_url" :alt="activeSpot.name" />
          <span class="spot-type">{{ activeSpot.type }}</span>
          <h2>{{ activeSpot.name }}</h2>
          <p>{{ activeSpot.description }}</p>
          <dl>
            <div>
              <dt>地址</dt>
              <dd>{{ activeSpot.address || '毛公山及周边区域' }}</dd>
            </div>
            <div>
              <dt>坐标</dt>
              <dd>{{ activeSpot.longitude || '待复核' }}, {{ activeSpot.latitude || '待复核' }}</dd>
            </div>
            <div>
              <dt>资料状态</dt>
              <dd>{{ activeSpot.verification_status || '来源已标注' }}</dd>
            </div>
          </dl>
          <RouterLink class="detail-link" :to="`/places/${activeSpot.id}`">查看点位详情</RouterLink>
        </aside>
      </section>

      <SectionTitle title="点位列表" desc="按资源类型筛选点位，点击列表项可同步高亮地图说明。" />
      <div class="filter-row panel">
        <el-input v-model="keyword" clearable placeholder="搜索点位名称、地址或介绍" aria-label="搜索地图点位" />
        <el-radio-group v-model="activeType">
          <el-radio-button value="全部" />
          <el-radio-button v-for="type in types" :key="type" :value="type" />
        </el-radio-group>
        <span>显示 {{ filteredSpots.length }} / {{ spots.length }} 个点位</span>
      </div>

      <el-empty v-if="!filteredSpots.length" description="没有匹配点位">
        <el-button type="primary" @click="resetFilter">清除筛选</el-button>
      </el-empty>

      <el-table v-else :data="filteredSpots" class="spot-table panel" @row-click="activeSpot = $event">
        <el-table-column prop="name" label="点位名称" min-width="150" />
        <el-table-column prop="type" label="类型" width="130" />
        <el-table-column prop="address" label="地址" min-width="180" />
        <el-table-column prop="description" label="说明" min-width="260" />
        <el-table-column prop="verification_status" label="考证状态" width="130" />
      </el-table>
    </main>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { http, FALLBACK_IMAGES, assetUrl } from '../api/http'
import PageHero from '../components/PageHero.vue'
import SectionTitle from '../components/SectionTitle.vue'
import SafeImage from '../components/SafeImage.vue'

const spots = ref([])
const activeSpot = ref(null)
const activeType = ref('全部')
const keyword = ref('')
const mapEl = ref(null)
const mapMessage = ref('')
const hasAmapKey = computed(() => Boolean(import.meta.env.VITE_AMAP_KEY))
const fallbackImage = '/assets/images/scenery/maogongshan-mountain.jpg'

const pinPositions = [
  { left: '12%', top: '18%' },
  { left: '30%', top: '62%' },
  { left: '55%', top: '28%' },
  { left: '70%', top: '58%' },
  { left: '45%', top: '46%' },
  { left: '18%', top: '50%' },
  { left: '76%', top: '25%' },
  { left: '64%', top: '68%' }
]

const types = computed(() => Array.from(new Set(spots.value.map((item) => item.type).filter(Boolean))))
const filteredSpots = computed(() => {
  const term = keyword.value.trim().toLowerCase()
  return spots.value.filter((item) => {
    const matchesType = activeType.value === '全部' || item.type === activeType.value
    const haystack = `${item.name || ''} ${item.address || ''} ${item.description || ''} ${item.route_hint || ''}`.toLowerCase()
    return matchesType && (!term || haystack.includes(term))
  })
})

watch(filteredSpots, (rows) => {
  if (!rows.some((item) => item.id === activeSpot.value?.id)) {
    activeSpot.value = rows[0] || null
  }
})

function resetFilter() { activeType.value = '全部'; keyword.value = '' }

function loadAmapScript() {
  return new Promise((resolve, reject) => {
    if (window.AMap) return resolve(window.AMap)
    window._AMapSecurityConfig = { securityJsCode: import.meta.env.VITE_AMAP_SECURITY_CODE || '' }
    const script = document.createElement('script')
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${import.meta.env.VITE_AMAP_KEY}&plugin=AMap.Driving,AMap.Walking,AMap.Transfer,AMap.Geolocation`
    script.onload = () => resolve(window.AMap)
    script.onerror = () => reject(new Error('高德地图脚本加载失败'))
    document.head.appendChild(script)
  })
}

function createMapPopup(spot) {
  const root = document.createElement('div')
  root.className = 'amap-safe-popup'
  root.style.maxWidth = '260px'

  const image = document.createElement('img')
  image.src = assetUrl(spot.image_url)
  image.alt = `${spot.name || '地图点位'}图片`
  image.loading = 'lazy'
  Object.assign(image.style, {
    width: '100%',
    height: '110px',
    objectFit: 'cover',
    borderRadius: '8px'
  })
  image.addEventListener('error', () => {
    image.src = FALLBACK_IMAGES.scenery
  }, { once: true })

  const title = document.createElement('h3')
  title.textContent = spot.name || '地图点位'
  const description = document.createElement('p')
  description.textContent = spot.description || '可在右侧点位列表查看完整介绍。'
  const status = document.createElement('p')
  status.textContent = spot.verification_status || '来源已标注'
  root.append(image, title, description, status)
  return root
}

async function initMap() {
  if (!hasAmapKey.value) {
    mapMessage.value = '尚未配置高德地图 Key，当前显示本地静态导览和点位列表。'
    return
  }

  try {
    await nextTick()
    const AMap = await loadAmapScript()
    const center = [120.39, 36.32]
    const map = new AMap.Map(mapEl.value, { zoom: 13, center, resizeEnable: true })
    map.addControl(new AMap.Geolocation({ position: 'RB' }))

    spots.value.forEach((spot) => {
      const marker = new AMap.Marker({
        position: [Number(spot.longitude || center[0]), Number(spot.latitude || center[1])],
        title: spot.name,
        map
      })
      const info = new AMap.InfoWindow({ content: createMapPopup(spot), offset: new AMap.Pixel(0, -28) })
      marker.on('click', () => {
        activeSpot.value = spot
        info.open(map, marker.getPosition())
      })
    })
  } catch (error) {
    mapMessage.value = `${error.message}，已切换为本地静态导览。`
  }
}

onMounted(async () => {
  try {
    spots.value = (await http.get('/api/scenic-spots')).data
    activeSpot.value = spots.value[0] || null
    await initMap()
  } catch {
    mapMessage.value = '点位接口暂时不可用，地图页其他导览入口仍可继续访问。'
  }
})
</script>

<style scoped>
.map-topic-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 16px 0 18px;
}

.map-topic-row a {
  padding: 10px 14px;
  color: var(--red-dark);
  background: #fffaf0;
  border: 1px solid var(--line);
  border-radius: 999px;
}

.map-topic-row a:hover {
  color: #fff8e6;
  background: var(--red);
}

.map-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(300px, 0.7fr);
  gap: 22px;
  align-items: stretch;
  margin-bottom: 32px;
}

.map-panel {
  padding: 0;
  overflow: hidden;
}

.amap-box,
.map-board {
  width: 100%;
  min-height: 560px;
}

.map-alert,
.filter-row {
  margin-bottom: 16px;
}

.filter-row { display:grid;grid-template-columns:minmax(220px,1fr) auto auto;gap:14px;align-items:center;padding:16px; }
.filter-row > span { color:var(--muted);white-space:nowrap; }

.map-pin {
  border: 0;
  text-align: left;
  cursor: pointer;
}

.map-pin.active {
  background: rgba(255, 248, 229, 0.96);
  color: var(--red-dark);
  box-shadow: 0 14px 30px rgba(95, 20, 24, 0.28);
  transform: translateY(-3px);
}

.spot-card {
  padding: 18px;
}

.spot-card :deep(.safe-image) {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  border-radius: 10px;
}

.spot-type {
  display: inline-flex;
  margin-top: 14px;
  color: var(--gold);
  font-weight: 700;
}

.spot-card h2 {
  margin: 8px 0;
  color: var(--red-dark);
}

.spot-card p {
  color: var(--muted);
  line-height: 1.8;
}

.spot-card dl {
  display: grid;
  gap: 10px;
}

.spot-card dl div {
  display: grid;
  grid-template-columns: 76px minmax(0, 1fr);
  gap: 10px;
}

.spot-card dt {
  color: var(--muted);
}

.spot-card dd {
  margin: 0;
}

.detail-link {
  display: inline-flex;
  margin-top: 16px;
  color: var(--red);
  font-weight: 700;
}

.spot-table {
  overflow: hidden;
}

@media (max-width: 900px) {
  .map-layout {
    grid-template-columns: 1fr;
  }

  .amap-box,
  .map-board {
    min-height: 460px;
  }

  .filter-row { grid-template-columns:1fr; }
}
</style>
