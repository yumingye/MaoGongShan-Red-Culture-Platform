import fs from 'node:fs'
import path from 'node:path'

const root = process.cwd()
const projectRoot = path.resolve(root, '..')
const srcDir = path.join(root, 'src')
const publicDir = path.join(root, 'public')
const dataDir = path.join(srcDir, 'data')
const staticOnly = process.argv.includes('--static-only')

const failures = []
const warnings = []

function fail(message) {
  failures.push(message)
}

function warn(message) {
  warnings.push(message)
}

function readText(file) {
  return fs.readFileSync(file, 'utf8')
}

function walk(dir, filter = () => true) {
  if (!fs.existsSync(dir)) return []
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const full = path.join(dir, entry.name)
    if (entry.isDirectory()) return walk(full, filter)
    return filter(full) ? [full] : []
  })
}

function assertNoForbiddenText() {
  const forbidden = [
    /Lorem ipsum/i,
    /占位图|空白图片|模拟数据|请管理员添加/,
    /姣涘|绾㈣|灞辫|鏁板|瀹炶|鍦板|鍥剧|璧勬|鈫|俙|锛/,
    /\/images\/.*\.svg/
  ]
  const files = [
    ...walk(srcDir, (file) => /\.(vue|js|json|css)$/.test(file)),
    path.join(projectRoot, 'README.md'),
    path.join(projectRoot, 'backend', 'app.py')
  ].filter(fs.existsSync)

  for (const file of files) {
    const text = readText(file)
    for (const pattern of forbidden) {
      if (pattern.test(text)) {
        fail(`发现禁用文案、乱码或旧图片路径：${path.relative(projectRoot, file)} -> ${pattern}`)
      }
    }
  }
}

function getImageSize(file) {
  const buffer = fs.readFileSync(file)
  const ext = path.extname(file).toLowerCase()

  if (ext === '.png' && buffer.length >= 24 && buffer.toString('ascii', 1, 4) === 'PNG') {
    return { width: buffer.readUInt32BE(16), height: buffer.readUInt32BE(20) }
  }

  if (ext === '.gif' && buffer.length >= 10 && buffer.toString('ascii', 0, 3) === 'GIF') {
    return { width: buffer.readUInt16LE(6), height: buffer.readUInt16LE(8) }
  }

  if (['.jpg', '.jpeg'].includes(ext) && buffer[0] === 0xff && buffer[1] === 0xd8) {
    let offset = 2
    while (offset < buffer.length) {
      if (buffer[offset] !== 0xff) break
      const marker = buffer[offset + 1]
      const length = buffer.readUInt16BE(offset + 2)
      if (marker >= 0xc0 && marker <= 0xc3) {
        return { height: buffer.readUInt16BE(offset + 5), width: buffer.readUInt16BE(offset + 7) }
      }
      offset += 2 + length
    }
  }

  return null
}

function assertLocalImages() {
  const imageRoot = path.join(publicDir, 'assets', 'images')
  const imageFiles = walk(imageRoot, (file) => /\.(jpg|jpeg|png|webp|gif)$/i.test(file))
  if (imageFiles.length < 60) fail(`本地图片数量不足：${imageFiles.length}`)
  if (!fs.existsSync(path.join(imageRoot, 'fallback', 'fallback-real-scenery.jpg'))) {
    fail('缺少图片加载失败备用图：assets/images/fallback/fallback-real-scenery.jpg')
  }

  const tooLarge = imageFiles.filter((file) => fs.statSync(file).size > 2_000_000)
  if (tooLarge.length) warn(`存在大于 2MB 的图片 ${tooLarge.length} 张，建议继续压缩。`)

  for (const file of imageFiles) {
    if (path.extname(file).toLowerCase() === '.webp') continue
    const size = getImageSize(file)
    const label = path.relative(projectRoot, file)
    if (!size) {
      fail(`图片文件无法读取尺寸，可能损坏：${label}`)
      continue
    }
    if (size.width < 120 || size.height < 120) {
      fail(`图片尺寸过小，容易造成空白或黑屏观感：${label} ${size.width}x${size.height}`)
    }
    if (size.width / size.height > 12 || size.height / size.width > 12) {
      warn(`图片比例过窄，建议避免用于首屏或卡片封面：${label} ${size.width}x${size.height}`)
    }
  }
}

