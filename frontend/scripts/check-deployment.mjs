import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const frontendRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const projectRoot = path.resolve(frontendRoot, '..')
const distRoot = path.join(frontendRoot, 'dist')
const failures = []

function requireFile(file, label) {
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) {
    failures.push(`${label} 不存在：${file}`)
  }
}

function walkFiles(directory) {
  if (!fs.existsSync(directory)) return []
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const fullPath = path.join(directory, entry.name)
    return entry.isDirectory() ? walkFiles(fullPath) : [fullPath]
  })
}

requireFile(path.join(projectRoot, 'render.yaml'), 'Render Blueprint')
requireFile(path.join(projectRoot, 'railway.toml'), 'Railway 配置')
requireFile(path.join(frontendRoot, 'vercel.json'), 'Vercel 配置')
requireFile(path.join(projectRoot, '.env.example'), '根环境变量示例')
requireFile(path.join(projectRoot, 'backend', '.env.example'), '后端环境变量示例')
requireFile(path.join(frontendRoot, '.env.example'), '前端环境变量示例')
requireFile(path.join(frontendRoot, '.env.production.example'), '生产环境变量示例')
requireFile(path.join(frontendRoot, 'package-lock.json'), '前端依赖锁文件')
requireFile(path.join(distRoot, 'index.html'), '生产构建入口')
requireFile(
  path.join(frontendRoot, 'public', 'assets', 'images', 'fallback', 'fallback-real-scenery.jpg'),
  '图片备用资源'
)

const blueprintPath = path.join(projectRoot, 'render.yaml')
if (fs.existsSync(blueprintPath)) {
  const blueprint = fs.readFileSync(blueprintPath, 'utf8')
  for (const required of [
    'runtime: python',
    'healthCheckPath: /api/health',
    'uvicorn backend.app:app --host 0.0.0.0 --port $PORT',
    'ENVIRONMENT',
    'production',
    'CORS_ORIGINS',
    'sync: false'
  ]) {
    if (!blueprint.includes(required)) failures.push(`render.yaml 缺少：${required}`)
  }
  if (/property:\s*host/.test(blueprint)) {
    failures.push('render.yaml 不应把 Render 私有网络 host 注入浏览器端')
  }
  if (/value:\s*https?:\/\/(?:localhost|127\.0\.0\.1)/i.test(blueprint)) {
    failures.push('render.yaml 的生产环境变量包含 localhost 地址')
  }
}

const vercelPath = path.join(frontendRoot, 'vercel.json')
if (fs.existsSync(vercelPath)) {
  const vercelConfig = JSON.parse(fs.readFileSync(vercelPath, 'utf8'))
  if (vercelConfig.framework !== 'vite') failures.push('vercel.json framework 必须为 vite')
  if (vercelConfig.outputDirectory !== 'dist') failures.push('vercel.json outputDirectory 必须为 dist')
  const spaRewrite = vercelConfig.rewrites?.some(
    (item) => item.source === '/(.*)' && item.destination === '/index.html'
  )
  if (!spaRewrite) failures.push('vercel.json 缺少 SPA 深层路由 Rewrite')
}

const railwayPath = path.join(projectRoot, 'railway.toml')
if (fs.existsSync(railwayPath)) {
  const railway = fs.readFileSync(railwayPath, 'utf8')
  for (const required of [
    'pip install -r backend/requirements.txt',
    'uvicorn backend.app:app --host 0.0.0.0 --port $PORT',
    'healthcheckPath = "/api/health"'
  ]) {
    if (!railway.includes(required)) failures.push(`railway.toml 缺少：${required}`)
  }
}

const productionEnvPath = path.join(frontendRoot, '.env.production.example')
if (fs.existsSync(productionEnvPath)) {
  const productionEnv = fs.readFileSync(productionEnvPath, 'utf8')
  if (!/^VITE_API_BASE_URL=https:\/\//m.test(productionEnv)) {
    failures.push('生产环境示例缺少 HTTPS VITE_API_BASE_URL')
  }
  if (/https?:\/\/(?:localhost|127\.0\.0\.1)/i.test(productionEnv)) {
    failures.push('生产环境示例包含 localhost 地址')
  }
}

const buildFiles = walkFiles(distRoot).filter((file) => /\.(html|js|css|json)$/i.test(file))
for (const file of buildFiles) {
  const content = fs.readFileSync(file, 'utf8')
  if (/file:\/\/|[A-Za-z]:\\Users\\/i.test(content)) {
    failures.push(`生产构建包含本机绝对路径：${path.relative(distRoot, file)}`)
  }
  const isAxiosVendor = /^axios-.*\.js$/i.test(path.basename(file))
  if (!isAxiosVendor && /https?:\/\/(?:localhost|127\.0\.0\.1)(?::\d+)?/i.test(content)) {
    failures.push(`生产构建包含 localhost 地址：${path.relative(distRoot, file)}`)
  }
}

const indexPath = path.join(distRoot, 'index.html')
if (fs.existsSync(indexPath)) {
  const html = fs.readFileSync(indexPath, 'utf8')
  const localRefs = [...html.matchAll(/(?:src|href)="\/([^"]+)"/g)].map((match) => match[1])
  for (const reference of localRefs) {
    const target = path.join(distRoot, ...reference.split('/'))
    if (!fs.existsSync(target)) failures.push(`构建入口引用不存在：/${reference}`)
  }
}

if (failures.length) {
  failures.forEach((failure) => console.error(`FAIL ${failure}`))
  process.exit(1)
}

console.log(
  `部署检查通过：${buildFiles.length} 个构建文本资源，Vercel、Render、Railway、SPA Rewrite、环境变量和本地路径均正常。`
)
