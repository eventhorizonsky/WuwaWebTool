<script setup lang="ts">
import { computed } from 'vue'
import type { CharacterEntry } from '@/types/character'
import { ATTRIBUTES, WEAPON_TYPES, getCompositeGrade } from '@/constants'
import { getResourceUrl, getAttrIcon } from '@/composables/useResources'
import { cacheGetScore } from '@/composables/useApi'

const props = defineProps<{
  character: CharacterEntry
  isActive: boolean
}>()

const ri = computed(() => props.character.role || props.character)
const cid = computed(() => String(ri.value.roleId || props.character.roleId || ''))
const name = computed(() => ri.value.roleName || '?')
const attr = computed(() => ATTRIBUTES[ri.value.attributeId || 0] || null)
const wt = computed(() => WEAPON_TYPES[ri.value.weaponTypeId || 0] || '')
const lv = computed(() => props.character.level || ri.value.level || '?')

const attrIcon = computed(() => (attr.value ? getAttrIcon(attr.value.name) : ''))
const attrColor = computed(() => attr.value?.color || '#666')

const cachedScore = computed(() => cacheGetScore(cid.value))
const gradeLabel = computed(() => {
  const s = cachedScore.value
  return s?.total_score != null ? getCompositeGrade(s.total_score) : null
})
const scoreDisplay = computed(() => {
  const s = cachedScore.value
  return s?.total_score != null ? s.total_score.toFixed(0) : null
})
</script>

<template>
  <div
    :class="[
      'char-list-item flex items-center gap-2.5 py-2 px-2.5 rounded-md border cursor-pointer transition-all bg-[var(--color-ink-1)]',
      isActive
        ? 'border-[#d4b163] bg-[rgba(212,177,99,0.08)]'
        : 'border-transparent hover:border-white/15 hover:bg-[var(--color-bg-card-hover)]'
    ]"
    @click="$emit('click')"
  >
    <img
      class="w-[42px] h-[42px] rounded-sm bg-black/30 flex-shrink-0 object-cover"
      :src="getResourceUrl('role_pile', 'role_pile_' + cid + '.png')"
      alt=""
      @error="(e) => (e.target as HTMLElement).style.display = 'none'"
    />
    <div class="flex-1 min-w-0">
      <div class="text-base font-semibold truncate">{{ name }}</div>
      <div class="text-[13px] text-[#9aa0aa] flex items-center gap-1">
        Lv.{{ lv }} · {{ wt }}
        <img
          v-if="attrIcon"
          :src="attrIcon"
          alt=""
          class="w-4 h-4"
        />
        <span :style="{ color: attrColor }">{{ attr?.name || '' }}</span>
      </div>
    </div>
    <div
      v-if="gradeLabel && scoreDisplay"
      class="font-[Oswald] text-lg font-bold flex-shrink-0 text-right leading-tight"
      :style="{ color: gradeLabel.color }"
    >
      {{ gradeLabel.label }}
      <small class="text-xs font-normal block text-[#9aa0aa]">{{ scoreDisplay }}</small>
    </div>
  </div>
</template>
