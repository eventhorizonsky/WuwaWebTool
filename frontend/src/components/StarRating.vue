<script setup lang="ts">
defineProps<{
  starLevel: number
}>()
</script>

<template>
  <span
    :class="starLevel >= 5 ? 'star-gold' : 'star-purple'"
    class="text-xs tracking-[0.5px]"
  >
    {{ '★'.repeat(Math.min(starLevel, 6)) }}
  </span>
</template>
