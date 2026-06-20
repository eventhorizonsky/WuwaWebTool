<script setup lang="ts">
import { useCharacterStore } from '@/stores/character'
import RoleGrid from './RoleGrid.vue'

const charStore = useCharacterStore()
</script>

<template>
  <div class="section-container page-main flex flex-col flex-1 min-h-0">
    <div class="section-header">
      <span class="section-title">共鸣者</span>
      <div class="section-deco-line"></div>
      <div class="flex gap-2 items-center ml-auto flex-shrink-0 flex-wrap">
        <input
          v-model="charStore.searchQuery"
          type="text"
          placeholder="搜索..."
          class="px-2 py-[5px] rounded-md bg-black/30 border border-[var(--color-line)] text-sm text-[#e8edf2] max-w-[140px] outline-none focus:border-[#d4b163]"
        />
        <select
          v-model="charStore.sortMode"
          class="px-2 py-[5px] rounded-md bg-black/30 border border-[var(--color-line)] text-sm text-[#e8edf2] outline-none focus:border-[#d4b163]"
        >
          <option value="score">评分</option>
          <option value="level">等级</option>
          <option value="element">属性</option>
        </select>
      </div>
    </div>
    <div class="overflow-y-auto flex-1 min-h-0 px-1 pt-1">
      <RoleGrid :characters="charStore.filteredChars" />
    </div>
  </div>
</template>
