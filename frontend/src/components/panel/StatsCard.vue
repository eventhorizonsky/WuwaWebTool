<script setup lang="ts">
import { computed } from 'vue'
import type { AttributeItem } from '@/types/character'

const props = defineProps<{
  attributeList: AttributeItem[]
  bonusProps: AttributeItem[]
}>()

const coreKeys = ['生命', '攻击', '防御', '暴击', '暴击伤害', '共鸣效率']

const coreStats = computed(() =>
  props.attributeList.filter((s) => coreKeys.includes(s.attributeName))
)

const otherStats = computed(() =>
  props.attributeList.filter((s) => !coreKeys.includes(s.attributeName))
)
</script>

<template>
  <div class="info-card flex-1 min-w-0 bg-[var(--color-ink-1)] border border-[var(--color-line)] rounded-[var(--radius-card)] p-3 overflow-y-auto">
    <div class="ic-title text-sm font-bold text-[#d4b163] uppercase tracking-[0.5px] pb-[5px] mb-1.5 border-b border-[var(--color-line)] flex items-center gap-1.5 flex-shrink-0">
      属性
      <div class="flex-1 h-px" style="background: linear-gradient(90deg, var(--color-line), transparent);"></div>
    </div>

    <div v-if="!attributeList.length" class="text-sm text-[#9aa0aa] text-center py-5">
      暂无属性
    </div>

    <div v-else class="flex flex-col gap-px">
      <!-- Core stats -->
      <div
        v-for="(s, i) in coreStats"
        :key="'core-' + i"
        class="flex justify-between items-center py-0.5 text-sm"
      >
        <span class="text-[#9aa0aa] flex items-center gap-1">
          <img
            v-if="s.iconUrl"
            :src="s.iconUrl"
            alt=""
            class="w-[18px] h-[18px] flex-shrink-0"
            @error="(e) => (e.target as HTMLElement).style.display = 'none'"
          />
          {{ s.attributeName }}
        </span>
        <span class="font-semibold text-[#e8edf2]">{{ s.attributeValue }}</span>
      </div>

      <!-- Other stats divider -->
      <template v-if="otherStats.length">
        <div class="pt-1.5 mt-1 border-t border-white/5">
          <span class="text-xs font-bold uppercase tracking-[0.3px] text-[rgba(212,177,99,0.6)]">
            其他加成
          </span>
        </div>
        <div
          v-for="(s, i) in otherStats"
          :key="'other-' + i"
          class="flex justify-between items-center py-0.5 text-sm"
        >
          <span class="text-[#9aa0aa] flex items-center gap-1">
            <img
              v-if="s.iconUrl"
              :src="s.iconUrl"
              alt=""
              class="w-[18px] h-[18px] flex-shrink-0"
              @error="(e) => (e.target as HTMLElement).style.display = 'none'"
            />
            {{ s.attributeName }}
          </span>
          <span class="font-semibold text-[#e8edf2]">{{ s.attributeValue }}</span>
        </div>
      </template>
    </div>
  </div>
</template>
