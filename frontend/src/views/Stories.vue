<template>
  <CollectionPage
    title="红色故事"
    subtitle="集中展示毛公山、城阳红色文化和青年实践中的故事化资料。"
    hero="/assets/images/generated/history-archive-v2-wide.webp"
    api="/api/red-stories"
    detail-prefix="/stories"
    item-type="红色故事"
  />
</template>

<script setup>
import CollectionPage from '../components/CollectionPage.vue'
</script>
