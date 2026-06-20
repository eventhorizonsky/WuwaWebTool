<script setup lang="ts">
import { computed, ref } from 'vue'
import type { WeaponData } from '@/types/character'
import { getResourceUrl } from '@/composables/useResources'

const props = defineProps<{
  weaponData: WeaponData | null
}>()

const expanded = ref(false)
</script>

<template>
  <div class="info-card flex-1 min-w-0 bg-[var(--color-ink-1)] border border-[var(--color-line)] rounded-[var(--radius-card)] p-3 overflow-y-auto">
    <div class="ic-title text-sm font-bold text-[#d4b163] uppercase tracking-[0.5px] pb-[5px] mb-1.5 border-b border-[var(--color-line)] flex items-center gap-1.5 flex-shrink-0">
      武器
      <div class="flex-1 h-px" style="background: linear-gradient(90deg, var(--color-line), transparent);"></div>
    </div>

    <div v-if="!weaponData" class="empty-hint text-sm text-[#9aa0aa] text-center py-5">
      暂无武器
    </div>
    <template v-else>
      <div class="weapon-row">
        <img
          :src="getResourceUrl('waves_weapon', 'weapon_' + (weaponData.weapon.weaponId || '') + '.png')"
          alt=""
          @error="(e) => (e.target as HTMLElement).style.display = 'none'"
        />
        <div class="flex-1 min-w-0">
          <div class="font-semibold text-base">
            {{ weaponData.weapon.weaponName || '武器' }} ⭐{{ weaponData.weapon.weaponStarLevel || 1 }}
          </div>
          <div class="text-sm text-[#9aa0aa]">
            Lv.{{ weaponData.level || 1 }} / 精{{ weaponData.resonLevel || 1 }}
          </div>
          <!-- Main stats -->
          <div v-if="weaponData.mainPropList?.length" class="mt-1 flex gap-3 text-sm">
            <span
              v-for="(s, i) in weaponData.mainPropList"
              :key="i"
              class="text-[#9aa0aa]"
            >
              {{ s.attributeName }}: <span class="font-semibold text-[#e8edf2]">{{ s.attributeValue }}</span>
            </span>
          </div>
          <!-- Passive effect -->
          <div
            v-if="weaponData.weapon.effectDescription"
            :class="['weapon-passive', { expanded }]"
            :title="expanded ? '' : '点击展开/收起'"
            @click="expanded = !expanded"
          >
            <template v-if="weaponData.weapon.weaponEffectName">
              【{{ weaponData.weapon.weaponEffectName }}】
            </template>
            {{ weaponData.weapon.effectDescription }}
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
