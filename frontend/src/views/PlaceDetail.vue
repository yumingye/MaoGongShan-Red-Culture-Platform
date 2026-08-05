<template>
  <StructuredDetail
    api="/api/places"
    detail-prefix="/places"
    list-path="/places"
    list-name="地点资源"
    item-type="地点资源"
    favorite-type="place"
  />
</template>

<script setup>
import StructuredDetail from '../components/StructuredDetail.vue'
</script>
