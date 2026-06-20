<script setup lang="ts">
import { computed } from 'vue'
import { useCharacterStore } from '@/stores/character'
import { getResourceUrl } from '@/composables/useResources'

const charStore = useCharacterStore()

const acct = computed(() => charStore.accountInfo)

const avatarSrc = computed(() => {
  if (!charStore.allChars.length) return ''
  const fs = charStore.allChars.find(
    (r) => (r.starLevel || r.role?.starLevel || 0) >= 5
  )
  if (fs) {
    const cid = String(fs.roleId || fs.role?.roleId || '')
    return getResourceUrl('waves_avatar', 'role_head_' + cid + '.png')
  }
  return ''
})

const isFull = computed(() => typeof acct.value?.creatTime === 'number')
</script>

<template>
  <div v-if="acct" class="user-card page-sidebar-user-card">
    <div class="deco-text" style="position:absolute;top:10px;right:14px;font-family:Oswald;font-size:11px;letter-spacing:4px;color:rgba(255,255,255,0.1);font-weight:bold;pointer-events:none;">
      ROVER CARD
    </div>
    <div class="avatar-container" style="width:80px;height:80px;margin-right:0;margin-bottom:12px;">
      <div class="avatar-ring"></div>
      <img
        :src="avatarSrc"
        alt="Avatar"
        class="relative z-[1] h-full w-full rounded-full object-cover"
        @error="($event.target as HTMLImageElement).style.display='none'"
        @load="($event.target as HTMLImageElement).style.display='block'"
      />
    </div>
    <div class="flex flex-col items-center z-[2]">
      <div class="flex flex-col items-center border-b border-white/8 pb-2 mb-1.5 w-full">
        <div class="text-[26px] font-extrabold text-white" style="text-shadow:0 4px 10px rgba(0,0,0,0.5);">
          {{ (acct.name || '漂泊者').substring(0, 10) }}
        </div>
        <div class="font-['JetBrains_Mono'] text-[15px] text-[#d4b163] bg-black/40 px-3 py-1 rounded-md border border-[#d4b163]/20 tracking-[1.5px] font-bold mt-1"
             style="box-shadow:0 2px 8px rgba(0,0,0,0.3);">
          UID {{ acct.id || '--' }}
        </div>
      </div>
      <div class="flex justify-center gap-6">
        <div class="flex flex-col items-center">
          <div class="font-[Oswald] text-2xl font-bold text-gold-gradient leading-tight">
            {{ isFull ? (acct.level ?? '--') : '--' }}
          </div>
          <div class="text-xs font-bold uppercase tracking-[1px] mt-0.5 text-[#6d717a]">联觉等级</div>
        </div>
        <div class="flex flex-col items-center">
          <div class="font-[Oswald] text-2xl font-bold text-gold-gradient leading-tight">
            {{ isFull ? (acct.worldLevel ?? '--') : '--' }}
          </div>
          <div class="text-xs font-bold uppercase tracking-[1px] mt-0.5 text-[#6d717a]">索拉等级</div>
        </div>
      </div>
    </div>
  </div>
</template>
