<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import type { CharacterEntry } from '@/types/character'
import {
  ATTRIBUTES,
  WEAPON_TYPES,
  SKILL_ORDER,
  CHAIN_NAMES,
} from '@/constants'
import { getResourceUrl, getAttrIcon, getWeaponTypeIcon } from '@/composables/useResources'
import { loadCharDetailAndScore } from '@/composables/useApi'
import { useCharacterStore } from '@/stores/character'

const props = defineProps<{
  character: CharacterEntry
}>()

const router = useRouter()
const charStore = useCharacterStore()

const ri = computed(() => props.character.role || props.character)
const cid = computed(() => String(props.character.roleId || ri.value.roleId || ''))
const cn = computed(() => ri.value.roleName || '?')
const lv = computed(() => props.character.level || ri.value.level || '?')
const sl = computed(() => ri.value.starLevel || 5)
const attr = computed(() => ATTRIBUTES[ri.value.attributeId || 0] || { name: '?', color: '#666' })

const hasDetail = computed(() => props.character._detail != null)
const hasScore = computed(() => props.character._score != null)

const chain = computed(() => {
  const d = props.character._detail
  if (d?.chainList) {
    return d.chainList.filter((c) => c.unlocked).length
  }
  return props.character.chainUnlockNum ?? 0
})

const grade = computed(() => props.character._grade || { label: '-', color: '#666' })

const avatarUrl = computed(() => getResourceUrl('waves_avatar', 'role_head_' + cid.value + '.png'))
const attrIcon = computed(() => getAttrIcon(attr.value.name))
const starClass = computed(() => (sl.value >= 5 ? 'star-gold' : 'star-purple'))

const chainName = computed(() => CHAIN_NAMES[Math.min(chain.value, 6)] || '零链')
const chainColorClass = computed(() => `chain-c-${Math.min(chain.value, 6)}`)

// Weapon line
const weaponHtml = computed(() => {
  const d = props.character._detail
  if (hasDetail.value && d?.weaponData) {
    const wd = d.weaponData
    const w = wd.weapon
    return {
      icon: getResourceUrl('waves_weapon', 'weapon_' + w.weaponId + '.png'),
      name: w.weaponName,
      detail: `Lv.${wd.level}`,
      reson: `精${wd.resonLevel}`,
      hasDetail: true,
    }
  }
  const wtName = WEAPON_TYPES[ri.value.weaponTypeId || 0] || ''
  const wtIcon = wtName ? getWeaponTypeIcon(wtName) : ''
  return {
    icon: wtIcon,
    name: wtName,
    hasDetail: false,
  }
})

// Skills
const skills = computed(() => {
  const d = props.character._detail
  if (!hasDetail.value || !d?.skillList) return []
  const sorted = [...d.skillList].sort(
    (a, b) =>
      SKILL_ORDER.indexOf(a.skill?.type || '') -
      SKILL_ORDER.indexOf(b.skill?.type || '')
  )
  return sorted.slice(0, 5)
})

async function openPanel() {
  try {
    await loadCharDetailAndScore(cid.value, false)
    // Update entry in allChars
    const entry = charStore.allChars.find(
      (r) => String(r.roleId || r.role?.roleId || '') === cid.value
    )
    if (entry) {
      const { hydrateCharFromCache, cacheSet } = await import('@/composables/useApi')
      hydrateCharFromCache(entry)
      cacheSet('roleList', charStore.allChars)
    }
  } catch (e) {
    console.warn('Pre-load failed, will retry in panel:', e)
  }
  router.push({ name: 'panel', query: { charId: cid.value } })
}
</script>

