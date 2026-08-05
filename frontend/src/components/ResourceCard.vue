<template>
  <article class="resource-card reveal">
    <div class="resource-icon">
      <el-icon><component :is="iconName" /></el-icon>
    </div>
    <div>
      <el-tag type="danger" effect="plain">{{ item.type }}</el-tag>
      <h3>{{ item.name }}</h3>
      <p class="subtle clamp">{{ item.summary }}</p>
      <p class="mini-meta">来源：{{ item.source }} · 发布时间：{{ item.uploaded_at }}</p>
      <div class="tag-row">
        <span v-for="tag in tagList" :key="tag">{{ tag }}</span>
      </div>
      <el-button type="primary" plain @click="$router.push(`/resources/${item.id}`)">查看详情</el-button>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({
  item: { type: Object, required: true }
})

const iconMap = {
  历史文献: 'Document',
  图片资料: 'Picture',
  视频资料: 'VideoCamera',
  新闻报道: 'Reading',
  研究文章: 'EditPen',
  口述历史: 'Microphone',
  音频资料: 'Headset'
}

const iconName = computed(() => iconMap[props.item.type] || 'Collection')
const tagList = computed(() => String(props.item.tags || '').split(',').filter(Boolean))
</script>
