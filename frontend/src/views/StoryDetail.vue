<template>
  <StructuredDetail
    api="/api/red-stories"
    detail-prefix="/stories"
    list-path="/stories"
    list-name="红色故事"
    item-type="红色故事"
    favorite-type="story"
  />
</template>

<script setup>
import StructuredDetail from '../components/StructuredDetail.vue'
</script>
