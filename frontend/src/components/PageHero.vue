<template>
  <section class="page-hero">
    <picture class="page-hero-media" aria-hidden="true">
      <source v-if="mobileImage" :srcset="mobileImage" media="(max-width: 640px)" />
      <img :src="image" alt="" loading="eager" fetchpriority="high" decoding="async" />
    </picture>
    <div class="page-hero-shade"></div>
    <div class="page-hero-content reveal">
      <p class="eyebrow">{{ eyebrow }}</p>
      <h1>{{ title }}</h1>
      <p>{{ subtitle }}</p>
      <slot />
    </div>
  </section>
</template>

<script setup>
const props = defineProps({
  eyebrow: { type: String, default: '红色文化数字资源' },
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  image: { type: String, default: '/assets/images/scenery/maogongshan-mountain.jpg' },
  mobileImage: { type: String, default: '' }
})
</script>
