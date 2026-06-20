<script setup lang="ts">
import type { CharacterDetail } from '@/types/character'
import WeaponCard from './WeaponCard.vue'
import SkillsCard from './SkillsCard.vue'
import StatsCard from './StatsCard.vue'

defineProps<{
  roleDetail: CharacterDetail
}>()
</script>

<template>
  <div class="panel-bottom-row">
    <WeaponCard :weapon-data="roleDetail.weaponData || null" />
    <SkillsCard
      :skill-list="roleDetail.skillList || []"
      :skill-branch-list="roleDetail.skillBranchList || []"
      :active-branch-id="roleDetail.activeBranchId || 0"
    />
    <StatsCard
      :attribute-list="roleDetail.roleAttributeList || roleDetail.role?.attributeList || []"
      :bonus-props="roleDetail.equipPhantomAddPropList || []"
    />
  </div>
</template>