function assertTopicImages() {
  const topicFiles = ['topicPages.js', 'experienceContent.js'].map((name) => path.join(srcDir, 'data', name)).filter(fs.existsSync)
  for (const topicFile of topicFiles) {
    const text = readText(topicFile)
    const matches = [...text.matchAll(/['"](\/assets\/images\/[^'"]+)['"]/g)].map((match) => match[1])
    for (const image of matches) {
      const normalized = image.startsWith('/') ? image.slice(1) : image
      const full = path.join(publicDir, normalized)
      if (!fs.existsSync(full)) fail(`专题图片不存在：${image}`)
    }
  }
}

function assertDataFiles() {
  const files = walk(dataDir, (file) => file.endsWith('.json'))
  for (const file of files) {
    let rows
    try {
      rows = JSON.parse(readText(file))
    } catch (error) {
      fail(`JSON 解析失败：${path.relative(projectRoot, file)} ${error.message}`)
      continue
    }
    if (!Array.isArray(rows) && Array.isArray(rows?.images)) {
      rows = rows.images
    }
    if (!Array.isArray(rows)) {
      warn(`数据文件不是数组：${path.relative(projectRoot, file)}`)
      continue
    }
    const ids = new Set()
    const titles = new Set()
    for (const [index, item] of rows.entries()) {
      const label = `${path.relative(projectRoot, file)}[${index}]`
      if (!item.id) fail(`${label} 缺少 id`)
      if (ids.has(item.id)) fail(`${label} id 重复：${item.id}`)
      ids.add(item.id)
      const title = item.title || item.name
      if (!title) fail(`${label} 缺少标题`)
      if (title && titles.has(title)) warn(`${label} 标题重复：${title}`)
      if (title) titles.add(title)
      if (!item.content && !item.summary && !item.description) fail(`${label} 缺少正文或摘要`)
      const images = [item.image, item.cover, item.photo, item.local_path, ...(Array.isArray(item.gallery) ? item.gallery : [])].filter(Boolean)
      for (const image of images) {
        if (typeof image !== 'string' || image.startsWith('http') || image.startsWith('data:')) continue
        const normalized = image.startsWith('/') ? image.slice(1) : image
        const full = path.join(publicDir, normalized)
        if (!fs.existsSync(full)) fail(`${label} 图片不存在：${image}`)
      }
    }
  }
}

async function fetchOk(url, label) {
  try {
    const response = await fetch(url, { signal: AbortSignal.timeout(8000) })
    if (!response.ok) fail(`${label} 返回 ${response.status}: ${url}`)
    return response
  } catch (error) {
    fail(`${label} 请求失败：${url} ${error.message}`)
    return null
  }
}

async function getJson(url) {
  const response = await fetchOk(url, 'API')
  if (!response) return null
  return response.json().catch(() => null)
}

function extractRows(payload) {
  return Array.isArray(payload) ? payload : payload?.items || []
}

