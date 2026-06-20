<script setup lang="ts">
defineProps<{
  score: number | null
  grade: { label: string; color: string } | null
  showPlaceholder?: boolean
}>()
</script>

<template>
  <div v-if="score != null && grade" class="text-right leading-none">
    <div class="text-2xl font-black italic" :style="{ color: grade.color }">
      {{ grade.label }}
    </div>
    <div
      class="font-[Oswald] text-base font-black italic"
      :style="{ color: grade.color }"
    >
      {{ score > 0 ? score.toFixed(0) : '--' }}
    </div>
  </div>
  <div v-else-if="showPlaceholder" class="text-right leading-none">
    <div class="text-lg" style="color: #555">--</div>
    <div
      class="font-['Microsoft_YaHei'] text-[10px] not-italic"
      style="color: #555"
    >
      点击加载
    </div>
  </div>
</template>
