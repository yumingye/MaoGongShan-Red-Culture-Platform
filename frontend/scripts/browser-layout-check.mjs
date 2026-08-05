import { spawn } from 'node:child_process'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'

const webBase = (process.env.WEB_BASE_URL || 'http://127.0.0.1:5173').replace(/\/+$/, '')
const apiBlockPattern = process.env.API_BLOCK_PATTERN || '*://127.0.0.1:5173/api/*'
const apiTestBase = (process.env.API_TEST_BASE_URL || 'http://127.0.0.1:8000').replace(/\/+$/, '')

const browserCandidates = [
  process.env.BROWSER_PATH,
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
  'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
].filter(Boolean)

const browserPath = browserCandidates.find((candidate) => fs.existsSync(candidate))
if (!browserPath) {
  console.error('未找到可用于浏览器检查的 Edge 或 Chrome。')
  process.exit(1)
}

// 每次检查使用独立调试端口，避免上一次异常退出的浏览器占用固定端口。
const port = 9300 + (process.pid % 700)
const profile = path.join(os.tmpdir(), `maogongshan-browser-check-${process.pid}`)
const browser = spawn(browserPath, [
  '--headless=new',
  '--disable-gpu',
  '--no-first-run',
  '--no-default-browser-check',
  `--remote-debugging-port=${port}`,
  `--user-data-dir=${profile}`,
  'about:blank'
], { stdio: 'ignore', windowsHide: true })

function delay(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds))
}

async function findPageTarget() {
  for (let attempt = 0; attempt < 40; attempt += 1) {
    try {
      const targets = await fetch(`http://127.0.0.1:${port}/json/list`).then((response) => response.json())
      const target = targets.find((item) => item.type === 'page')
      if (target?.webSocketDebuggerUrl) return target
    } catch {
      // 浏览器启动需要短暂时间，继续轮询。
    }
    await delay(150)
  }
  throw new Error('无法连接浏览器调试端口。')
}

class CdpClient {
  constructor(url) {
    this.socket = new WebSocket(url)
    this.nextId = 1
    this.pending = new Map()
    this.events = []
  }

  async open() {
    await new Promise((resolve, reject) => {
      this.socket.addEventListener('open', resolve, { once: true })
      this.socket.addEventListener('error', reject, { once: true })
    })
    this.socket.addEventListener('message', (event) => {
      const message = JSON.parse(event.data)
      if (message.id) {
        const pending = this.pending.get(message.id)
        if (!pending) return
        this.pending.delete(message.id)
        if (message.error) pending.reject(new Error(message.error.message))
        else pending.resolve(message.result)
        return
      }
      this.events.push(message)
    })
  }

  send(method, params = {}) {
    const id = this.nextId
    this.nextId += 1
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject })
      this.socket.send(JSON.stringify({ id, method, params }))
    })
  }

  close() {
    this.socket.close()
  }
}

async function evaluateJson(cdp, expression, label) {
  for (let attempt = 0; attempt < 4; attempt += 1) {
    const result = await cdp.send('Runtime.evaluate', { expression, returnByValue: true })
    const value = result?.result?.value
    if (typeof value === 'string') {
      try { return JSON.parse(value) } catch { /* 页面仍在切换执行上下文，稍后重试。 */ }
    }
    await delay(250)
  }
  throw new Error(`无法读取页面指标：${label}`)
}

async function waitForPageSettled(cdp, label) {
  for (let attempt = 0; attempt < 100; attempt += 1) {
    try {
      const result = await cdp.send('Runtime.evaluate', {
        expression: `document.readyState === 'complete' &&
          (!document.fonts || document.fonts.status === 'loaded') &&
          (document.querySelector('#app')?.innerText || '').trim().length >= 40 &&
          (document.querySelector('main')?.innerText || '').trim().length >= 40 &&
          !document.querySelector('.route-loading-state') &&
          [...document.querySelectorAll('.page-transition-enter-active,.page-transition-leave-active')]
            .every((element) => Number.parseFloat(getComputedStyle(element).opacity || '1') >= 0.98) &&
          ![...document.querySelectorAll('.reveal:not(.is-visible)')].some((element) => {
            const rect = element.getBoundingClientRect()
            return rect.top < window.innerHeight * 0.92 && rect.bottom > 0
          })`,
        returnByValue: true
      })
      if (result?.result?.value) {
        await delay(180)
        return
      }
    } catch {
      // 页面导航期间执行上下文会短暂重建，继续等待。
    }
    await delay(150)
  }
  let diagnostics = ''
  try {
    const result = await cdp.send('Runtime.evaluate', {
      expression: `JSON.stringify({
        ready: document.readyState,
        fonts: document.fonts?.status,
        textLength: (document.querySelector('#app')?.innerText || '').trim().length,
        mainTextLength: (document.querySelector('main')?.innerText || '').trim().length,
        transitions: [...document.querySelectorAll('.page-transition-enter-active,.page-transition-leave-active')]
          .map((element) => ({
            className: element.className,
            opacity: getComputedStyle(element).opacity
          })),
        hiddenVisible: [...document.querySelectorAll('.reveal:not(.is-visible)')].map((element) => {
          const rect = element.getBoundingClientRect()
          return { className: element.className, top: Math.round(rect.top), bottom: Math.round(rect.bottom) }
        }).filter((item) => item.top < window.innerHeight * 0.92 && item.bottom > 0).slice(0, 6)
      })`,
      returnByValue: true
    })
    diagnostics = result?.result?.value || ''
  } catch {
    diagnostics = '无法读取诊断信息'
  }
  throw new Error(`页面未在限定时间内完成转场：${label} ${diagnostics}`)
}

