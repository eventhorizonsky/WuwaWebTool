<script setup lang="ts">
import { computed } from 'vue'
import type { EchoData } from '@/types/character'
import type { EchoGradeData } from '@/types/scoring'
import { getEchoGrade } from '@/constants'
import { getResourceUrl, getTextureUrl, getAttrEffectIcon } from '@/composables/useResources'

const props = defineProps<{
  echo: EchoData
  index: number
  echoGrade: EchoGradeData | undefined
}>()

const pp = computed(() => props.echo.phantomProp)
const icon = computed(() => getResourceUrl('phantom', 'phantom_' + (pp.value?.phantomId || '') + '.png'))
const grade = computed(() => props.echoGrade?.grade || 'c')
const score = computed(() => props.echoGrade?.score)

const gradeInfo = computed(() => {
  if (score.value != null) return getEchoGrade(score.value)
  return { color: '#6b8e6e' }
})

const fetterIcon = computed(() => {
  if (props.echo.fetterDetail) return getAttrEffectIcon(props.echo.fetterDetail.name)
  return ''
})

const mainProps = computed(() => props.echo.mainProps || [])
const subProps = computed(() => props.echo.subProps || [])

const subScores = computed(() => props.echoGrade?.substat_scores || [])

function getStatIcon(name: string) {
  return getTextureUrl('attribute_prop', 'attr_prop_' + name + '.png')
}

const promoteIcon = '/assets/textures/texture2d/promote_icon.png'
</script>

<template>
  <div class="echo-card" :id="'echo-' + index">
    <!-- Grade bar -->
    <div :class="['ech-bar', 'grade-' + grade]"></div>

    <!-- Grade tag -->
    <div
      class="ech-grade-tag text-white"
      :style="{ background: gradeInfo.color }"
    >
      {{ grade.toUpperCase() }}
    </div>

    <!-- Body -->
    <div class="flex-1 flex flex-col px-[4%] pt-[3%] pb-[4%] min-h-0">
      <!-- Top row: icon + name -->
      <div class="flex items-start gap-[3%] mb-[2%]">
        <div class="relative w-[26%] flex-shrink-0 aspect-square rounded-[3px] overflow-hidden bg-black/40">
          <img
            class="w-full h-full object-cover"
            :src="icon"
            alt=""
            @error="(e) => (e.target as HTMLElement).style.display = 'none'"
          />
          <img
            v-if="fetterIcon"
            class="absolute right-0 bottom-0 w-[42%] h-[42%] object-contain bg-black/50 rounded-tl-sm"
            :src="fetterIcon"
            alt=""
          />
        </div>

        <div class="flex-1 min-w-0 flex flex-col gap-0.5">
          <span class="text-[#eab704] font-bold truncate leading-tight" style="font-size: clamp(10px, 5.4cqw, 18px);">
            {{ pp?.name || '声骸' }}
          </span>
          <div class="flex items-center gap-[3%] flex-wrap">
            <span class="inline-flex items-center px-1.5 rounded-full text-xs font-semibold whitespace-nowrap leading-relaxed bg-white/10 text-[#ccc]" style="font-size: clamp(8px, 4.2cqw, 14px);">
              Lv.{{ echo.level || '?' }}
            </span>
            <span class="inline-flex items-center px-1.5 rounded-full text-xs font-bold whitespace-nowrap leading-relaxed bg-[rgba(186,55,42,0.7)] text-white" style="font-size: clamp(8px, 4.2cqw, 14px);">
              {{ score != null ? score.toFixed(1) + '分' : '--' }}
            </span>
          </div>
        </div>
      </div>

      <!-- COST stars -->
      <div class="flex gap-px mb-[1.5%]">
        <img
          v-for="_ in (echo.cost || 0)"
          :key="'star-' + _"
          class="ech-star opacity-75"
          style="width: clamp(12px, 7cqw, 24px);"
          :src="promoteIcon"
          alt=""
        />
      </div>

      <!-- Divider -->
      <div class="h-px bg-white/5 mb-[2%] flex-shrink-0"></div>

      <!-- Stats -->
      <div class="flex-1 flex flex-col gap-px min-h-0">
        <!-- Main props -->
        <template v-for="(s, i) in mainProps" :key="'main-' + i">
          <div class="flex items-center gap-[2%] flex-1 min-h-0">
            <img
              class="flex-shrink-0 opacity-85"
              style="width: clamp(16px, 10cqw, 32px);"
              :src="getStatIcon(s.attributeName)"
              alt=""
              @error="(e) => (e.target as HTMLElement).style.display = 'none'"
            />
            <span class="flex-1 truncate text-white" style="font-size: clamp(8px, 4.2cqw, 15px);">
              {{ s.attributeName }}
            </span>
            <span class="font-semibold whitespace-nowrap flex-shrink-0 text-white" style="font-size: clamp(8px, 4.2cqw, 15px);">
              {{ s.attributeValue }}
            </span>
          </div>
        </template>

        <!-- Divider between main and sub -->
        <div v-if="mainProps.length && subProps.length" class="h-px bg-white/10 my-px flex-shrink-0"></div>

        <!-- Sub props -->
        <template v-for="(s, i) in subProps" :key="'sub-' + i">
          <div class="flex items-center gap-[2%] flex-1 min-h-0">
            <img
              class="flex-shrink-0 opacity-85"
              style="width: clamp(16px, 10cqw, 32px);"
              :src="getStatIcon(s.attributeName)"
              alt=""
              @error="(e) => (e.target as HTMLElement).style.display = 'none'"
            />
            <span
              class="flex-1 truncate"
              style="font-size: clamp(8px, 4.2cqw, 15px);"
              :style="{ color: subScores[mainProps.length + i]?.name_color || '#ffffff' }"
            >
              {{ s.attributeName }}
            </span>
            <span
              class="font-semibold whitespace-nowrap flex-shrink-0"
              style="font-size: clamp(8px, 4.2cqw, 15px);"
              :style="{ color: subScores[mainProps.length + i]?.num_color || '#ffffff' }"
            >
              {{ s.attributeValue }}
            </span>
            <span
              class="font-semibold whitespace-nowrap flex-shrink-0 ml-auto opacity-80 text-right min-w-[1.2em]"
              style="font-size: clamp(6px, 2.8cqw, 11px);"
              :style="{ color: (subScores[mainProps.length + i]?.score || 0) > 0 ? '#3598db' : '#95a5a6' }"
            >
              {{ subScores[mainProps.length + i]?.score || 0 }}
            </span>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>
