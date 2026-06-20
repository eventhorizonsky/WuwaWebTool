<script setup lang="ts">
import { computed } from 'vue'
import type { CharacterDetail } from '@/types/character'
import type { EchoGradeData } from '@/types/scoring'
import SonataTooltip from './SonataTooltip.vue'
import EchoGrid from './EchoGrid.vue'

const props = defineProps<{
  roleDetail: CharacterDetail
  echoGrades: Record<number, EchoGradeData>
}>()

const phantomData = computed(() => props.roleDetail.phantomData)
const echoes = computed(() => phantomData.value?.equipPhantomList || [])
const totalCost = computed(() => phantomData.value?.cost || 0)

const firstEcho = computed(() => echoes.value[0])
</script>

<template>
  <div class="echoes-card flex-1 min-w-0 bg-[var(--color-ink-1)] border border-[var(--color-line)] rounded-[var(--radius-card)] px-3 py-2 flex flex-col min-h-0">
    <div class="flex items-center gap-2 mb-1 pb-1 border-b border-[var(--color-line)] flex-shrink-0">
      <span class="text-sm font-bold text-[#d4b163] uppercase tracking-[0.5px] whitespace-nowrap">
        装备声骸
      </span>
      <SonataTooltip
        v-if="firstEcho?.fetterDetail"
        :fetter-detail="firstEcho.fetterDetail"
      />
      <span class="text-xs text-[#9aa0aa] ml-auto">COST {{ totalCost }}</span>
      <div class="w-5 h-px" style="background: linear-gradient(90deg, rgba(212,177,99,0.35), transparent);"></div>
    </div>
    <EchoGrid
      :echoes="echoes"
      :echo-grades="echoGrades"
    />
  </div>
</template>
