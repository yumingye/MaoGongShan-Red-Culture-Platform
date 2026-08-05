<template>
  <StructuredDetail
    api="/api/achievements"
    detail-prefix="/achievements"
    list-path="/achievements"
    list-name="实践成果"
    item-type="实践成果"
    favorite-type="achievement"
  />
</template>

<script setup>
import StructuredDetail from '../components/StructuredDetail.vue'
</script>
