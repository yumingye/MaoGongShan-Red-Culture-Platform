<template>
  <article class="history-card reveal">
    <SafeImage :src="item.image_url" :alt="item.title" />
    <div class="history-card-body">
      <div class="meta-line">
        <el-tag type="danger">{{ item.category || '历史事件' }}</el-tag>
        <el-tag :type="item.verified ? 'success' : 'warning'">{{ item.verification_status || (item.verified ? '已考证' : '待考证') }}</el-tag>
      </div>
      <h3>{{ item.title }}</h3>
      <p class="mini-meta">{{ item.event_time }} · {{ item.location }}</p>
      <p class="subtle clamp">{{ item.summary }}</p>
      <el-button type="primary" plain @click="$router.push(`/events/${item.id}`)">查看详情</el-button>
    </div>
  </article>
</template>

<script setup>
import SafeImage from './SafeImage.vue'

defineProps({
  item: { type: Object, required: true }
})
</script>
