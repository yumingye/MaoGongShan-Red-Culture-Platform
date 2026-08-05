import axios from 'axios'

const responseCache = new Map()
const CACHE_PREFIX = 'mgs-api-cache:'
const MAX_CACHE_BYTES = 350000
const configuredApi = (
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_API_HOST ||
  ''
).trim().replace(/\/+$/, '')

// Render 的 fromService.host 只提供主机名，生产构建时自动补全 HTTPS。
export const API_BASE_URL = configuredApi && !/^https?:\/\//i.test(configuredApi)
  ? `https://${configuredApi}`
  : configuredApi

export const http = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000
})

http.interceptors.request.use((config) => {
  let token = ''
  try { token = localStorage.getItem('admin_token') || '' } catch { token = '' }
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  if (config.method === 'get') {
    const params = new URLSearchParams(config.params || {}).toString()
    config.__cacheKey = `${config.url || ''}${params ? `?${params}` : ''}`
  }
  return config
})

http.interceptors.response.use(
  (response) => {
    const key = response.config?.__cacheKey
    if (key && response.status >= 200 && response.status < 300) {
      responseCache.set(key, response.data)
      try {
        const serialized = JSON.stringify(response.data)
        if (serialized.length <= MAX_CACHE_BYTES) {
          sessionStorage.setItem(`${CACHE_PREFIX}${key}`, serialized)
        }
      } catch {
        // 浏览器禁用存储或数据过大时，仅保留内存缓存。
      }
    }
    return response
  },
  async (error) => {
    const config = error.config || {}
    const retryable = config.method === 'get' && !config.__retried && (!error.response || error.response.status >= 500)
    if (retryable) {
      config.__retried = true
      await new Promise((resolve) => window.setTimeout(resolve, 350))
      try {
        return await http(config)
      } catch (retryError) {
        error = retryError
      }
    }

    const key = config.__cacheKey
    if (key) {
      let cached = responseCache.get(key)
      if (cached === undefined) {
        try {
          const stored = sessionStorage.getItem(`${CACHE_PREFIX}${key}`)
          if (stored) cached = JSON.parse(stored)
        } catch {
          cached = undefined
        }
      }
      if (cached !== undefined) {
        return {
          data: cached,
          status: 200,
          statusText: 'Offline cache',
          headers: {},
          config,
          request: null,
          fromCache: true
        }
      }
    }
    return Promise.reject(error)
  }
)

export const FALLBACK_IMAGE = '/assets/images/fallback/fallback-real-scenery.jpg'
export const FALLBACK_IMAGES = Object.freeze({
  scenery: '/assets/images/scenery/summit-terrace-panorama-detail.webp',
  culture: '/assets/images/red-culture/exhibition-calligraphy-detail.webp',
  research: '/assets/images/research/research-history-gallery-a-detail.webp',
  team: '/assets/images/team/team-platform-group-detail.webp',
  people: '/assets/images/people/figure-profile-display-a-detail.webp',
  news: '/assets/images/research/research-biography-display-detail.webp',
  default: FALLBACK_IMAGE
})

export function assetUrl(url) {
  if (!url) return FALLBACK_IMAGE
  if (url.startsWith('http') || url.startsWith('data:')) return url
  if (url.startsWith('/static/') && API_BASE_URL) return `${API_BASE_URL}${url}`
  return url
}

export function imageFallback(event, fallback = FALLBACK_IMAGE) {
  if (!event?.target) return
  event.target.onerror = null
  event.target.src = fallback
}

export function normalizeListResponse(data) {
  if (Array.isArray(data)) return { items: data, total: data.length }
  if (!data || typeof data !== 'object') return { items: [], total: 0 }
  return {
    ...data,
    items: Array.isArray(data.items) ? data.items : [],
    total: Number.isFinite(Number(data.total)) ? Number(data.total) : 0
  }
}