async function firstId(endpoint, fallback) {
  try {
    const payload = await fetch(`${apiTestBase}${endpoint}`).then((response) => response.json())
    return (payload.items || payload)[0]?.id || fallback
  } catch {
    return fallback
  }
}

async function navigateAndWait(cdp, url, label) {
  let lastError
  for (let attempt = 0; attempt < 3; attempt += 1) {
    cdp.events.length = 0
    await cdp.send('Page.navigate', { url })
    try {
      await waitForPageSettled(cdp, label)
      return
    } catch (error) {
      lastError = error
      if (attempt < 2) await delay(600)
    }
  }
  throw lastError
}

const [figureId, storyId, placeId, imageId] = await Promise.all([
  firstId('/api/figures?page=1&page_size=1', 1),
  firstId('/api/red-stories?page=1&page_size=1', 1),
  firstId('/api/places?page=1&page_size=1', 1),
  firstId('/api/images', 1)
])

const quickMode = process.env.BROWSER_QUICK === '1'
const skipCrawl = process.env.BROWSER_SKIP_CRAWL === '1'
const skipInteractions = process.env.BROWSER_SKIP_INTERACTIONS === '1'
const allRoutes = [
  '/', '/party-history', '/learning/1', '/party-history/stage/agrarian-revolution', '/red-events', '/spirits', '/figures', '/figures/120', '/figures/140', '/timeline', '/scenery', '/resources', '/chat', '/map', '/school', '/research', '/team', '/news',
  '/exhibitions', '/exhibitions/red-zone', '/shandong-red', '/videos', '/videos/party-century', '/learning-challenge',
  '/party-history/stage/may-fourth', '/party-history/stage/agrarian-revolution', '/party-history/stage/new-era', '/search?q=百年党史时间长卷',
  `/figures/${figureId}`, `/stories/${storyId}`, `/places/${placeId}`, `/images/${imageId}`,
  '/photos/summit-terrace-panorama', '/not-exist-browser-check'
]
const allViewports = [
  { name: 'wide-desktop', width: 1920, height: 1080, mobile: false },
  { name: 'desktop', width: 1440, height: 1000, mobile: false },
  { name: 'compact-desktop', width: 1366, height: 768, mobile: false },
  { name: 'tablet', width: 820, height: 1100, mobile: true },
  { name: 'mobile', width: 390, height: 844, mobile: true }
]
const quickRoutes = process.env.BROWSER_ROUTE
  ? process.env.BROWSER_ROUTE.split(',').map((value) => value.trim()).filter(Boolean)
  : ['/', '/scenery', '/research', '/team', '/news']
const routes = process.env.BROWSER_ROUTE ? quickRoutes : quickMode ? quickRoutes : allRoutes
const quickViewport = process.env.BROWSER_VIEWPORT || 'mobile'
const requestedViewports = process.env.BROWSER_VIEWPORT
  ? process.env.BROWSER_VIEWPORT.split(',').map((value) => value.trim()).filter(Boolean)
  : []
const viewports = requestedViewports.length
  ? allViewports.filter((item) => requestedViewports.includes(item.name))
  : quickMode
    ? allViewports.filter((item) => item.name === quickViewport)
    : allViewports
const failures = []
let crawledRouteCount = 0

