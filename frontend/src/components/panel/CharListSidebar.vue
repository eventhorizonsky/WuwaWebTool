<script setup lang="ts">
import type { CharacterEntry } from '@/types/character'
import CharListItem from './CharListItem.vue'

defineProps<{
  characters: CharacterEntry[]
  currentCharId: string
}>()

const emit = defineEmits<{
  switch: [charId: string]
}>()
</script>

<template>
  <div v-if="characters.length === 0" class="char-list-col justify-center items-center">
    <div class="text-sm text-[#9aa0aa] text-center py-5">暂无角色</div>
  </div>
  <div v-else class="char-list-col">
    <CharListItem
      v-for="r in characters"
      :key="String(r.roleId || r.role?.roleId || '')"
      :character="r"
      :is-active="String(r.roleId || r.role?.roleId || '') === currentCharId"
      @click="emit('switch', String(r.roleId || r.role?.roleId || ''))"
    />
  </div>
</template>
