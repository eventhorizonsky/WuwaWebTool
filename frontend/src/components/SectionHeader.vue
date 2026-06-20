<script setup lang="ts">
defineProps<{
  title: string
}>()
</script>

<template>
  <div class="section-header">
    <span class="section-title">{{ title }}</span>
    <div class="section-deco-line"></div>
    <slot />
  </div>
</template>
