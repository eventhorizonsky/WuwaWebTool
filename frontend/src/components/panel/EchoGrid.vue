<script setup lang="ts">
import type { EchoData } from '@/types/character'
import type { EchoGradeData } from '@/types/scoring'
import EchoCard from './EchoCard.vue'

defineProps<{
  echoes: EchoData[]
  echoGrades: Record<number, EchoGradeData>
}>()
</script>

<template>
  <div v-if="echoes.length === 0" class="text-sm text-[#9aa0aa] text-center py-5">
    暂无装备声骸
  </div>
  <div v-else class="echo-grid">
    <EchoCard
      v-for="(echo, idx) in echoes"
      :key="idx"
      :echo="echo"
      :index="idx"
      :echo-grade="echoGrades[idx]"
    />
  </div>
</template>
