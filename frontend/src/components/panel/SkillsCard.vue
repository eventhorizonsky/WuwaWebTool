<script setup lang="ts">
import { computed } from 'vue'
import type { SkillItem, SkillBranch } from '@/types/character'
import { SKILL_ORDER } from '@/constants'

const props = defineProps<{
  skillList: SkillItem[]
  skillBranchList: SkillBranch[]
  activeBranchId: number
}>()

const sortedSkills = computed(() => {
  return [...props.skillList].sort(
    (a, b) =>
      SKILL_ORDER.indexOf(a.skill?.type || '') -
      SKILL_ORDER.indexOf(b.skill?.type || '')
  )
})

const activeBranch = computed(() => {
  return (
    props.skillBranchList.find((b) => b.branchId === props.activeBranchId) ||
    props.skillBranchList[0]
  )
})

const inactiveBranch = computed(() => {
  return props.skillBranchList.find((b) => b.branchId !== props.activeBranchId)
})

function toggleSkill(event: Event) {
  const el = (event.currentTarget as HTMLElement)
  el.classList.toggle('expanded')
}
</script>

<template>
  <div class="info-card flex-1 min-w-0 bg-[var(--color-ink-1)] border border-[var(--color-line)] rounded-[var(--radius-card)] p-3 overflow-y-auto">
    <div class="ic-title text-sm font-bold text-[#d4b163] uppercase tracking-[0.5px] pb-[5px] mb-1.5 border-b border-[var(--color-line)] flex items-center gap-1.5 flex-shrink-0">
      技能
      <div class="flex-1 h-px" style="background: linear-gradient(90deg, var(--color-line), transparent);"></div>
    </div>

    <div v-if="!skillList.length" class="text-sm text-[#9aa0aa] text-center py-5">
      暂无技能
    </div>

    <div v-else class="skills-list">
      <div
        v-for="(s, i) in sortedSkills"
        :key="i"
        class="skill-item"
        @click="toggleSkill"
      >
        <img
          :src="s.skill?.iconUrl || ''"
          alt=""
          class="w-6 h-6 rounded-md bg-black/30 flex-shrink-0"
          @error="(e) => (e.target as HTMLElement).style.display = 'none'"
        />
        <span class="flex-1 text-sm text-[#9aa0aa] truncate">
          {{ s.skill?.type || '?' }}{{ s.skill?.name ? ' - ' + s.skill.name : '' }}
        </span>
        <span class="font-bold text-sm flex-shrink-0 text-[#e8edf2]">Lv.{{ s.level || 1 }}</span>
        <span class="skill-arrow">▼</span>
        <div
          v-if="s.skill?.description"
          class="skill-desc"
          v-html="s.skill.description.replace(/\n\n/g, '<br><br>').replace(/\n/g, '<br>')"
        ></div>
      </div>
    </div>

    <!-- Branch badge -->
    <div v-if="activeBranch" class="branch-badge">
      <img
        :src="activeBranch.skillIcon || ''"
        alt=""
        class="w-[18px] h-[18px] rounded-sm"
        @error="(e) => (e.target as HTMLElement).style.display = 'none'"
      />
      {{ activeBranch.branchName }}
      <span
        v-if="inactiveBranch"
        class="text-[#9aa0aa] ml-0.5"
      >({{ inactiveBranch.branchName }}未激活)</span>
    </div>
  </div>
</template>
