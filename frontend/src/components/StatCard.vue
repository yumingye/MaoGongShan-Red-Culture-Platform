<template>
  <article class="stat-card reveal">
    <div class="stat-icon">
      <el-icon><component :is="icon" /></el-icon>
    </div>
    <div>
      <strong>{{ displayValue }}</strong>
      <span>{{ label }}</span>
    </div>
  </article>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'

const props = defineProps({
  label: { type: String, required: true },
  value: { type: Number, default: 0 },
  icon: { type: String, default: 'DataLine' }
})

const displayValue = ref(0)

function animate() {
  const target = Number(props.value || 0)
  const start = displayValue.value
  const startTime = performance.now()
  const duration = 750
  function step(time) {
    const progress = Math.min((time - startTime) / duration, 1)
    displayValue.value = Math.round(start + (target - start) * progress)
    if (progress < 1) requestAnimationFrame(step)
  }
  requestAnimationFrame(step)
}

onMounted(animate)
watch(() => props.value, animate)
</script>
