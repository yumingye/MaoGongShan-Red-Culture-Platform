<template>
  <article class="figure-card reveal" @click="$router.push(`/figures/${item.id}`)">
    <SafeImage :src="item.photo_url" :alt="item.name" />
    <div>
      <h3>{{ item.name }}</h3>
      <p class="mini-meta">{{ item.active_period || '公开资料所示时期' }}</p>
      <p class="subtle clamp">{{ item.biography }}</p>
      <div class="meta-line">
        <el-tag size="small" :type="item.verified ? 'success' : 'warning'">{{ item.verification_status || '公开资料' }}</el-tag>
        <el-tag size="small" type="info">查看详情</el-tag>
      </div>
    </div>
  </article>
</template>

<script setup>
import SafeImage from './SafeImage.vue'

defineProps({
  item: { type: Object, required: true }
})
</script>
