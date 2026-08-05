import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  // 托管平台注入的环境变量优先于本地 .env 文件。
  const env = { ...loadEnv(mode, process.cwd(), ''), ...process.env }
  const proxyTarget = env.VITE_DEV_PROXY_TARGET || 'http://127.0.0.1:8000'
  const productionApi = String(env.VITE_API_BASE_URL || env.VITE_API_HOST || '').trim()

  if (mode === 'production') {
    if (!productionApi) {
      throw new Error('生产构建必须设置 VITE_API_BASE_URL，例如 https://your-api.onrender.com')
    }
    if (/https?:\/\/(?:localhost|127\.0\.0\.1)(?::\d+)?/i.test(productionApi)) {
      throw new Error('生产环境 VITE_API_BASE_URL 不能指向 localhost 或 127.0.0.1')
    }
  }

  return {
    plugins: [vue()],
    base: '/',
    build: {
      chunkSizeWarningLimit: 1200,
      rollupOptions: {
        output: {
          manualChunks(id) {
            if (!id.includes('node_modules')) return undefined
            if (id.includes('element-plus') || id.includes('@element-plus')) return 'element'
            if (id.includes('/axios/')) return 'axios'
            if (id.includes('/vue/') || id.includes('/@vue/') || id.includes('vue-router')) return 'vue'
            return undefined
          }
        }
      }
    },
    server: {
      host: env.VITE_DEV_HOST || '127.0.0.1',
      port: Number(env.VITE_DEV_PORT || 5173),
      proxy: {
        '/api': proxyTarget,
        '/static': proxyTarget
      }
    }
  }
})
