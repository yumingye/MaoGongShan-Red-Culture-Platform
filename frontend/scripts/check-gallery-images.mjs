import fs from 'node:fs'
import path from 'node:path'

const root = process.cwd()
const publicDir = path.join(root, 'public')
const fallback = path.join(publicDir, 'assets', 'images', 'fallback', 'fallback-real-scenery.jpg')
const apiBase = process.env.CHECK_API_BASE || 'http://127.0.0.1:8000'

function fail(message) {
  console.error(`FAIL ${message}`)
  process.exitCode = 1
}

function getImageSize(file) {
  const buffer = fs.readFileSync(file)
  const ext = path.extname(file).toLowerCase()
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
  if (ext === '.png' && buffer.toString('ascii', 1, 4) === 'PNG') {
    return { width: buffer.readUInt32BE(16), height: buffer.readUInt32BE(20) }
  }
  if (ext === '.gif' && buffer.toString('ascii', 0, 3) === 'GIF') {
    return { width: buffer.readUInt16LE(6), height: buffer.readUInt16LE(8) }
  }
  if (
    ext === '.webp' &&
    buffer.toString('ascii', 0, 4) === 'RIFF' &&
    buffer.toString('ascii', 8, 12) === 'WEBP'
  ) {
    let offset = 12
    while (offset + 8 <= buffer.length) {
      const chunk = buffer.toString('ascii', offset, offset + 4)
      const length = buffer.readUInt32LE(offset + 4)
      const data = offset + 8
      if (chunk === 'VP8X' && data + 10 <= buffer.length) {
        const width = 1 + buffer[data + 4] + (buffer[data + 5] << 8) + (buffer[data + 6] << 16)
        const height = 1 + buffer[data + 7] + (buffer[data + 8] << 8) + (buffer[data + 9] << 16)
        return { width, height }
      }
      if (chunk === 'VP8 ' && data + 10 <= buffer.length) {
        return {
          width: buffer.readUInt16LE(data + 6) & 0x3fff,
          height: buffer.readUInt16LE(data + 8) & 0x3fff
        }
      }
      if (chunk === 'VP8L' && data + 5 <= buffer.length && buffer[data] === 0x2f) {
        const bits = buffer.readUInt32LE(data + 1)
        return {
          width: (bits & 0x3fff) + 1,
          height: ((bits >> 14) & 0x3fff) + 1
        }
      }
      offset = data + length + (length % 2)
    }
  }
  return null
}

async function main() {
  if (!fs.existsSync(fallback)) fail('图库备用图片不存在')
  const fallbackSize = getImageSize(fallback)
  if (!fallbackSize || fallbackSize.width < 300 || fallbackSize.height < 200) {
    fail('图库备用图片尺寸不足，不能作为可靠兜底照片')
  }

  const response = await fetch(`${apiBase}/api/images`, { signal: AbortSignal.timeout(10000) })
  if (!response.ok) fail(`/api/images 返回 ${response.status}`)
  const rows = await response.json()
  if (!Array.isArray(rows) || rows.length < 100) fail(`图库记录数量不足：${Array.isArray(rows) ? rows.length : 0}`)

  for (const item of rows) {
    if (!item.image_url) {
      fail(`图库记录缺少 image_url：${item.id} ${item.title || ''}`)
      continue
    }
    if (item.image_url.startsWith('http') || item.image_url.startsWith('data:')) continue
    const file = path.join(publicDir, item.image_url.replace(/^\//, ''))
    if (!fs.existsSync(file)) {
      fail(`图库本地图片不存在：${item.id} ${item.image_url}`)
      continue
    }
    const size = getImageSize(file)
    if (!size || size.width < 120 || size.height < 120) {
      fail(`图库图片不可用或尺寸过小：${item.id} ${item.image_url}`)
    }
  }

  if (!process.exitCode) console.log(`图库图片检查通过：${rows.length} 条记录均有可显示照片。`)
}

main().catch((error) => {
  fail(`图库图片检查异常：${error.message}`)
})
