<script setup lang="ts">
import type { CharacterDetail } from '@/types/character'
import type { ScoreData, EchoGradeData } from '@/types/scoring'
import IdentityCard from './IdentityCard.vue'
import EchoesCard from './EchoesCard.vue'

defineProps<{
  roleDetail: CharacterDetail
  scoreData: ScoreData | null
  echoGrades: Record<number, EchoGradeData>
  charId: string
}>()

const emit = defineEmits<{
  refresh: []
}>()
</script>

<template>
  <div class="panel-top-row">
    <IdentityCard
      :role-detail="roleDetail"
      :score-data="scoreData"
      :char-id="charId"
      @refresh="emit('refresh')"
    />
    <EchoesCard
      :role-detail="roleDetail"
      :echo-grades="echoGrades"
    />
  </div>
</template>
