<template>
  <section class="page-hero" :style="heroStyle">
    <div class="page-hero-content reveal">
      <p class="eyebrow">{{ eyebrow }}</p>
      <h1>{{ title }}</h1>
      <p>{{ subtitle }}</p>
      <slot />
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  eyebrow: { type: String, default: '红色文化数字资源' },
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  image: { type: String, default: '/assets/images/scenery/maogongshan-mountain.jpg' }
})

const heroStyle = computed(() => ({
  backgroundImage: [
    'linear-gradient(105deg, rgba(62, 9, 13, .9), rgba(143, 29, 34, .72), rgba(28, 31, 29, .25))',
    `url(${props.image})`,
    "url('/assets/images/fallback/fallback-real-scenery.jpg')"
  ].join(', ')
}))
</script>
