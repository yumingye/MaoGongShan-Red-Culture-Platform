import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const frontendRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const projectRoot = path.resolve(frontendRoot, '..')
const source = path.join(projectRoot, 'assets')
const publicRoot = path.join(frontendRoot, 'public')
const target = path.join(publicRoot, 'assets')

if (!fs.existsSync(source)) {
  throw new Error(`项目资源目录不存在：${source}`)
}

const expectedTarget = path.join(frontendRoot, 'public', 'assets')
if (path.resolve(target) !== path.resolve(expectedTarget)) {
  throw new Error(`拒绝同步到非预期目录：${target}`)
}

fs.mkdirSync(publicRoot, { recursive: true })
fs.rmSync(target, { recursive: true, force: true })
fs.cpSync(source, target, { recursive: true })

console.log(`静态资源已同步到 frontend/public/assets（${source} -> ${target}）`)