async function assertApis() {
  const apiBase = (process.env.API_TEST_BASE_URL || 'http://127.0.0.1:8000').replace(/\/+$/, '')
  const endpoints = [
    '/api/health',
    '/docs',
    '/api/stats',
    '/api/home',
    '/api/events',
    '/api/figures',
    '/api/resources',
    '/api/images',
    '/api/research-logs',
    '/api/audio-guides',
    '/api/red-stories',
    '/api/places',
    '/api/achievements',
    '/api/learning-articles',
    '/api/platform-overview',
    '/api/scenic-spots',
    '/api/chat/suggestions',
    '/api/search/suggestions?q=毛公山'
  ]
  for (const endpoint of endpoints) await fetchOk(`${apiBase}${endpoint}`, 'API')

  const counts = [
    ['历史事件', '/api/events?page=1&page_size=1', 50],
    ['人物资料', '/api/figures?page=1&page_size=1', 30],
    ['红色故事', '/api/red-stories?page=1&page_size=1', 50],
    ['地点资源', '/api/places?page=1&page_size=1', 30],
    ['数字资源', '/api/resources?page=1&page_size=1', 250],
    ['实践成果', '/api/achievements?page=1&page_size=1', 25],
    ['党史学习专题', '/api/learning-articles?page=1&page_size=1', 50]
  ]
  for (const [name, endpoint, min] of counts) {
    const payload = await getJson(`${apiBase}${endpoint}`)
    const total = payload?.total ?? extractRows(payload).length
    if (total < min) fail(`${name} 数量不足：${total} / ${min}`)
  }

  const arrayCounts = [
    ['实践日志', '/api/research-logs', 35],
    ['音频讲解', '/api/audio-guides', 20],
    ['图库图片', '/api/images', 100],
    ['地图点位', '/api/scenic-spots', 12]
  ]
  for (const [name, endpoint, min] of arrayCounts) {
    const payload = await getJson(`${apiBase}${endpoint}`)
    const total = extractRows(payload).length
    if (total < min) fail(`${name} 数量不足：${total} / ${min}`)
  }

  const images = extractRows(await getJson(`${apiBase}/api/images`))
  for (const image of images) {
    if (!image.image_url) {
      fail(`图库图片缺少 image_url：${image.id} ${image.title || ''}`)
      continue
    }
    if (image.image_url.startsWith('http') || image.image_url.startsWith('data:')) continue
    const normalized = image.image_url.startsWith('/') ? image.image_url.slice(1) : image.image_url
    const full = path.join(publicDir, normalized)
    if (!fs.existsSync(full)) fail(`图库接口返回的图片路径不存在：${image.id} ${image.image_url}`)
  }

  const learning = extractRows(await getJson(`${apiBase}/api/learning-articles?page=1&page_size=100`))
  const spiritCount = learning.filter((article) => article.category === '红色精神').length
  if (spiritCount < 30) fail(`红色精神独立专题不足：${spiritCount} / 30`)
  for (const article of learning) {
    if (!article.title || !article.content || article.content.length < 800) fail(`党史专题正文不完整：${article.id} ${article.title || ''}`)
    if (!article.source_name || !article.source_url) fail(`党史专题缺少来源：${article.id} ${article.title || ''}`)
    if (!article.scope || !article.verification_status) fail(`党史专题缺少范围或核验状态：${article.id} ${article.title || ''}`)
    const normalized = article.image?.startsWith('/') ? article.image.slice(1) : article.image
    if (!normalized || !fs.existsSync(path.join(publicDir, normalized))) fail(`党史专题图片不存在：${article.id} ${article.image || ''}`)
  }

  const detailCollections = [
    ['/api/events?page=1&page_size=200', '/api/events', '历史事件'],
    ['/api/figures?page=1&page_size=200', '/api/figures', '人物档案'],
    ['/api/resources?page=1&page_size=400', '/api/resources', '数字资源'],
    ['/api/images', '/api/images', '图片详情'],
    ['/api/research-logs', '/api/research-logs', '实践日志'],
    ['/api/audio-guides', '/api/audio-guides', '音频讲解'],
    ['/api/red-stories?page=1&page_size=200', '/api/red-stories', '红色故事'],
    ['/api/places?page=1&page_size=200', '/api/places', '地点资源'],
    ['/api/achievements?page=1&page_size=200', '/api/achievements', '实践成果'],
    ['/api/learning-articles?page=1&page_size=100', '/api/learning-articles', '党史专题']
  ]
  let checkedDetails = 0
  for (const [listEndpoint, detailPrefix, label] of detailCollections) {
    const rows = extractRows(await getJson(`${apiBase}${listEndpoint}`))
    for (const row of rows) {
      const detail = await getJson(`${apiBase}${detailPrefix}/${row.id}`)
      if (!detail || !(detail.title || detail.name)) fail(`${label}详情为空：${row.id}`)
      checkedDetails += 1
    }
  }
  if (checkedDetails < 300) fail(`全量详情接口覆盖不足：${checkedDetails} / 300`)
}