<template>
  <div
    class="role-card"
    :data-rarity="sl >= 5 ? '5' : '4'"
    :title="cn + (hasScore ? ' — ' + grade.label : ' — 点击查看详情')"
    @click="openPanel"
  >
    <!-- Top: avatar + info -->
    <div class="flex gap-2.5 p-2.5 items-start">
      <!-- Avatar box -->
      <div class="w-[90px] h-[90px] flex-shrink-0 relative bg-black/30 rounded-lg overflow-hidden">
        <img
          :src="avatarUrl"
          :alt="cn"
          class="w-full h-full object-contain object-[center_40%] block bg-black/20"
          @error="($event.target as HTMLImageElement).style.background = '#222'"
        />
        <div class="absolute top-[3px] right-[3px] w-6 h-6 bg-black/50 rounded-full p-0.5 border border-white/15 backdrop-blur-[2px] z-[2]">
          <img :src="attrIcon" :alt="attr.name" class="w-full h-full block" @error="(e) => (e.target as HTMLElement).parentElement!.style.display='none'" />
        </div>
        <div class="absolute top-[3px] left-0 bg-gradient-to-r from-black/85 via-black/60 to-transparent px-1.5 py-px text-white font-[Oswald] text-[22px] font-black leading-tight z-[2] rounded-r-lg border-l-2 border-[#d4b163]" style="text-shadow:0 1px 2px black;">
          Lv.{{ lv }}
        </div>
      </div>

      <!-- Info -->
      <div class="flex-1 min-w-0 flex flex-col gap-[3px] relative">
        <div :class="['text-xs tracking-[0.5px]', starClass]">
          {{ '★'.repeat(Math.min(sl, 6)) }}
        </div>
        <div class="font-bold text-sm text-white truncate">{{ cn }}</div>
        <div :class="['text-xs font-bold whitespace-nowrap', chainColorClass]">
          {{ chainName }}
        </div>

        <!-- Weapon -->
        <div class="text-xs text-[#9aa0aa] flex items-center gap-[3px] whitespace-nowrap overflow-hidden truncate">
          <img
            v-if="weaponHtml.icon"
            :src="weaponHtml.icon"
            alt=""
            class="w-[18px] h-[18px] rounded-[3px] bg-black/30 flex-shrink-0"
            @error="(e) => (e.target as HTMLElement).style.display='none'"
          />
          <span>{{ weaponHtml.name }}</span>
          <template v-if="weaponHtml.hasDetail">
            <span>{{ weaponHtml.detail }}</span>
            <span class="text-[10px] text-[#d4b163] bg-[#d4b163]/10 px-1 rounded-[3px] border border-[#d4b163]/20 flex-shrink-0">
              {{ weaponHtml.reson }}
            </span>
          </template>
        </div>

        <!-- Score corner -->
        <div class="absolute top-0 right-0 text-right leading-none">
          <template v-if="hasScore">
            <div class="text-2xl font-black italic" :style="{ color: grade.color }">
              {{ grade.label }}
            </div>
            <div
              class="font-[Oswald] text-base font-black italic"
              :style="{ color: grade.color }"
            >
              {{ (character._score || 0) > 0 ? (character._score || 0).toFixed(0) : '--' }}
            </div>
          </template>
          <template v-else>
            <div class="text-lg" style="color: #555">--</div>
            <div class="font-['Microsoft_YaHei'] text-[10px] not-italic" style="color: #555; font-family: inherit;">
              点击加载
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- Bottom: skills -->
    <div class="px-2.5 pb-2.5 pt-1.5 border-t border-white/5 flex flex-col gap-1">
      <div class="flex gap-2 justify-center flex-wrap">
        <div
          v-for="(s, idx) in skills"
          :key="idx"
          class="text-center text-[10px] text-[#9aa0aa] w-10"
        >
          <img
            :src="s.skill?.iconUrl || ''"
            alt=""
            class="w-7 h-7 rounded-md bg-black/30 block mx-auto mb-px"
            @error="(e) => (e.target as HTMLElement).style.display='none'"
          />
          <span class="font-bold text-xs text-[#f3f3f3]">{{ s.level || 1 }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
