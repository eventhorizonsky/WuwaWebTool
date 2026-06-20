<script setup lang="ts">
defineProps<{
  label: string
  value: string | number
  highlight?: boolean
}>()
</script>

<template>
  <div :class="['info-item', { highlight }]">
    <div
      class="info-key relative z-[1] font-bold tracking-[1px] leading-none"
      :class="highlight ? 'text-[rgba(212,177,99,0.78)]' : 'text-[#9aa0aa]'"
    >
      {{ label }}
    </div>
    <div
      class="info-value relative z-[1] font-[Oswald] font-bold leading-none"
      :class="highlight ? 'text-gold-gradient' : 'text-white'"
    >
      {{ value }}
    </div>
  </div>
</template>
