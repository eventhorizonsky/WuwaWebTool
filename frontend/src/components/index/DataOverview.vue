<script setup lang="ts">
import { computed } from 'vue'
import { useCharacterStore } from '@/stores/character'
import { STANDARD_BANNER_NAMES } from '@/constants'
import InfoItem from '@/components/shared/InfoItem.vue'

const charStore = useCharacterStore()

const acct = computed(() => charStore.accountInfo)

const isFull = computed(() => typeof acct.value?.creatTime === 'number')

const upCount = computed(() => {
  let c = 0
  for (const r of charStore.allChars) {
    const ri = r.role || r
    if (ri.starLevel === 5 && !STANDARD_BANNER_NAMES.includes(ri.roleName || '')) c++
  }
  return c
})

const calabashLevel = computed(() => {
  return charStore.calabashData?.isUnlock ? charStore.calabashData.level : 0
})

interface OverviewItem {
  key: string
  value: string | number
  highlight: boolean
}

const items = computed<OverviewItem[]>(() => {
  if (!acct.value) return []
  const list: OverviewItem[] = [
    { key: '活跃天数', value: acct.value.activeDays ?? '--', highlight: true },
    { key: '解锁角色', value: acct.value.roleNum ?? '--', highlight: false },
    { key: 'UP角色', value: upCount.value, highlight: true },
    { key: '数据坞等级', value: calabashLevel.value, highlight: false },
    { key: '已达成成就', value: acct.value.achievementCount ?? '--', highlight: true },
    { key: '成就星数', value: acct.value.achievementStar ?? '--', highlight: false },
    { key: '小型信标', value: acct.value.smallCount ?? '--', highlight: false },
    { key: '中型信标', value: acct.value.bigCount ?? '--', highlight: true },
  ]
  if (acct.value.treasureBoxList?.length) {
    acct.value.treasureBoxList.forEach((b, i) => {
      if (b?.name) list.push({ key: b.name, value: b.num ?? '--', highlight: i % 2 === 0 })
    })
  }
  return list
})
</script>

<template>
  <div v-if="isFull" class="section-container page-sidebar-section">
    <div class="section-header">
      <span class="section-title">数据概览</span>
      <div class="section-deco-line"></div>
    </div>
    <div class="base-info-grid">
      <InfoItem
        v-for="it in items"
        :key="it.key"
        :label="it.key"
        :value="it.value"
        :highlight="it.highlight"
      />
    </div>
  </div>
</template>
