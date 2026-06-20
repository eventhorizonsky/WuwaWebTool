<script setup lang="ts">
import type { CharacterEntry } from '@/types/character'
import RoleCard from './RoleCard.vue'

defineProps<{
  characters: CharacterEntry[]
}>()
</script>

<template>
  <div v-if="characters.length === 0" class="text-center py-15 px-5 text-lg text-[#9aa0aa] col-span-full">
    无匹配角色
  </div>
  <div
    v-else
    class="role-grid grid gap-3.5"
  >
    <RoleCard
      v-for="r in characters"
      :key="String(r.roleId || r.role?.roleId || '')"
      :character="r"
    />
  </div>
</template>