async function assertChat() {
  const apiBase = (process.env.API_TEST_BASE_URL || 'http://127.0.0.1:8000').replace(/\/+$/, '')
  const questions = [
    '毛公山在哪里', '毛公山有什么红色故事', '山东大学软件学院做了什么', '怎么游览毛公山', '平台有哪些资源',
    '图片资料有没有来源', '地图没有 Key 怎么办', '山软青年专题在哪里', '实践团队做了哪些工作', '音频讲解怎么使用',
    '毛公山有什么景色', '城阳红色文化有哪些内容', '怎么查询历史资料', '怎么收藏资源', '最近浏览在哪里看',
    '这个平台是谁开发的', '软件学院为什么做这个项目', '技术架构是什么', '数据来源在哪里', '哪些内容需要核验',
    '如何查看图片详情', '如何打开资源详情', '如何看实践日志', '三维沙盘有什么用', '地图导览有哪些点位',
    '如何搜索山东大学', '如何搜索人物资料', '如何搜索红色故事', '如何查看时间轴', '如何查看成果展示',
    '平台是否收集隐私', 'Word 文档信息如何处理', '图片能否商业使用', '问答会不会编造', '没有资料时怎么回答',
    '毛公山登山路线', '红色文化教育价值', '青年实践意义', '数字资源库类型', '访谈记录在哪里',
    '调研路线是什么', '项目成果有哪些', '软件赋能红色文化', '如何配置高德地图', '后台默认账号',
    '使用帮助在哪里', '收藏中心怎么用', '全景图库分类', '音频没有声音怎么办', 'API 文档在哪里',
    '五四运动有什么历史意义', '中共一大在哪里召开', '南昌起义是什么', '长征精神是什么', '遵义会议为什么重要',
    '延安精神的主要内容', '西柏坡精神有什么启示', '雷锋精神如何理解', '焦裕禄精神是什么', '科学家精神包括什么',
    '毛公山资料和全国党史内容如何区分', '山东红色文化有哪些学习线索'
  ]

  const answers = []
  for (const question of questions) {
    const chat = await fetch(`${apiBase}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
      signal: AbortSignal.timeout(8000)
    }).then((res) => res.json()).catch((error) => ({ error: error.message }))
    if (!chat.answer || chat.answer.length < 20) fail(`问答回答过短或为空：${question}`)
    answers.push(chat.answer)
  }
  if (new Set(answers).size <= 2) fail('问答结果重复度过高，疑似固定模板回答。')
}

async function assertRoutes() {
  const webBase = (process.env.WEB_BASE_URL || 'http://127.0.0.1:5173').replace(/\/+$/, '')
  const apiBase = (process.env.API_TEST_BASE_URL || 'http://127.0.0.1:8000').replace(/\/+$/, '')
  const payloads = await Promise.all([
    getJson(`${apiBase}/api/events?page=1&page_size=10`),
    getJson(`${apiBase}/api/figures?page=1&page_size=5`),
    getJson(`${apiBase}/api/resources?page=1&page_size=5`),
    getJson(`${apiBase}/api/images`),
    getJson(`${apiBase}/api/research-logs`),
    getJson(`${apiBase}/api/audio-guides`),
    getJson(`${apiBase}/api/red-stories?page=1&page_size=5`),
    getJson(`${apiBase}/api/places?page=1&page_size=5`),
    getJson(`${apiBase}/api/achievements?page=1&page_size=5`),
    getJson(`${apiBase}/api/learning-articles?page=1&page_size=12`)
  ])

  const many = (payload, prefix, limit) => extractRows(payload).slice(0, limit).map((item) => `${prefix}/${item.id}`)
  const routes = [
    '/',
    '/overview',
    '/overview/geography',
    '/overview/name-origin',
    '/overview/nature',
    '/overview/culture',
    '/overview/routes',
    '/history',
    '/party-history',
    '/party-history/stage/may-fourth',
    '/party-history/stage/party-founding',
    '/party-history/stage/great-revolution',
    '/party-history/stage/agrarian-revolution',
    '/party-history/stage/war-resistance',
    '/party-history/stage/liberation-war',
    '/party-history/stage/socialist-construction',
    '/party-history/stage/reform-opening',
    '/party-history/stage/new-era',
    '/red-events',
    '/spirits',
    '/red-culture',
    '/exhibitions',
    '/exhibitions/red-zone',
    '/exhibitions/shandong-red',
    '/exhibitions/qingdao-red',
    '/exhibitions/sdu-practice',
    '/exhibitions/youth-mission',
    '/shandong-red',
    '/qingdao-red',
    '/youth-mission',
    '/conferences',
    '/red-books',
    '/red-relics',
    '/photo-compare',
    '/study-routes',
    '/videos',
    '/videos/party-century',
    '/videos/long-march-route',
    '/videos/software-practice',
    '/learning-challenge',
    '/red-scenic',
    '/history/topic/spirit',
    '/history/topic/qingdao-memory',
    '/figures',
    '/timeline',
    '/stories',
    '/scenery',
    '/gallery/maogongshan',
    '/gallery/red-culture',
    '/gallery/research',
    '/gallery/school',
    '/map',
    '/map/topic/red-points',
    '/map/topic/research-route',
    '/map/topic/service',
    '/resources',
    '/resources/category/documents',
    '/resources/category/images',
    '/resources/category/audio',
    '/resources/category/achievements',
    '/research',
    '/research/topic/route',
    '/research/topic/interviews',
    '/research/topic/methods',
    '/research/topic/reflections',
    '/school',
    '/school/topic/introduction',
    '/school/topic/architecture',
    '/school/topic/development',
    '/school/topic/responsibility',
    '/search?q=毛公山',
    '/admin',
    '/about',
    '/project',
    '/plan',
    '/results',
    '/team',
    '/sources',
    '/chat',
    '/guide',
    '/audio',
    '/sandtable',
    '/favorites',
    '/help',
    ...many(payloads[0], '/events', 10),
    ...many(payloads[1], '/figures', 5),
    ...many(payloads[2], '/resources', 5),
    ...many(payloads[3], '/images', 5),
    ...many(payloads[4], '/research', 3),
    ...many(payloads[5], '/audio', 2),
    ...many(payloads[6], '/stories', 3),
    ...many(payloads[7], '/places', 3),
    ...many(payloads[8], '/achievements', 3),
    ...many(payloads[9], '/learning', 10),
    '/not-exist-quality-check'
  ]
  for (const route of Array.from(new Set(routes))) await fetchOk(`${webBase}${route}`, '前端路由')
}

async function main() {
  assertNoForbiddenText()
  assertDataFiles()
  assertTopicImages()
  assertLocalImages()
  if (!staticOnly) {
    await assertApis()
    await assertChat()
    await assertRoutes()
  }

  for (const item of warnings) console.warn(`WARN ${item}`)
  if (failures.length) {
    for (const item of failures) console.error(`FAIL ${item}`)
    process.exit(1)
  }
  console.log(`质量检查通过：${warnings.length} 个提醒，0 个失败。`)
}

main()
