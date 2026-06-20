<script setup lang="ts">
defineProps<{
  src: string
  size?: number
}>()
</script>

<template>
  <div
    class="avatar-container"
    :style="{ width: (size || 100) + 'px', height: (size || 100) + 'px' }"
  >
    <div class="avatar-ring"></div>
    <img
      :src="src"
      alt="Avatar"
      class="relative z-[1] h-full w-full rounded-full object-cover"
      @error="($event.target as HTMLImageElement).style.display = 'none'"
    />
  </div>
</template>
