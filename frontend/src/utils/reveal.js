/** 用 IntersectionObserver 统一管理滚动出现动画，并兼容异步路由新增节点。 */
export function setupRevealObserver() {
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  if (reduceMotion || !('IntersectionObserver' in window)) {
    document.querySelectorAll('.reveal').forEach((element) => element.classList.add('is-visible'))
    return () => {}
  }

  const observed = new WeakSet()
  const safetyTimers = new Set()
  const observer = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue
      entry.target.classList.add('is-visible')
      observer.unobserve(entry.target)
    }
  }, { rootMargin: '0px 0px -7% 0px', threshold: 0.08 })

  function register(root = document) {
    const nodes = root.matches?.('.reveal') ? [root] : root.querySelectorAll?.('.reveal') || []
    for (const node of nodes) {
      if (observed.has(node)) continue
      observed.add(node)
      const rect = node.getBoundingClientRect()
      if (rect.top <= window.innerHeight * 1.05 && rect.bottom >= -40) {
        // 首屏内容同步显示，避免路由直达或弱网加载时出现短暂整页空白。
        node.classList.add('is-visible')
      } else {
        observer.observe(node)
      }
      // 动画绝不能成为内容可见性的单点故障。浏览器降速、异步路由或
      // IntersectionObserver 回调异常时，节点仍会在短暂过渡后强制显现。
      const timer = window.setTimeout(() => {
        node.classList.add('is-visible')
        observer.unobserve(node)
        safetyTimers.delete(timer)
      }, 900)
      safetyTimers.add(timer)
    }
  }

  const mutationObserver = new MutationObserver((records) => {
    for (const record of records) {
      for (const node of record.addedNodes) {
        if (node.nodeType === Node.ELEMENT_NODE) register(node)
      }
    }
  })

  register()
  mutationObserver.observe(document.body, { childList: true, subtree: true })
  return () => {
    observer.disconnect()
    mutationObserver.disconnect()
    for (const timer of safetyTimers) window.clearTimeout(timer)
    safetyTimers.clear()
  }
}
