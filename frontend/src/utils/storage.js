// 浏览器隐私模式、存储配额不足或损坏数据都不应导致页面崩溃。
export function readStorage(key, fallback) {
  try {
    const value = localStorage.getItem(key)
    return value === null ? fallback : JSON.parse(value)
  } catch {
    return fallback
  }
}

export function writeStorage(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value))
    return true
  } catch {
    return false
  }
}

export function removeStorage(key) {
  try { localStorage.removeItem(key); return true } catch { return false }
}
