<script setup lang="ts">
import type { FetterDetail } from '@/types/character'

defineProps<{
  fetterDetail: FetterDetail
}>()
</script>

<template>
  <span class="sonata-tag">
    {{ fetterDetail.name }}
    <span class="sonata-tooltip">
      <b>2件套:</b> {{ fetterDetail.firstDescription || '—' }}<br />
      <b>5件套:</b> {{ fetterDetail.secondDescription || '—' }}
      <template v-if="fetterDetail.tripleDescription">
        <br /><b>—:</b> {{ fetterDetail.tripleDescription }}
      </template>
    </span>
  </span>
</template>
