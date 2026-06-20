<script setup lang="ts">
defineProps<{
  message: string
  type: 'success' | 'error'
}>()
</script>

<template>
  <div :class="['toast', type === 'success' ? 'toast-success' : 'toast-error']">
    {{ message }}
  </div>
</template>
