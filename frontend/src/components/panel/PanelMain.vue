<script setup lang="ts">
import type { CharacterDetail } from '@/types/character'
import type { ScoreData, EchoGradeData } from '@/types/scoring'
import PanelTopRow from './PanelTopRow.vue'
import PanelBottomRow from './PanelBottomRow.vue'

defineProps<{
  roleDetail: CharacterDetail | null
  scoreData: ScoreData | null
  echoGrades: Record<number, EchoGradeData>
  charId: string
}>()

const emit = defineEmits<{
  refresh: []
}>()
</script>

<template>
  <div class="panel-main">
    <div v-if="!roleDetail" class="text-center py-15 text-[#9aa0aa]">
      <div class="spinner mb-2"></div>
    </div>
    <template v-else>
      <PanelTopRow
        :role-detail="roleDetail"
        :score-data="scoreData"
        :echo-grades="echoGrades"
        :char-id="charId"
        @refresh="emit('refresh')"
      />
      <PanelBottomRow :role-detail="roleDetail" />
    </template>
  </div>
</template>