try {
  const target = await findPageTarget()
  const cdp = new CdpClient(target.webSocketDebuggerUrl)
  await cdp.open()
  await cdp.send('Page.enable')
  await cdp.send('Runtime.enable')
  await cdp.send('Network.enable')
  const screenshotDir = process.env.BROWSER_SCREENSHOT_DIR
    ? path.resolve(process.env.BROWSER_SCREENSHOT_DIR)
    : path.resolve(process.cwd(), '..', 'docs', 'screenshots')
  fs.mkdirSync(screenshotDir, { recursive: true })

  for (const viewport of viewports) {
    await cdp.send('Emulation.setDeviceMetricsOverride', {
      width: viewport.width,
      height: viewport.height,
      deviceScaleFactor: 1,
      mobile: viewport.mobile
    })

    for (const route of routes) {
      try {
        await navigateAndWait(cdp, `${webBase}${route}`, `${viewport.name} ${route}`)
      } catch (error) {
        failures.push(error.message)
        continue
      }
      let metrics
      try {
        metrics = await evaluateJson(cdp, `JSON.stringify({
          title: document.title,
          innerWidth: window.innerWidth,
          scrollWidth: document.documentElement.scrollWidth,
          bodyWidth: document.body.scrollWidth,
          textLength: (document.querySelector('#app')?.innerText || '').trim().length,
          failedImages: [...document.images].filter(img => img.complete && img.naturalWidth === 0).map(img => img.currentSrc || img.src),
          menuDisplay: document.querySelector('.menu-toggle') ? getComputedStyle(document.querySelector('.menu-toggle')).display : 'missing',
          runtimeAlert: document.querySelector('.runtime-alert')?.innerText || ''
        })`, `${viewport.name} ${route}`)
      } catch (error) {
        failures.push(error.message)
        continue
      }
      if (metrics.scrollWidth > metrics.innerWidth + 1 || metrics.bodyWidth > metrics.innerWidth + 1) {
        failures.push(`${viewport.name} ${route} 横向溢出：viewport=${metrics.innerWidth}, document=${metrics.scrollWidth}, body=${metrics.bodyWidth}`)
      }
      if (metrics.textLength < 40) failures.push(`${viewport.name} ${route} 页面正文过少，疑似白屏`)
      if (metrics.failedImages.length) failures.push(`${viewport.name} ${route} 存在失败图片：${metrics.failedImages.join(', ')}`)
      if (metrics.runtimeAlert) failures.push(`${viewport.name} ${route} 捕获到运行时错误：${metrics.runtimeAlert}`)
      if (viewport.mobile && metrics.menuDisplay === 'none') failures.push(`${viewport.name} ${route} 移动菜单按钮不可见`)
      const badResponses = cdp.events.filter((event) => event.method === 'Network.responseReceived' && event.params.response.status >= 400 && !event.params.response.url.includes('favicon'))
      if (badResponses.length) failures.push(`${viewport.name} ${route} 存在失败请求：${badResponses.map((event) => `${event.params.response.status} ${event.params.response.url}`).join(', ')}`)
      const routeExceptions = cdp.events.filter((event) => event.method === 'Runtime.exceptionThrown')
      if (routeExceptions.length) failures.push(`${viewport.name} ${route} 捕获到 ${routeExceptions.length} 个未处理脚本异常`)
      if (['/', '/scenery', '/research', '/team', '/news'].includes(route) && ['wide-desktop', 'mobile'].includes(viewport.name)) {
        await delay(700)
        const shot = await cdp.send('Page.captureScreenshot', { format: 'jpeg', quality: 72, captureBeyondViewport: false })
        const routeName = route === '/' ? 'home' : route.slice(1).replaceAll('/', '-')
        fs.writeFileSync(path.join(screenshotDir, `${routeName}-${viewport.name}.jpg`), Buffer.from(shot.data, 'base64'))
      }
    }
  }

  await cdp.send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false })

  if (!quickMode && !skipCrawl) {
    const discovered = new Set()
    for (const seed of ['/', '/party-history', '/resources', '/research', '/scenery', '/about']) {
      await navigateAndWait(cdp, `${webBase}${seed}`, `链接发现 ${seed}`)
      const links = await evaluateJson(cdp, `JSON.stringify(
        [...document.querySelectorAll('a[href]')]
          .map((link) => new URL(link.href, location.href))
          .filter((url) => url.origin === location.origin && !url.pathname.startsWith('/admin'))
          .map((url) => url.pathname + url.search)
      )`, `链接发现 ${seed}`)
      links.filter((link) => link.startsWith('/') && link !== '/').forEach((link) => discovered.add(link))
    }

    for (const route of [...discovered].sort()) {
      try {
        await navigateAndWait(cdp, `${webBase}${route}`, `链接巡检 ${route}`)
        const result = await evaluateJson(cdp, `JSON.stringify({
          textLength: (document.querySelector('#app')?.innerText || '').trim().length,
          notFound: Boolean(document.querySelector('.not-found')),
          failedImages: [...document.images].filter((img) => img.complete && img.naturalWidth === 0).length,
          runtimeAlert: document.querySelector('.runtime-alert')?.innerText || ''
        })`, `链接巡检 ${route}`)
        if (result.textLength < 40 || result.notFound || result.failedImages || result.runtimeAlert) {
          failures.push(`内部链接异常 ${route}：${JSON.stringify(result)}`)
        }
      } catch (error) {
        failures.push(error.message)
      }
    }
    crawledRouteCount = discovered.size
  }

  const interactions = quickMode || skipInteractions ? [] : [
    {
      route: '/learning-challenge',
      action: `Boolean(document.querySelector('.question-card > button:not(.el-button)')?.click?.() ?? true)`,
      assertion: `Boolean(document.querySelector('.explanation'))`,
      label: '知识闯关答题与解析'
    },
    {
      route: '/timeline',
      action: `Boolean([...document.querySelectorAll('.timeline-actions button')].find(button => button.innerText.includes('自动播放'))?.click?.() ?? true)`,
      assertion: `[...document.querySelectorAll('.timeline-actions button')].some(button => button.innerText.includes('暂停自动播放'))`,
      label: '时间轴自动播放'
    },
    {
      route: '/videos/party-century',
      action: `Boolean(document.querySelector('.motion-toolbar button')?.click?.() ?? true)`,
      assertion: `document.querySelector('.motion-toolbar button')?.innerText.includes('播放')`,
      label: '动态微课暂停'
    },
    {
      route: '/photo-compare',
      action: `(() => { const input=document.querySelector('.photo-compare input'); if(!input)return false; input.value='70'; input.dispatchEvent(new Event('input',{bubbles:true})); return true })()`,
      assertion: `document.querySelector('.photo-compare input')?.value === '70'`,
      label: '照片对比滑块'
    },
    {
      route: '/learning-challenge',
      action: `(() => { const tab=[...document.querySelectorAll('.el-tabs__item')].find(node=>node.innerText.includes('事件排序')); tab?.click(); return Boolean(tab) })()`,
      assertion: `Boolean(document.querySelector('.choice-bank button'))`,
      label: '事件排序模式切换'
    },
    {
      route: '/map',
      action: `(() => { const input=document.querySelector('.filter-row input'); if(!input)return false; input.value='入口'; input.dispatchEvent(new Event('input',{bubbles:true})); return true })()`,
      assertion: `document.querySelector('.filter-row')?.innerText.includes('显示')`,
      label: '地图点位搜索'
    },
    {
      route: '/scenery',
      action: `Boolean(document.querySelector('.museum-photo')?.click?.() ?? true)`,
      assertion: `Boolean(document.querySelector('.photo-lightbox'))`,
      label: '图库大图灯箱打开'
    },
    {
      route: '/',
      action: `Boolean(document.querySelector('.hero-carousel .el-carousel__arrow--right')?.click?.() ?? true)`,
      assertion: `Boolean(document.querySelector('.hero-carousel .el-carousel__item.is-active img'))`,
      label: '首页真实照片轮播切换'
    },
    {
      route: '/search?q=百年党史时间长卷',
      action: `true`,
      assertion: `document.body.innerText.includes('百年党史时间长卷') && document.body.innerText.includes('图文微课')`,
      label: '本地图文微课全站搜索'
    }
  ]
  for (const interaction of interactions) {
    try {
      await navigateAndWait(cdp, `${webBase}${interaction.route}`, `交互 ${interaction.route}`)
    } catch (error) {
      failures.push(error.message)
      continue
    }
    const actionResult = await cdp.send('Runtime.evaluate', { expression: interaction.action, returnByValue: true })
    await delay(180)
    const assertionResult = await cdp.send('Runtime.evaluate', { expression: interaction.assertion, returnByValue: true })
    if (!actionResult.result.value || !assertionResult.result.value) failures.push(`交互失败：${interaction.label} ${interaction.route}`)
  }

  if (!quickMode) {
    await navigateAndWait(cdp, `${webBase}/scenery`, '媒体失败兜底')
    await cdp.send('Runtime.evaluate', { expression: `(() => { const img=document.querySelector('.safe-image img'); if(!img)return false; img.src='/assets/images/forced-missing-test.jpg'; return true })()`, returnByValue: true })
    await delay(500)
    const fallbackResult = await cdp.send('Runtime.evaluate', { expression: `[...document.images].every(img => !img.complete || img.naturalWidth > 0)`, returnByValue: true })
    if (!fallbackResult.result.value) failures.push('媒体失败兜底：强制损坏图片后仍存在裂图')

    await cdp.send('Runtime.evaluate', {
      expression: `(() => { try { sessionStorage.clear() } catch {} return true })()`,
      returnByValue: true
    })
    await cdp.send('Network.setBlockedURLs', { urls: [apiBlockPattern] })
    const offlineRoutes = [
      { route: '/', minText: 80, minImages: 3 },
      { route: '/overview', minText: 180, minImages: 0 },
      { route: '/project', minText: 120, minImages: 0 },
      { route: '/school', minText: 120, minImages: 1 },
      { route: '/team', minText: 180, minImages: 1, minMembers: 6 },
      { route: '/guide', minText: 80, minImages: 0 }
    ]
    for (const offlineRoute of offlineRoutes) {
      await navigateAndWait(cdp, `${webBase}${offlineRoute.route}`, `后端断连降级 ${offlineRoute.route}`)
      const offlinePage = await evaluateJson(cdp, `JSON.stringify({
        textLength: (document.querySelector('main')?.innerText || '').trim().length,
        images: [...document.images].filter((img) => img.complete && img.naturalWidth > 0).length,
        memberCards: document.querySelectorAll('.member-card').length,
        runtimeAlert: document.querySelector('.runtime-alert')?.innerText || ''
      })`, `后端断连降级 ${offlineRoute.route}`)
      if (
        offlinePage.textLength < offlineRoute.minText ||
        offlinePage.images < offlineRoute.minImages ||
        offlinePage.memberCards < (offlineRoute.minMembers || 0) ||
        offlinePage.runtimeAlert
      ) {
        failures.push(`后端断连降级异常 ${offlineRoute.route}：${JSON.stringify(offlinePage)}`)
      }
    }
    await cdp.send('Network.setBlockedURLs', { urls: [] })

    await cdp.send('Network.emulateNetworkConditions', {
      offline: false,
      latency: 450,
      downloadThroughput: 180000,
      uploadThroughput: 90000,
      connectionType: 'cellular3g'
    })
    await navigateAndWait(cdp, `${webBase}/news`, '慢网新闻页')
    const slowPage = await evaluateJson(cdp, `JSON.stringify({
      textLength: (document.querySelector('main')?.textContent || '').trim().length,
      failedImages: [...document.images].filter((img) => img.complete && img.naturalWidth === 0).length
    })`, '慢网新闻页')
    if (slowPage.textLength < 120 || slowPage.failedImages) {
      failures.push(`慢网新闻页异常：${JSON.stringify(slowPage)}`)
    }
    await cdp.send('Network.emulateNetworkConditions', {
      offline: false,
      latency: 0,
      downloadThroughput: -1,
      uploadThroughput: -1,
      connectionType: 'none'
    })
  }

  await cdp.send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 1, mobile: true })
  await navigateAndWait(cdp, `${webBase}/`, '移动端菜单')
  await cdp.send('Runtime.evaluate', { expression: `document.querySelector('.menu-toggle')?.click()`, returnByValue: true })
  await delay(250)
  const menuResult = await cdp.send('Runtime.evaluate', { expression: `JSON.stringify({ expanded:document.querySelector('.menu-toggle')?.getAttribute('aria-expanded'), visible:Boolean(document.querySelector('.mobile-nav')), overflow:document.documentElement.scrollWidth>window.innerWidth+1 })`, returnByValue: true })
  const menuState = JSON.parse(menuResult.result.value || '{}')
  if (menuState.expanded !== 'true' || !menuState.visible || menuState.overflow) failures.push(`移动端菜单状态异常：${JSON.stringify(menuState)}`)

  if (failures.length) failures.forEach((failure) => console.error(`FAIL ${failure}`))
  else {
    const extras = quickMode ? '' : '，以及断网、慢网和坏图降级'
    console.log(`浏览器布局检查通过：${viewports.length} 种视口 × ${routes.length} 条核心路由，${crawledRouteCount} 条页面生成链接，${interactions.length} 项真实交互${extras}。`)
  }
  cdp.close()
} finally {
  browser.kill()
  await Promise.race([
    new Promise((resolve) => browser.once('exit', resolve)),
    delay(1200)
  ])
  try {
    fs.rmSync(profile, { recursive: true, force: true, maxRetries: 3, retryDelay: 200 })
  } catch {
    // Windows 偶尔会短暂锁定 Edge 配置文件，清理失败不影响页面质量判断。
  }
}

if (failures.length) process.exit(1)
