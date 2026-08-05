import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const manifestPath = path.join(root, 'src', 'data', 'maogongshanPhotos.json')
const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'))
const errors = []
const warnings = []
const ids = new Set()
const slugs = new Set()
const detailFiles = new Set()

function publicFile(url) {
  return path.join(root, 'public', url.replace(/^\/+/, '').split('/').join(path.sep))
}

function requireText(item, field) {
  if (!String(item[field] || '').trim()) errors.push(`${item.slug || '未知图片'} 缺少 ${field}`)
}

if (manifest.used_images < 40) errors.push(`使用图片数量不足：${manifest.used_images}`)
if (manifest.images.length !== manifest.used_images) {
  errors.push(`清单数量 ${manifest.images.length} 与 used_images ${manifest.used_images} 不一致`)
}

for (const item of manifest.images) {
  for (const field of ['id', 'slug', 'title', 'group', 'category', 'description', 'alt', 'source_name', 'copyright_note']) {
    requireText(item, field)
  }
  if (ids.has(item.id)) errors.push(`重复数据库 ID：${item.id}`)
  if (slugs.has(item.slug)) errors.push(`重复 slug：${item.slug}`)
  ids.add(item.id)
  slugs.add(item.slug)

  for (const field of ['thumbnail_url', 'detail_url', 'mobile_url']) {
    const target = publicFile(item[field])
    if (!fs.existsSync(target)) errors.push(`${item.slug} 缺少 ${field}: ${item[field]}`)
    if (fs.existsSync(target) && fs.statSync(target).size < 8_000) {
      warnings.push(`${item.slug} 的 ${field} 文件过小，建议人工检查`)
    }
  }
  if (detailFiles.has(item.detail_url)) errors.push(`详情图被重复登记：${item.detail_url}`)
  detailFiles.add(item.detail_url)
  if (item.hero_url && !fs.existsSync(publicFile(item.hero_url))) {
    errors.push(`${item.slug} 缺少首页横幅：${item.hero_url}`)
  }
}

for (const slug of manifest.hero_slugs) {
  const item = manifest.images.find((entry) => entry.slug === slug)
  if (!item) errors.push(`首页横幅引用未知 slug：${slug}`)
  else if (!item.hero_url) errors.push(`首页横幅 ${slug} 未配置 hero_url`)
}

if (warnings.length) {
  console.warn(`照片资源检查警告 ${warnings.length} 项：`)
  warnings.forEach((warning) => console.warn(`- ${warning}`))
}
if (errors.length) {
  console.error(`照片资源检查失败 ${errors.length} 项：`)
  errors.forEach((error) => console.error(`- ${error}`))
  process.exit(1)
}

console.log(
  `照片资源检查通过：${manifest.images.length} 张照片，` +
  `${manifest.hero_slugs.length} 张首页横幅，所有 WebP 变体均存在。`
)
