<script setup lang="ts">
defineProps<{
  chainCount: number
}>()
</script>

<template>
  <div class="flex gap-1">
    <span
      v-for="i in 6"
      :key="i"
      :class="['chain-dot', { active: i <= chainCount }]"
    ></span>
  </div>
</template>
