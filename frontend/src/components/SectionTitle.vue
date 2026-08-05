<template>
  <div class="section-heading reveal">
    <p v-if="eyebrow">{{ eyebrow }}</p>
    <h2>{{ title }}</h2>
    <span v-if="desc">{{ desc }}</span>
  </div>
</template>

<script setup>
defineProps({
  eyebrow: { type: String, default: '' },
  title: { type: String, required: true },
  desc: { type: String, default: '' }
})
</script>
