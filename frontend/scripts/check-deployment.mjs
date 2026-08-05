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
requireFile(path.join(projectRoot, 'netlify.toml'), 'Netlify 配置')
requireFile(path.join(frontendRoot, 'public', '_redirects'), 'Netlify SPA 路由规则')
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

const netlifyPath = path.join(projectRoot, 'netlify.toml')
if (fs.existsSync(netlifyPath)) {
  const netlify = fs.readFileSync(netlifyPath, 'utf8')
  for (const required of [
    'base = "frontend"',
    'command = "npm run build"',
    'publish = "dist"',
    'from = "/*"',
    'to = "/index.html"',
    'status = 200'
  ]) {
    if (!netlify.includes(required)) failures.push(`netlify.toml 缺少：${required}`)
  }
}

const redirectsPath = path.join(frontendRoot, 'public', '_redirects')
if (fs.existsSync(redirectsPath)) {
  const redirects = fs.readFileSync(redirectsPath, 'utf8')
  if (!/^\/\*\s+\/index\.html\s+200\s*$/m.test(redirects)) {
    failures.push('frontend/public/_redirects 缺少 SPA 200 回退规则')
  }
}

const builtRedirectsPath = path.join(distRoot, '_redirects')
if (fs.existsSync(distRoot)) {
  requireFile(builtRedirectsPath, '构建产物中的 Netlify SPA 路由规则')
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
  `部署检查通过：${buildFiles.length} 个构建文本资源，Netlify、Render、SPA Rewrite、环境变量和本地路径均正常。`
)
