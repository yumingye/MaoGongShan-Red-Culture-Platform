import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { pathToFileURL } from 'node:url'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const manifestPath = path.join(root, 'public', 'data', 'party-media-manifest.json')
const failures = []

function fail(message) { failures.push(message) }
function publicFile(url) { return path.join(root, 'public', String(url || '').replace(/^\//, '').replaceAll('/', path.sep)) }

if (!fs.existsSync(manifestPath)) fail('缺少党史媒体清单 public/data/party-media-manifest.json')
const manifest = fs.existsSync(manifestPath) ? JSON.parse(fs.readFileSync(manifestPath, 'utf8')) : { articles: [], media: [], figures: [] }
const mediaByArticle = new Map()
for (const media of manifest.media) {
  const rows = mediaByArticle.get(media.article_slug) || []
  rows.push(media)
  mediaByArticle.set(media.article_slug, rows)
  for (const field of ['media_key', 'article_slug', 'section_id', 'title', 'image_url', 'media_type', 'caption', 'alt', 'source_name', 'copyright_note', 'verification_status', 'fallback_image']) {
    if (!String(media[field] || '').trim()) fail(`媒体 ${media.media_key || '(无ID)'} 缺少 ${field}`)
  }
  if (!fs.existsSync(publicFile(media.image_url))) fail(`媒体文件不存在：${media.image_url}`)
  if (!fs.existsSync(publicFile(media.fallback_image))) fail(`备用图不存在：${media.fallback_image}`)
  if (/scenery|maogongshan-mountain|xifu-beauty/i.test(media.image_url)) fail(`党史媒体误用山景：${media.media_key} -> ${media.image_url}`)
  if (media.is_historical_photo && media.media_type !== '历史原始照片') fail(`非历史原照被标记为历史照片：${media.media_key}`)
  if (/图片1|历史照片$|红色配图/.test(media.caption)) fail(`图片说明过于笼统：${media.media_key}`)
}

for (const article of manifest.articles) {
  const rows = mediaByArticle.get(article.slug) || []
  if (!rows.length) fail(`文章没有章节媒体：${article.slug}`)
  if (!rows.some((item) => item.section_id === '内容导语')) fail(`文章缺少导语媒体：${article.slug}`)
  if (!String(article.image_note || '').trim()) fail(`文章封面说明为空：${article.slug}`)
  if (!fs.existsSync(publicFile(article.image))) fail(`文章封面不存在：${article.slug} -> ${article.image}`)
}

const photoUse = new Map()
for (const media of manifest.media.filter((item) => item.media_type !== '项目自制')) {
  const slugs = new Set(photoUse.get(media.image_url) || [])
  slugs.add(media.article_slug)
  photoUse.set(media.image_url, [...slugs])
}
for (const [image, slugs] of photoUse) {
  if (slugs.length > 2) fail(`同一真实照片关联过多不同专题：${image} -> ${slugs.join(', ')}`)
}

for (const figure of manifest.figures) {
  for (const field of ['name', 'photo_url', 'active_period', 'photo_note', 'photo_type', 'source_url', 'copyright_note', 'verification_status']) {
    if (!String(figure[field] || '').trim()) fail(`人物 ${figure.name || figure.id} 缺少 ${field}`)
  }
  if (!fs.existsSync(publicFile(figure.photo_url))) fail(`人物照片不存在：${figure.name} -> ${figure.photo_url}`)
  if (!['人物照片', '项目自制人物档案'].includes(figure.photo_type)) fail(`人物媒体类型不合规：${figure.name} -> ${figure.photo_type}`)
  if (figure.photo_type === '项目自制人物档案' && !figure.photo_note.includes('不是')) fail(`人物档案图解未明确说明不是本人照片：${figure.name}`)
}

const { videoLessons } = await import(pathToFileURL(path.join(root, 'src', 'data', 'experienceContent.js')).href)
for (const lesson of videoLessons) {
  if (lesson.frames.length < 3) fail(`图文微课画面少于3幅：${lesson.slug}`)
  if (lesson.frames.length !== lesson.frameCaptions.length || lesson.frames.length !== lesson.frameTypes.length) fail(`图文微课画面、说明和类型数量不一致：${lesson.slug}`)
  if (new Set(lesson.frames).size !== lesson.frames.length) fail(`同一图文微课重复使用画面：${lesson.slug}`)
  lesson.frames.forEach((frame, index) => {
    if (!fs.existsSync(publicFile(frame))) fail(`图文微课画面不存在：${lesson.slug} -> ${frame}`)
    if (!String(lesson.frameCaptions[index] || '').trim()) fail(`图文微课画面说明为空：${lesson.slug} 第${index + 1}幅`)
    if (!String(lesson.frameTypes[index] || '').trim()) fail(`图文微课媒体类型为空：${lesson.slug} 第${index + 1}幅`)
  })
}

const { historyStages } = await import(pathToFileURL(path.join(root, 'src', 'data', 'historyStages.js')).href)
for (const stage of historyStages) {
  if (!fs.existsSync(publicFile(stage.cover))) fail(`党史阶段图不存在：${stage.slug} -> ${stage.cover}`)
  if (stage.coverType !== '项目自制') fail(`党史阶段图类型未标明为项目自制：${stage.slug}`)
  if (!String(stage.coverNote || '').includes('不是历史现场照片')) fail(`党史阶段图说明未区分历史现场：${stage.slug}`)
}

if (failures.length) {
  console.error(`党史图文一致性检查失败，共 ${failures.length} 项：`)
  failures.forEach((item) => console.error(`- ${item}`))
  process.exit(1)
}

console.log(`党史图文一致性检查通过：${manifest.articles.length} 篇文章、${manifest.media.length} 条章节媒体、${manifest.figures.length} 份人物档案、${historyStages.length} 个阶段、${videoLessons.length} 个图文微课。`)
