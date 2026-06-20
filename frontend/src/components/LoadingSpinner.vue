<script setup lang="ts">
defineProps<{
  message?: string
}>()
</script>

<template>
  <div class="loading-container">
    <div class="spinner"></div>
    <p>{{ message || '加载中...' }}</p>
  </div>
</template>
