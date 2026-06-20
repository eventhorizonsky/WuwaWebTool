<script setup lang="ts">
import { computed } from 'vue'
import type { CharacterDetail } from '@/types/character'
import type { ScoreData } from '@/types/scoring'
import { ATTRIBUTES, WEAPON_TYPES, getCompositeGrade } from '@/constants'
import { getResourceUrl, getAttrIcon, getWeaponTypeIcon } from '@/composables/useResources'
import ChainDots from '@/components/ChainDots.vue'
import StarRating from '@/components/StarRating.vue'

const props = defineProps<{
  roleDetail: CharacterDetail
  scoreData: ScoreData | null
  charId: string
}>()

defineEmits<{
  refresh: []
}>()

const ri = computed(() => props.roleDetail.role || props.roleDetail)
const attr = computed(() => ATTRIBUTES[ri.value.attributeId || 0] || { name: '?', color: '#666' })
const wt = computed(() => WEAPON_TYPES[ri.value.weaponTypeId || 0] || '?')
const cn = computed(() => ri.value.roleName || '?')
const lv = computed(() => props.roleDetail.level || ri.value.level || '?')
const sl = computed(() => ri.value.starLevel || 5)
const chain = computed(() =>
  props.roleDetail.chainList
    ? props.roleDetail.chainList.filter((c) => c.unlocked).length
    : ri.value.chain || 0
)

const gradeInfo = computed(() =>
  props.scoreData?.total_score != null
    ? getCompositeGrade(props.scoreData.total_score)
    : null
)

const skin = computed(() => props.roleDetail.roleSkin)
</script>

<template>
  <div class="identity-card">
    <img
      class="max-w-full max-h-[200px] object-contain object-[center_25%] rounded-lg bg-black/20 mb-1.5"
      :src="getResourceUrl('role_pile', 'role_pile_' + charId + '.png')"
      alt=""
      @error="(e) => (e.target as HTMLElement).style.display = 'none'"
    />

    <div class="flex items-baseline gap-2 flex-wrap justify-center">
      <span class="text-[1.4rem] font-bold text-[#e8edf2]">{{ cn }}</span>
      <span
        v-if="gradeInfo"
        class="font-[Oswald] text-lg font-bold"
        :style="{ color: gradeInfo.color }"
      >
        {{ gradeInfo.label }} · {{ (scoreData?.total_score || 0).toFixed(2) }}
      </span>
    </div>

    <div class="text-sm text-[#9aa0aa] flex items-center justify-center gap-1 mt-1">
      <img :src="getWeaponTypeIcon(wt)" alt="" class="w-[18px] h-[18px]" @error="(e) => (e.target as HTMLElement).style.display='none'" />
      {{ wt }} ·
      <span :style="{ color: attr.color }">
        <img :src="getAttrIcon(attr.name)" alt="" class="w-[18px] h-[18px] inline" @error="(e) => (e.target as HTMLElement).style.display='none'" />
        {{ attr.name }}
      </span>
    </div>

    <div class="text-sm text-[#9aa0aa] mt-0.5">
      Lv.{{ lv }} {{ '⭐'.repeat(Math.min(sl, 5)) }}
    </div>

    <div class="flex items-center justify-center gap-1 mt-[3px]">
      <ChainDots :chain-count="chain" />
      <span class="text-xs text-[#9aa0aa] ml-1">共鸣链 {{ chain }}/6</span>
    </div>

    <!-- Skin -->
    <div v-if="skin" class="inline-flex items-center gap-1 text-xs text-[#9aa0aa] mt-[3px]">
      <img :src="skin.skinIcon || ''" alt="" class="w-[18px] h-[18px] rounded-sm" @error="(e) => (e.target as HTMLElement).style.display='none'" />
      {{ skin.skinName || skin.qualityName || '' }}
    </div>

    <button class="btn-refresh-char" @click="$emit('refresh')">
      🔄 刷新角色
    </button>
  </div>
</template>
